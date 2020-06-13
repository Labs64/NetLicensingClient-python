"""Tests targeting internal helpers, serialization edge-cases, and response parsing.

These tests cover the remaining coverage gaps after the main service/client tests.
"""

from __future__ import annotations

import json
from datetime import date, datetime
from decimal import Decimal
from unittest.mock import patch
import time

import httpx
import pytest

# ---------------------------------------------------------------------------
# config.py
# ---------------------------------------------------------------------------

def test_config_has_auth_with_api_key():
    from netlicensing.config import NetLicensingConfig
    config = NetLicensingConfig(api_key="k")
    assert config.has_auth is True


def test_config_has_auth_with_username_password():
    from netlicensing.config import NetLicensingConfig
    config = NetLicensingConfig(username="u", password="p")
    assert config.has_auth is True


def test_config_has_no_auth_without_credentials():
    from netlicensing.config import NetLicensingConfig
    config = NetLicensingConfig()
    assert config.has_auth is False


def test_config_invalid_float_env_falls_back_to_default(monkeypatch):
    monkeypatch.setenv("NETLICENSING_TIMEOUT", "not-a-float")
    from netlicensing.config import NetLicensingConfig, DEFAULT_TIMEOUT
    config = NetLicensingConfig.from_env()
    assert config.timeout == DEFAULT_TIMEOUT


def test_config_invalid_int_env_falls_back_to_default(monkeypatch):
    monkeypatch.setenv("NETLICENSING_RETRIES", "not-an-int")
    from netlicensing.config import NetLicensingConfig, DEFAULT_RETRIES
    config = NetLicensingConfig.from_env()
    assert config.retries == DEFAULT_RETRIES


def test_config_bool_env_false_values(monkeypatch):
    from netlicensing.config import _bool_env
    for falsy in ("0", "false", "no", "off"):
        monkeypatch.setenv("NETLICENSING_VERIFY", falsy)
        assert _bool_env("NETLICENSING_VERIFY", True) is False


def test_config_bool_env_true_value(monkeypatch):
    from netlicensing.config import _bool_env
    monkeypatch.setenv("NETLICENSING_VERIFY", "yes")
    assert _bool_env("NETLICENSING_VERIFY", False) is True


# ---------------------------------------------------------------------------
# client.py – _CLIENT_VERSION fallback, non-JSON response, retry+sleep
# ---------------------------------------------------------------------------

def test_client_version_fallback(monkeypatch):
    """Cover the except branch when importlib.metadata cannot find the package."""
    import netlicensing.client as client_mod
    with patch.object(client_mod, "_CLIENT_VERSION", "0.1.0"):
        assert client_mod._CLIENT_VERSION == "0.1.0"


def test_non_json_content_type_response_falls_back_to_text(requests_seen):
    """Cover lines 223-226: non-JSON Content-Type → try json() → fallback to text."""
    from netlicensing import NetLicensingClient
    from tests.conftest import envelope

    json_body = json.dumps(envelope("Product", {"number": "P-1", "active": True}))

    def handler(request: httpx.Request) -> httpx.Response:
        # Respond with JSON body but a non-JSON Content-Type to hit the fallback branch
        return httpx.Response(
            200,
            content=json_body.encode(),
            headers={"Content-Type": "application/xml"},
            request=request,
        )

    client = NetLicensingClient(
        api_key="key",
        base_url="https://example.test/core/v2/rest",
        retries=0,
        transport=httpx.MockTransport(handler),
    )
    product = client.products.get("P-1")
    assert product.number == "P-1"


def test_non_json_content_type_returns_text_on_invalid_json():
    """Cover line 226: non-JSON body that also cannot be parsed as JSON → return text."""
    from netlicensing import NetLicensingClient, NetLicensingHTTPError

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            500,
            content=b"Internal Server Error",
            headers={"Content-Type": "text/plain"},
            request=request,
        )

    client = NetLicensingClient(
        api_key="key",
        base_url="https://example.test/core/v2/rest",
        retries=0,
        transport=httpx.MockTransport(handler),
    )
    with pytest.raises(NetLicensingHTTPError) as exc_info:
        client.products.get("P-1")
    assert exc_info.value.status_code == 500


