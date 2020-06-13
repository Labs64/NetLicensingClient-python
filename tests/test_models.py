from __future__ import annotations

from decimal import Decimal

from netlicensing.models import Bundle, License, Licensee, LicenseTemplate, LicensingModel, Notification, NotificationEvent, NotificationProtocol, Product, ProductDiscount, ValidationParameters
from netlicensing.models.entities import ProductModuleValidation, ValidationResult
from netlicensing.models.pagination import Page
from netlicensing.models.response import model_from_response, validation_from_response


def test_product_model_parses_nested_discounts():
    payload = {
        "items": {
            "item": [
                {
                    "type": "Product",
                    "property": [
                        {"name": "number", "value": "P-1"},
                        {"name": "active", "value": "true"},
                    ],
                    "list": [
                        {
                            "name": "discount",
                            "property": [
                                {"name": "totalPrice", "value": "100.00"},
                                {"name": "currency", "value": "EUR"},
                                {"name": "amountPercent", "value": "10"},
                            ],
                            "list": [],
                        }
                    ],
                }
            ]
        },
        "infos": {"info": []},
    }

    product = model_from_response(payload, model=Product, item_type="Product")

    assert product.active is True
    assert product.discounts
    assert product.discounts[0].amount_percent == 10
    assert product.to_form()["discount"] == ["100.00;EUR;10%"]


def test_bundle_numbers_are_split_and_serialized():
    bundle = Bundle.model_validate({"number": "B-1", "licenseTemplateNumbers": "LT-1,LT-2"})

    assert bundle.license_template_numbers == ["LT-1", "LT-2"]
    assert bundle.to_form()["licenseTemplateNumbers"] == "LT-1,LT-2"


def test_validation_parameters_support_multiple_modules():
    params = ValidationParameters(
        product_number="P-1",
        product_module_parameters={
            "MOD-1": {"nodeSecret": "abc"},
            "MOD-2": {"sessionId": "xyz"},
        },
    )

    assert params.to_form() == {
        "productNumber": "P-1",
        "productModuleNumber0": "MOD-1",
        "nodeSecret0": "abc",
        "productModuleNumber1": "MOD-2",
        "sessionId1": "xyz",
    }


def test_product_discount_rejects_ambiguous_amounts():
    try:
        ProductDiscount(total_price="100", currency="EUR", amount_fix="5", amount_percent="10")
    except ValueError as exc:
        assert "amount_fix" in str(exc)
    else:
        raise AssertionError("expected validation error")


def test_product_discount_fix_serialization():
    d = ProductDiscount(total_price=Decimal("50"), currency="USD", amount_fix=Decimal("5"))
    assert d.as_api_value() == "50;USD;5"


def test_product_discount_empty_when_fields_missing():
    d = ProductDiscount()
    assert d.as_api_value() == ""


def test_licensee_aliases_split():
    l = Licensee.model_validate({"number": "C-1", "aliases": "A,B,C"})
    assert l.aliases == ["A", "B", "C"]


def test_notification_events_serialized_as_csv():
    n = Notification(events=[NotificationEvent.LICENSEE_CREATED, NotificationEvent.LICENSE_CREATED])
    form = n.to_form()
    assert form["events"] == "LICENSEE_CREATED,LICENSE_CREATED"


def test_page_length_and_iteration():
    page: Page[Product] = Page(items=[Product(number="P-1"), Product(number="P-2")])
    assert len(page) == 2
    assert bool(page) is True
    assert [p.number for p in page] == ["P-1", "P-2"]


def test_page_empty_is_falsy():
    page: Page[Product] = Page(items=[])
    assert bool(page) is False


def test_validation_result_is_valid_when_all_modules_valid():
    result = ValidationResult(
        validations=[
            ProductModuleValidation(productModuleNumber="M1", valid=True),
            ProductModuleValidation(productModuleNumber="M2", valid=True),
        ]
    )
    assert result.is_valid() is True


def test_validation_result_not_valid_when_any_module_invalid():
    result = ValidationResult(
        validations=[
            ProductModuleValidation(productModuleNumber="M1", valid=True),
            ProductModuleValidation(productModuleNumber="M2", valid=False),
        ]
    )
    assert result.is_valid() is False


def test_validation_result_empty_is_not_valid():
    assert ValidationResult(validations=[]).is_valid() is False


def test_validation_from_response_parses_ttl():
    payload = {
        "infos": {"info": []},
        "items": {
            "item": [
                {
                    "type": "ProductModuleValidation",
                    "property": [
                        {"name": "productModuleNumber", "value": "MOD-1"},
                        {"name": "valid", "value": "true"},
                    ],
                    "list": [],
                }
            ]
        },
        "ttl": "720",
    }
    result = validation_from_response(payload)
    assert result.ttl == 720
    assert result.is_valid()


def test_license_model_to_form_excludes_in_use():
    lic = License(number="L-1", active=True, in_use=True)
    form = lic.to_form()
    assert "inUse" not in form
    assert form["number"] == "L-1"


def test_license_template_to_form_excludes_in_use():
    tmpl = LicenseTemplate(number="LT-1", active=True, in_use=True, licenseType="FEATURE")
    form = tmpl.to_form()
    assert "inUse" not in form


def test_product_to_form_no_discounts():
    p = Product(number="P-1", active=True, name="Test")
    form = p.to_form()
    assert form["number"] == "P-1"
    assert "discount" not in form


def test_product_to_form_with_empty_discounts():
    p = Product(number="P-1", discounts=[])
    form = p.to_form()
    assert form["discount"] == [""]
