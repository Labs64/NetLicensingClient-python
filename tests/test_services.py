from __future__ import annotations

import pytest
import httpx

from tests.conftest import envelope, form_body, page_envelope, validation_envelope
from netlicensing import LicenseType, TokenType, ApiKeyRole


def test_product_service_get_list_create_update_delete(make_client, requests_seen):
    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if request.method == "GET" and path.endswith("/product/P-1"):
            return httpx.Response(200, json=envelope("Product", {"number": "P-1", "active": True, "name": "One"}), request=request)
        if request.method == "GET" and path.endswith("/product"):
            return httpx.Response(
                200,
                json=page_envelope("Product", [{"number": "P-1", "active": True}, {"number": "P-2", "active": False}]),
                request=request,
            )
        if request.method == "POST" and path.endswith("/product"):
            body = form_body(request)
            return httpx.Response(200, json=envelope("Product", {"number": body["number"], "active": body["active"]}), request=request)
        if request.method == "POST" and path.endswith("/product/P-1"):
            body = form_body(request)
            return httpx.Response(200, json=envelope("Product", {"number": "P-1", "name": body["name"], "active": True}), request=request)
        if request.method == "DELETE":
            return httpx.Response(204, request=request)
        raise AssertionError(f"unexpected request {request.method} {request.url}")

    client = make_client(handler)

    assert client.products.get("P-1").name == "One"
    products = client.products.list({"active": True})
    assert len(products) == 2
    assert requests_seen[1].url.params["filter"] == "active=True"
    assert client.products.create(number="P-3", active=True).number == "P-3"
    assert form_body(requests_seen[2]) == {"number": "P-3", "active": "true"}
    assert client.products.update("P-1", name="Updated").name == "Updated"
    assert client.products.delete("P-1") is True


def test_licensee_validation_builds_form_and_parses_result(make_client, requests_seen):
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path.endswith("/licensee/CUST-1/validate")
        assert form_body(request) == {
            "productNumber": "P-1",
            "productModuleNumber0": "MOD-1",
            "nodeSecret0": "machine",
            "dryRun": "true",
        }
        return httpx.Response(200, json=validation_envelope(True), request=request)

    client = make_client(handler)

    result = client.licensees.validate(
        "CUST-1",
        product_number="P-1",
        dry_run=True,
        product_module_parameters={"MOD-1": {"nodeSecret": "machine"}},
    )

    assert result.ttl == 1440
    assert result.is_valid()
    assert result.by_product_module("MOD-1") is not None


def test_token_service_create_shop_token(make_client, requests_seen):
    def handler(request: httpx.Request) -> httpx.Response:
        assert form_body(request) == {
            "tokenType": "SHOP",
            "licenseeNumber": "CUST-1",
            "productNumber": "P-1",
            "successURL": "https://vendor.test/success",
        }
        return httpx.Response(
            200,
            json=envelope(
                "Token",
                {
                    "number": "T-1",
                    "active": True,
                    "tokenType": "SHOP",
                    "licenseeNumber": "CUST-1",
                    "shopURL": "https://go.netlicensing.io/shop/T-1",
                },
            ),
            request=request,
        )

    client = make_client(handler)

    token = client.tokens.create_shop_token(
        "CUST-1",
        product_number="P-1",
        success_url="https://vendor.test/success",
    )

    assert token.token_type == TokenType.SHOP
    assert token.shop_url == "https://go.netlicensing.io/shop/T-1"


def test_license_template_create_uses_enum_value(make_client, requests_seen):
    def handler(request: httpx.Request) -> httpx.Response:
        body = form_body(request)
        assert body["licenseType"] == "FEATURE"
        return httpx.Response(
            200,
            json=envelope(
                "LicenseTemplate",
                {"number": "LT-1", "active": True, "name": "Feature", "licenseType": "FEATURE"},
            ),
            request=request,
        )

    client = make_client(handler)

    template = client.license_templates.create(
        product_module_number="MOD-1",
        number="LT-1",
        name="Feature",
        license_type=LicenseType.FEATURE,
    )

    assert template.license_type == LicenseType.FEATURE