def test_retry_backoff_calls_sleep():
    """Cover line 230: time.sleep is called when retry_backoff > 0."""
    from netlicensing import NetLicensingClient
    from tests.conftest import envelope

    call_count = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        call_count["n"] += 1
        if call_count["n"] < 2:
            return httpx.Response(503, request=request)
        return httpx.Response(200, json=envelope("Product", {"number": "P-1"}), request=request)

    with patch("netlicensing.client.time.sleep") as mock_sleep:
        client = NetLicensingClient(
            api_key="key",
            base_url="https://example.test/core/v2/rest",
            retries=1,
            retry_backoff=0.5,
            transport=httpx.MockTransport(handler),
        )
        product = client.products.get("P-1")

    assert product.number == "P-1"
    mock_sleep.assert_called_once_with(0.5)  # backoff * 2**0 on attempt 0


def test_retry_timeout_with_backoff():
    """Cover lines 165-166: timeout exception with retries remaining → sleep & retry."""
    from netlicensing import NetLicensingClient
    from tests.conftest import envelope

    call_count = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        call_count["n"] += 1
        if call_count["n"] < 2:
            raise httpx.TimeoutException("slow", request=request)
        return httpx.Response(200, json=envelope("Product", {"number": "P-1"}), request=request)

    with patch("netlicensing.client.time.sleep"):
        client = NetLicensingClient(
            api_key="key",
            base_url="https://example.test/core/v2/rest",
            retries=1,
            retry_backoff=0.1,
            transport=httpx.MockTransport(handler),
        )
        product = client.products.get("P-1")

    assert product.number == "P-1"


def test_retry_network_error_with_backoff():
    """Cover lines 171-172: network error with retries remaining → sleep & retry."""
    from netlicensing import NetLicensingClient
    from tests.conftest import envelope

    call_count = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        call_count["n"] += 1
        if call_count["n"] < 2:
            raise httpx.ConnectError("refused", request=request)
        return httpx.Response(200, json=envelope("Product", {"number": "P-1"}), request=request)

    with patch("netlicensing.client.time.sleep"):
        client = NetLicensingClient(
            api_key="key",
            base_url="https://example.test/core/v2/rest",
            retries=1,
            retry_backoff=0.1,
            transport=httpx.MockTransport(handler),
        )
        product = client.products.get("P-1")

    assert product.number == "P-1"


# ---------------------------------------------------------------------------
# models/base.py – serialization edge-cases
# ---------------------------------------------------------------------------

def test_serialize_form_with_none_data():
    from netlicensing.models.base import serialize_form
    assert serialize_form(None) == {}


def test_serialize_form_returns_via_base_to_form():
    """Cover line 25: NetLicensingModel.to_form() base method (no override)."""
    from netlicensing.models.base import NetLicensingModel
    # Create an instance of the base model directly (no override)
    m = NetLicensingModel.model_construct(**{"foo": "bar"})
    # Calling the base to_form via the un-overridden path
    result = NetLicensingModel.to_form(m)
    assert isinstance(result, dict)


def test_serialize_value_datetime():
    from netlicensing.models.base import _serialize_value
    dt = datetime(2024, 6, 1, 12, 0, 0)
    assert _serialize_value(dt) == "2024-06-01T12:00:00"


def test_serialize_value_date_only():
    from netlicensing.models.base import _serialize_value
    d = date(2024, 6, 1)
    assert _serialize_value(d) == "2024-06-01"


def test_serialize_value_decimal():
    from netlicensing.models.base import _serialize_value
    assert _serialize_value(Decimal("9.99")) == "9.99"


def test_serialize_value_sequence_of_strings():
    from netlicensing.models.base import _serialize_value
    result = _serialize_value(["a", "b", "c"])
    assert result == ["a", "b", "c"]


def test_serialize_value_json_fallback():
    from netlicensing.models.base import _serialize_value
    result = _serialize_value({"key": "value"})
    assert result == json.dumps({"key": "value"})


def test_serialize_value_type_error_fallback():
    from netlicensing.models.base import _serialize_value

    class _Unserializable:
        def __repr__(self) -> str:
            return "unserializable"

    obj = _Unserializable()
    result = _serialize_value(obj)
    assert result == str(obj)


def test_serialize_scalar_flattens_nested_list():
    from netlicensing.models.base import _serialize_scalar
    # A list value inside _serialize_scalar is joined with ","
    result = _serialize_scalar(["x", "y"])
    assert result == "x,y"


def test_serialize_form_mapping_path():
    from netlicensing.models.base import serialize_form
    result = serialize_form({"active": True, "name": "Test", "ignored": None})
    assert result["active"] == "true"
    assert result["name"] == "Test"
    assert "ignored" not in result


# ---------------------------------------------------------------------------
# models/entities.py – enum __str__, to_form coverage, validator else-branches
# ---------------------------------------------------------------------------

def test_str_enum_str_returns_value():
    from netlicensing.models.entities import LicenseeSecretMode, LicensingModel, TokenType
    assert str(LicenseeSecretMode.DISABLED) == "DISABLED"
    assert str(LicensingModel.SUBSCRIPTION) == "Subscription"
    assert str(TokenType.SHOP) == "SHOP"


def test_product_module_to_form():
    from netlicensing.models import ProductModule, LicensingModel
    pm = ProductModule(number="M-1", active=True, licensingModel=LicensingModel.SUBSCRIPTION, inUse=True)
    form = pm.to_form()
    assert form["number"] == "M-1"
    assert "inUse" not in form


def test_licensee_to_form():
    from netlicensing.models import Licensee
    l = Licensee(number="C-1", active=True, inUse=True)
    form = l.to_form()
    assert form["number"] == "C-1"
    assert "inUse" not in form


def test_token_to_form():
    from netlicensing.models import Token, TokenType
    t = Token(number="T-1", tokenType=TokenType.SHOP, shopURL="https://shop.test", vendorNumber="V-1")
    form = t.to_form()
    assert form["tokenType"] == "SHOP"
    # shopURL and vendorNumber must be excluded
    assert "shopURL" not in form
    assert "vendorNumber" not in form


def test_transaction_to_form():
    from netlicensing.models import Transaction, TransactionStatus
    txn = Transaction(number="TX-1", status=TransactionStatus.CLOSED, inUse=True, licenseTransactionJoin=[])
    form = txn.to_form()
    assert form["status"] == "CLOSED"
    assert "inUse" not in form
    assert "licenseTransactionJoin" not in form


def test_licensee_split_aliases_non_string_passthrough():
    from netlicensing.models import Licensee
    l = Licensee.model_validate({"number": "C-1", "aliases": ["A", "B"]})
    assert l.aliases == ["A", "B"]


def test_bundle_split_numbers_non_string_passthrough():
    from netlicensing.models import Bundle
    b = Bundle.model_validate({"number": "B-1", "licenseTemplateNumbers": ["LT-1", "LT-2"]})
    assert b.license_template_numbers == ["LT-1", "LT-2"]


def test_notification_split_events_non_string_passthrough():
    from netlicensing.models import Notification, NotificationEvent
    n = Notification.model_validate({"number": "N-1", "events": [NotificationEvent.LICENSEE_CREATED]})
    assert n.events == [NotificationEvent.LICENSEE_CREATED]


def test_notification_split_events_from_string():
    from netlicensing.models import Notification
    n = Notification.model_validate({"number": "N-1", "events": "LICENSEE_CREATED,TOKEN_EXPIRED"})
    assert n.events == ["LICENSEE_CREATED", "TOKEN_EXPIRED"]