def test_bundle_obtain_returns_created_licenses(make_client):
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path.endswith("/bundle/B-1/obtain")
        return httpx.Response(
            200,
            json=page_envelope("License", [{"number": "L-1", "active": True}, {"number": "L-2", "active": True}]),
            request=request,
        )

    client = make_client(handler)

    licenses = client.bundles.obtain("B-1", "CUST-1")

    assert [license.number for license in licenses] == ["L-1", "L-2"]


# ---------------------------------------------------------------------------
# Licensee service – create / update / transfer
# ---------------------------------------------------------------------------

def test_licensee_service_create_and_update(make_client, requests_seen):
    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        body = form_body(request)
        if request.method == "POST" and path.endswith("/licensee"):
            return httpx.Response(200, json=envelope("Licensee", {"number": body["number"], "active": body["active"], "productNumber": body["productNumber"]}), request=request)
        if request.method == "POST" and path.endswith("/licensee/CUST-1"):
            return httpx.Response(200, json=envelope("Licensee", {"number": "CUST-1", "name": body["name"]}), request=request)
        raise AssertionError(f"unexpected {request.method} {request.url}")

    client = make_client(handler)

    licensee = client.licensees.create(product_number="P-1", number="CUST-1", active=True)
    assert licensee.number == "CUST-1"
    assert licensee.product_number == "P-1"

    updated = client.licensees.update("CUST-1", name="Alice")
    assert updated.name == "Alice"


def test_licensee_transfer(make_client, requests_seen):
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path.endswith("/licensee/CUST-2/transfer")
        assert form_body(request) == {"sourceLicenseeNumber": "CUST-1"}
        return httpx.Response(200, json={"infos": {"info": []}, "items": {"item": []}}, request=request)

    client = make_client(handler)
    assert client.licensees.transfer("CUST-2", "CUST-1") is True


# ---------------------------------------------------------------------------
# License service – create / update / delete
# ---------------------------------------------------------------------------

def test_license_service_create_and_update(make_client, requests_seen):
    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        body = form_body(request)
        if request.method == "POST" and path.endswith("/license"):
            return httpx.Response(200, json=envelope("License", {"number": body["number"], "licenseeNumber": body["licenseeNumber"], "licenseTemplateNumber": body["licenseTemplateNumber"]}), request=request)
        if request.method == "POST" and path.endswith("/license/L-1"):
            return httpx.Response(200, json=envelope("License", {"number": "L-1", "name": body.get("name", "")}), request=request)
        if request.method == "DELETE":
            return httpx.Response(204, request=request)
        raise AssertionError(f"unexpected {request.method} {request.url}")

    client = make_client(handler)

    lic = client.licenses.create(licensee_number="CUST-1", license_template_number="LT-1", number="L-1")
    assert lic.number == "L-1"
    assert lic.licensee_number == "CUST-1"

    updated = client.licenses.update("L-1", name="My License")
    assert updated.name == "My License"

    assert client.licenses.delete("L-1") is True


# ---------------------------------------------------------------------------
# License template service – update / delete
# ---------------------------------------------------------------------------

def test_license_template_update_and_delete(make_client):
    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        body = form_body(request)
        if request.method == "POST" and path.endswith("/licensetemplate/LT-1"):
            return httpx.Response(200, json=envelope("LicenseTemplate", {"number": "LT-1", "name": body.get("name", ""), "active": "true"}), request=request)
        if request.method == "DELETE":
            return httpx.Response(204, request=request)
        raise AssertionError(f"unexpected {request.method} {request.url}")

    client = make_client(handler)
    tmpl = client.license_templates.update("LT-1", name="Renamed")
    assert tmpl.name == "Renamed"
    assert client.license_templates.delete("LT-1") is True


# ---------------------------------------------------------------------------
# Product module service – create / update / delete
# ---------------------------------------------------------------------------

def test_product_module_service_create_update_delete(make_client):
    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        body = form_body(request)
        if request.method == "POST" and path.endswith("/productmodule"):
            return httpx.Response(200, json=envelope("ProductModule", {"number": body["number"], "productNumber": body["productNumber"], "licensingModel": body["licensingModel"]}), request=request)
        if request.method == "POST" and path.endswith("/productmodule/MOD-1"):
            return httpx.Response(200, json=envelope("ProductModule", {"number": "MOD-1", "name": body.get("name", "")}), request=request)
        if request.method == "DELETE":
            return httpx.Response(204, request=request)
        raise AssertionError(f"unexpected {request.method} {request.url}")

    client = make_client(handler)

    from netlicensing import LicensingModel
    mod = client.product_modules.create(product_number="P-1", number="MOD-1", name="Module", licensing_model=LicensingModel.SUBSCRIPTION)
    assert mod.number == "MOD-1"
    assert mod.product_number == "P-1"

    updated = client.product_modules.update("MOD-1", name="Updated Module")
    assert updated.name == "Updated Module"

    assert client.product_modules.delete("MOD-1") is True