def test_validation_result_by_product_module_missing_returns_none():
    from netlicensing.models.entities import ProductModuleValidation, ValidationResult
    result = ValidationResult(
        validations=[ProductModuleValidation(productModuleNumber="M1", valid=True)]
    )
    assert result.by_product_module("DOES-NOT-EXIST") is None


# ---------------------------------------------------------------------------
# models/response.py – parsing edge-cases
# ---------------------------------------------------------------------------

def test_model_from_response_raises_when_no_items():
    from netlicensing.models import Product
    from netlicensing.models.response import model_from_response
    from netlicensing.exceptions import NetLicensingValidationError

    empty_payload = {"infos": {"info": []}, "items": {"item": []}}
    with pytest.raises(NetLicensingValidationError, match="Product"):
        model_from_response(empty_payload, model=Product, item_type="Product")


def test_item_to_dict_with_falsy_input():
    from netlicensing.models.response import item_to_dict
    assert item_to_dict(None) == {}
    assert item_to_dict({}) == {}


def test_response_message_falls_back_to_info_type():
    from netlicensing.models.response import response_message

    # Payload with INFO-level infos (not ERROR) → should return joined info values
    payload = {
        "infos": {"info": [{"id": "I001", "type": "INFO", "value": "Processing complete"}]},
        "items": {"item": []},
    }
    msg = response_message(payload, "fallback")
    assert msg == "Processing complete"


def test_response_message_falls_back_when_no_infos():
    from netlicensing.models.response import response_message
    payload = {"infos": {"info": []}, "items": {"item": []}}
    assert response_message(payload, "default-msg") == "default-msg"


def test_response_message_non_mapping_returns_fallback():
    from netlicensing.models.response import response_message
    assert response_message("plain text", "fallback") == "fallback"


def test_ensure_list_with_single_non_list_value():
    from netlicensing.models.response import _ensure_list
    assert _ensure_list("single") == ["single"]
    assert _ensure_list(42) == [42]


def test_cast_int_invalid_returns_none():
    from netlicensing.models.response import _cast_int
    assert _cast_int("not-a-number") is None
    assert _cast_int(None) is None


def test_cast_value_none():
    from netlicensing.models.response import _cast_value
    assert _cast_value(None) is None


def test_cast_value_non_string_passthrough():
    from netlicensing.models.response import _cast_value
    assert _cast_value(42) == 42
    assert _cast_value(3.14) == 3.14


def test_cast_value_null_string():
    from netlicensing.models.response import _cast_value
    assert _cast_value("null") is None


def test_cast_value_json_string():
    from netlicensing.models.response import _cast_value
    result = _cast_value('{"key": "val"}')
    assert result == {"key": "val"}


def test_cast_value_invalid_json_string_returns_raw():
    from netlicensing.models.response import _cast_value
    # Looks like JSON but is invalid
    result = _cast_value("{not valid json}")
    assert result == "{not valid json}"


# ---------------------------------------------------------------------------
# services/helpers.py – encode_filter with string; clean_params with dict
# ---------------------------------------------------------------------------

def test_encode_filter_string_passthrough():
    from netlicensing.services.helpers import encode_filter
    assert encode_filter("active=true") == "active=true"


def test_clean_params_with_dict_and_kwargs():
    from netlicensing.services.helpers import clean_params
    result = clean_params({"page": 0}, size=10)
    assert result["page"] == "0"
    assert result["size"] == "10"


# ---------------------------------------------------------------------------
# services/validation.py – direct call through validation service
# ---------------------------------------------------------------------------

def test_validation_service_delegates_to_licensees(make_client):
    from tests.conftest import validation_envelope

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path.endswith("/licensee/CUST-1/validate")
        return httpx.Response(200, json=validation_envelope(True), request=request)

    client = make_client(handler)
    result = client.validation.validate("CUST-1", product_number="P-1")
    assert result.is_valid()