# ---------------------------------------------------------------------------
# Token service – API key token / list / delete
# ---------------------------------------------------------------------------

def test_token_create_api_key_token(make_client, requests_seen):
    def handler(request: httpx.Request) -> httpx.Response:
        body = form_body(request)
        assert body["tokenType"] == "APIKEY"
        assert body["apiKeyRole"] == "ROLE_APIKEY_LICENSEE"
        assert body["licenseeNumber"] == "CUST-1"
        return httpx.Response(200, json=envelope("Token", {"number": "AK-1", "tokenType": "APIKEY", "apiKeyRole": "ROLE_APIKEY_LICENSEE"}), request=request)

    client = make_client(handler)
    token = client.tokens.create_api_key_token(api_key_role=ApiKeyRole.LICENSEE, licensee_number="CUST-1")
    assert token.number == "AK-1"
    assert token.api_key_role == ApiKeyRole.LICENSEE


def test_token_list_and_delete(make_client, requests_seen):
    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        if request.method == "GET" and path.endswith("/token"):
            return httpx.Response(200, json=page_envelope("Token", [{"number": "T-1", "tokenType": "SHOP"}]), request=request)
        if request.method == "DELETE":
            return httpx.Response(204, request=request)
        raise AssertionError(f"unexpected {request.method} {request.url}")

    client = make_client(handler)
    tokens = client.tokens.list()
    assert len(tokens) == 1
    assert tokens.items[0].number == "T-1"
    assert client.tokens.delete("T-1") is True


# ---------------------------------------------------------------------------
# Transaction service – create / update / delete raises
# ---------------------------------------------------------------------------

def test_transaction_create_and_update(make_client):
    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        body = form_body(request)
        if request.method == "POST" and path.endswith("/transaction"):
            return httpx.Response(200, json=envelope("Transaction", {"number": "TRX-1", "status": body["status"], "active": "true"}), request=request)
        if request.method == "POST" and path.endswith("/transaction/TRX-1"):
            return httpx.Response(200, json=envelope("Transaction", {"number": "TRX-1", "status": body.get("status", "CLOSED"), "active": "true"}), request=request)
        raise AssertionError(f"unexpected {request.method} {request.url}")

    client = make_client(handler)

    from netlicensing import TransactionStatus
    txn = client.transactions.create(status=TransactionStatus.PENDING)
    assert txn.number == "TRX-1"
    assert txn.status == TransactionStatus.PENDING

    updated = client.transactions.update("TRX-1", status=TransactionStatus.CLOSED)
    assert updated.status == TransactionStatus.CLOSED


def test_transaction_delete_raises():
    from netlicensing.services.transaction import TransactionService

    class _FakeClient:
        pass

    svc = TransactionService(_FakeClient())
    with pytest.raises(NotImplementedError):
        svc.delete("TRX-1")


# ---------------------------------------------------------------------------
# Payment method service – update / errors for create+delete
# ---------------------------------------------------------------------------

def test_payment_method_update(make_client):
    def handler(request: httpx.Request) -> httpx.Response:
        body = form_body(request)
        return httpx.Response(200, json=envelope("PaymentMethod", {"number": "PAYPAL", "active": body.get("active", "true")}), request=request)

    client = make_client(handler)
    pm = client.payment_methods.update("PAYPAL", active=True)
    assert pm.number == "PAYPAL"


def test_payment_method_create_and_delete_raise():
    from netlicensing.services.payment_method import PaymentMethodService

    class _FakeClient:
        pass

    svc = PaymentMethodService(_FakeClient())
    with pytest.raises(NotImplementedError):
        svc.create()
    with pytest.raises(NotImplementedError):
        svc.delete("X")


# ---------------------------------------------------------------------------
# Bundle service – create / update
# ---------------------------------------------------------------------------

def test_bundle_create_and_update(make_client):
    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        body = form_body(request)
        if request.method == "POST" and path.endswith("/bundle"):
            return httpx.Response(200, json=envelope("Bundle", {"number": body["number"], "name": body["name"], "licenseTemplateNumbers": body["licenseTemplateNumbers"]}), request=request)
        if request.method == "POST" and path.endswith("/bundle/B-1"):
            return httpx.Response(200, json=envelope("Bundle", {"number": "B-1", "name": body.get("name", ""), "active": "true"}), request=request)
        raise AssertionError(f"unexpected {request.method} {request.url}")

    client = make_client(handler)

    bundle = client.bundles.create(number="B-1", name="Bundle One", license_template_numbers=["LT-1", "LT-2"])
    assert bundle.number == "B-1"
    assert bundle.license_template_numbers == ["LT-1", "LT-2"]

    updated = client.bundles.update("B-1", name="Bundle Updated")
    assert updated.name == "Bundle Updated"


# ---------------------------------------------------------------------------
# Notification service – create / update / delete
# ---------------------------------------------------------------------------

def test_notification_service_crud(make_client):
    def handler(request: httpx.Request) -> httpx.Response:
        path = request.url.path
        body = form_body(request)
        if request.method == "POST" and path.endswith("/notification"):
            return httpx.Response(200, json=envelope("Notification", {"number": body.get("number", "N-1"), "name": body.get("name", "")}), request=request)
        if request.method == "POST" and path.endswith("/notification/N-1"):
            return httpx.Response(200, json=envelope("Notification", {"number": "N-1", "name": body.get("name", "")}), request=request)
        if request.method == "DELETE":
            return httpx.Response(204, request=request)
        raise AssertionError(f"unexpected {request.method} {request.url}")

    client = make_client(handler)

    from netlicensing import Notification, NotificationProtocol, NotificationEvent
    notification = client.notifications.create(number="N-1", name="My Hook", protocol=NotificationProtocol.WEBHOOK)
    assert notification.name == "My Hook"

    updated = client.notifications.update("N-1", name="Updated Hook")
    assert updated.name == "Updated Hook"

    assert client.notifications.delete("N-1") is True


# ---------------------------------------------------------------------------
# Utility service – list_countries / list_license_types / list_licensing_models
# ---------------------------------------------------------------------------

def test_utility_list_countries(make_client):
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path.endswith("/utility/countries")
        return httpx.Response(200, json=page_envelope("Country", [{"code": "DE", "name": "Germany", "vatPercent": "19.00", "isEu": "true"}]), request=request)

    client = make_client(handler)
    countries = client.utility.list_countries()
    assert len(countries) == 1
    country = countries.items[0]
    assert country.code == "DE"
    assert country.name == "Germany"


def test_utility_list_license_types(make_client):
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path.endswith("/utility/licenseTypes")
        return httpx.Response(
            200,
            json={
                "infos": {"info": []},
                "items": {
                    "item": [
                        {
                            "type": "LicenseType",
                            "property": [{"name": "name", "value": "FEATURE"}],
                            "list": [],
                        },
                        {
                            "type": "LicenseType",
                            "property": [{"name": "name", "value": "TIMEVOLUME"}],
                            "list": [],
                        },
                    ]
                },
            },
            request=request,
        )

    client = make_client(handler)
    types = client.utility.list_license_types()
    assert "FEATURE" in types
    assert "TIMEVOLUME" in types


def test_utility_list_licensing_models(make_client):
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path.endswith("/utility/licensingModels")
        return httpx.Response(
            200,
            json={
                "infos": {"info": []},
                "items": {
                    "item": [
                        {
                            "type": "LicensingModelProperties",
                            "property": [{"name": "name", "value": "Subscription"}],
                            "list": [],
                        },
                    ]
                },
            },
            request=request,
        )

    client = make_client(handler)
    models = client.utility.list_licensing_models()
    assert "Subscription" in models


# ---------------------------------------------------------------------------
# iterate() helper
# ---------------------------------------------------------------------------

def test_iterate_yields_all_items(make_client):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=page_envelope("Product", [{"number": "P-1"}, {"number": "P-2"}, {"number": "P-3"}]), request=request)

    client = make_client(handler)
    numbers = [p.number for p in client.products.iterate()]
    assert numbers == ["P-1", "P-2", "P-3"]
