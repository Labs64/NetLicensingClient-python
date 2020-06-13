"""NetLicensing entity models."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any

from pydantic import AliasChoices, Field, field_validator, model_validator

from netlicensing.models.base import FormValue, NetLicensingModel, serialize_form


class _StrEnum(str, Enum):
    def __str__(self) -> str:
        return str(self.value)


class LicenseeSecretMode(_StrEnum):
    DISABLED = "DISABLED"
    PREDEFINED = "PREDEFINED"
    CLIENT = "CLIENT"


class LicensingModel(_StrEnum):
    TRY_AND_BUY = "TryAndBuy"
    SUBSCRIPTION = "Subscription"
    RENTAL = "Rental"
    FLOATING = "Floating"
    MULTI_FEATURE = "MultiFeature"
    PAY_PER_USE = "PayPerUse"
    PRICING_TABLE = "PricingTable"
    QUOTA = "Quota"
    NODE_LOCKED = "NodeLocked"
    DISCOUNT = "Discount"


class LicenseType(_StrEnum):
    FEATURE = "FEATURE"
    TIMEVOLUME = "TIMEVOLUME"
    FLOATING = "FLOATING"
    QUANTITY = "QUANTITY"


class TokenType(_StrEnum):
    DEFAULT = "DEFAULT"
    SHOP = "SHOP"
    APIKEY = "APIKEY"
    ACTION = "ACTION"


class ApiKeyRole(_StrEnum):
    LICENSEE = "ROLE_APIKEY_LICENSEE"
    ANALYTICS = "ROLE_APIKEY_ANALYTICS"
    OPERATION = "ROLE_APIKEY_OPERATION"
    MAINTENANCE = "ROLE_APIKEY_MAINTENANCE"
    ADMIN = "ROLE_APIKEY_ADMIN"


class TransactionStatus(_StrEnum):
    PENDING = "PENDING"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"


class TransactionSource(_StrEnum):
    SHOP = "SHOP"
    AUTO_LICENSE_CREATE = "AUTO_LICENSE_CREATE"
    AUTO_LICENSE_UPDATE = "AUTO_LICENSE_UPDATE"
    AUTO_LICENSE_DELETE = "AUTO_LICENSE_DELETE"
    AUTO_LICENSEE_CREATE = "AUTO_LICENSEE_CREATE"
    AUTO_LICENSEE_DELETE = "AUTO_LICENSEE_DELETE"
    AUTO_LICENSEE_VALIDATE = "AUTO_LICENSEE_VALIDATE"
    AUTO_LICENSETEMPLATE_DELETE = "AUTO_LICENSETEMPLATE_DELETE"
    AUTO_PRODUCTMODULE_DELETE = "AUTO_PRODUCTMODULE_DELETE"
    AUTO_PRODUCT_DELETE = "AUTO_PRODUCT_DELETE"
    AUTO_LICENSES_TRANSFER = "AUTO_LICENSES_TRANSFER"
    SUBSCRIPTION_UPDATE = "SUBSCRIPTION_UPDATE"
    RECURRING_PAYMENT = "RECURRING_PAYMENT"
    CANCEL_RECURRING_PAYMENT = "CANCEL_RECURRING_PAYMENT"
    OBTAIN_BUNDLE = "OBTAIN_BUNDLE"


class PaymentMethodType(_StrEnum):
    NULL = "NULL"
    PAYPAL = "PAYPAL"
    PAYPAL_SANDBOX = "PAYPAL_SANDBOX"
    STRIPE = "STRIPE"
    STRIPE_TESTING = "STRIPE_TESTING"


class NotificationProtocol(_StrEnum):
    EMAIL = "EMAIL"
    WEBHOOK = "WEBHOOK"


class NotificationEvent(_StrEnum):
    TRANSACTION_STATUS_CHANGED = "TRANSACTION_STATUS_CHANGED"
    LICENSEE_CREATED = "LICENSEE_CREATED"
    LICENSEE_UPDATED = "LICENSEE_UPDATED"
    LICENSE_CREATED = "LICENSE_CREATED"
    LICENSE_UPDATED = "LICENSE_UPDATED"


class ProductDiscount(NetLicensingModel):
    total_price: Decimal | None = Field(default=None, alias="totalPrice")
    currency: str | None = None
    amount_fix: Decimal | None = Field(default=None, alias="amountFix")
    amount_percent: Decimal | None = Field(default=None, alias="amountPercent")

    @model_validator(mode="after")
    def _check_amount(self) -> "ProductDiscount":
        if self.amount_fix is not None and self.amount_percent is not None:
            raise ValueError("amount_fix and amount_percent cannot both be set")
        return self

    def as_api_value(self) -> str:
        amount: Decimal | None
        suffix = ""
        if self.amount_percent is not None:
            amount = self.amount_percent
            suffix = "%"
        else:
            amount = self.amount_fix
        if self.total_price is None or self.currency is None or amount is None:
            return ""
        return f"{self.total_price};{self.currency};{amount}{suffix}"


class Product(NetLicensingModel):
    active: bool | None = None
    number: str | None = None
    name: str | None = None
    version: str | None = None
    description: str | None = None
    licensing_info: str | None = Field(default=None, alias="licensingInfo")
    licensee_auto_create: bool | None = Field(default=None, alias="licenseeAutoCreate")
    licensee_secret_mode: LicenseeSecretMode | str | None = Field(default=None, alias="licenseeSecretMode")
    vat_mode: str | None = Field(default=None, alias="vatMode")
    discounts: list[ProductDiscount] | None = Field(default=None, alias="discount")
    in_use: bool | None = Field(default=None, alias="inUse")

    def to_form(self, *, exclude: set[str] | None = None) -> dict[str, FormValue]:
        form = serialize_form(self, exclude=(exclude or set()) | {"in_use", "discounts"})
        if self.discounts is not None:
            form["discount"] = [discount.as_api_value() for discount in self.discounts] if self.discounts else [""]
        return form


class ProductModule(NetLicensingModel):
    active: bool | None = None
    number: str | None = None
    name: str | None = None
    licensing_model: LicensingModel | str | None = Field(default=None, alias="licensingModel")
    product_number: str | None = Field(default=None, alias="productNumber")
    in_use: bool | None = Field(default=None, alias="inUse")

    def to_form(self, *, exclude: set[str] | None = None) -> dict[str, FormValue]:
        return serialize_form(self, exclude=(exclude or set()) | {"in_use"})


class Licensee(NetLicensingModel):
    active: bool | None = None
    number: str | None = None
    name: str | None = None
    product_number: str | None = Field(default=None, alias="productNumber")
    marked_for_transfer: bool | None = Field(default=None, alias="markedForTransfer")
    licensee_secret: str | None = Field(default=None, alias="licenseeSecret")
    aliases: list[str] | None = None
    in_use: bool | None = Field(default=None, alias="inUse")

    @field_validator("aliases", mode="before")
    @classmethod
    def _split_aliases(cls, value: Any) -> Any:
        if isinstance(value, str):
            return [part for part in value.split(",") if part]
        return value

    def to_form(self, *, exclude: set[str] | None = None) -> dict[str, FormValue]:
        return serialize_form(self, exclude=(exclude or set()) | {"in_use", "aliases"})


class LicenseTemplate(NetLicensingModel):
    active: bool | None = None
    number: str | None = None
    name: str | None = None
    license_type: LicenseType | str | None = Field(default=None, alias="licenseType")
    price: Decimal | None = None
    currency: str | None = None
    automatic: bool | None = None
    hidden: bool | None = None
    hide_licenses: bool | None = Field(default=None, alias="hideLicenses")
    product_module_number: str | None = Field(default=None, alias="productModuleNumber")
    in_use: bool | None = Field(default=None, alias="inUse")

    def to_form(self, *, exclude: set[str] | None = None) -> dict[str, FormValue]:
        return serialize_form(self, exclude=(exclude or set()) | {"in_use"})


class License(NetLicensingModel):
    active: bool | None = None
    number: str | None = None
    name: str | None = None
    price: Decimal | None = None
    currency: str | None = None
    hidden: bool | None = None
    licensee_number: str | None = Field(default=None, alias="licenseeNumber")
    license_template_number: str | None = Field(default=None, alias="licenseTemplateNumber")
    product_module_number: str | None = Field(default=None, alias="productModuleNumber")
    start_date: datetime | str | None = Field(default=None, alias="startDate")
    in_use: bool | None = Field(default=None, alias="inUse")

    def to_form(self, *, exclude: set[str] | None = None) -> dict[str, FormValue]:
        return serialize_form(self, exclude=(exclude or set()) | {"in_use"})


class Token(NetLicensingModel):
    active: bool | None = None
    number: str | None = None
    expiration_time: datetime | None = Field(default=None, alias="expirationTime")
    token_type: TokenType | str | None = Field(default=None, alias="tokenType")
    vendor_number: str | None = Field(default=None, alias="vendorNumber")
    licensee_number: str | None = Field(default=None, alias="licenseeNumber")
    license_template_number: str | None = Field(default=None, alias="licenseTemplateNumber")
    action: str | None = None
    api_key_role: ApiKeyRole | str | None = Field(default=None, alias="apiKeyRole")
    bundle_number: str | None = Field(default=None, alias="bundleNumber")
    bundle_price: Decimal | None = Field(default=None, alias="bundlePrice")
    product_number: str | None = Field(default=None, alias="productNumber")
    predefined_shopping_item: str | None = Field(default=None, alias="predefinedShoppingItem")
    success_url: str | None = Field(default=None, alias="successURL")
    success_url_title: str | None = Field(default=None, alias="successURLTitle")
    cancel_url: str | None = Field(default=None, alias="cancelURL")
    cancel_url_title: str | None = Field(default=None, alias="cancelURLTitle")
    shop_url: str | None = Field(default=None, alias="shopURL")

    def to_form(self, *, exclude: set[str] | None = None) -> dict[str, FormValue]:
        return serialize_form(self, exclude=(exclude or set()) | {"shop_url", "vendor_number"})


class Transaction(NetLicensingModel):
    active: bool | None = None
    number: str | None = None
    status: TransactionStatus | str | None = None
    source: TransactionSource | str | None = None
    grand_total: Decimal | None = Field(default=None, alias="grandTotal")
    discount: Decimal | None = None
    currency: str | None = None
    date_created: datetime | None = Field(
        default=None,
        alias="dateCreated",
        validation_alias=AliasChoices("dateCreated", "datecreated"),
    )
    date_closed: datetime | None = Field(
        default=None,
        alias="dateClosed",
        validation_alias=AliasChoices("dateClosed", "dateclosed"),
    )
    payment_method: PaymentMethodType | str | None = Field(default=None, alias="paymentMethod")
    license_transaction_joins: list[dict[str, Any]] | None = Field(default=None, alias="licenseTransactionJoin")
    in_use: bool | None = Field(default=None, alias="inUse")

    def to_form(self, *, exclude: set[str] | None = None) -> dict[str, FormValue]:
        return serialize_form(self, exclude=(exclude or set()) | {"in_use", "license_transaction_joins"})


class PaymentMethod(NetLicensingModel):
    active: bool | None = None
    number: str | None = None


class Bundle(NetLicensingModel):
    active: bool | None = None
    number: str | None = None
    name: str | None = None
    price: Decimal | None = None
    currency: str | None = None
    product_number: str | None = Field(default=None, alias="productNumber")
    license_template_numbers: list[str] | None = Field(default=None, alias="licenseTemplateNumbers")
    stale_license_template_numbers: list[str] | None = Field(default=None, alias="staleLicenseTemplateNumbers")
    description: str | None = None

    @field_validator("license_template_numbers", "stale_license_template_numbers", mode="before")
    @classmethod
    def _split_numbers(cls, value: Any) -> Any:
        if isinstance(value, str):
            return [part for part in value.split(",") if part]
        return value

    def to_form(self, *, exclude: set[str] | None = None) -> dict[str, FormValue]:
        form = serialize_form(
            self,
            exclude=(exclude or set()) | {"stale_license_template_numbers", "license_template_numbers"},
        )
        if self.license_template_numbers is not None:
            form["licenseTemplateNumbers"] = ",".join(self.license_template_numbers)
        return form


class Notification(NetLicensingModel):
    active: bool | None = None
    number: str | None = None
    name: str | None = None
    protocol: NotificationProtocol | str | None = None
    events: list[NotificationEvent | str] | None = None
    payload: str | None = None
    endpoint: str | None = None

    @field_validator("events", mode="before")
    @classmethod
    def _split_events(cls, value: Any) -> Any:
        if isinstance(value, str):
            return [part for part in value.split(",") if part]
        return value

    def to_form(self, *, exclude: set[str] | None = None) -> dict[str, FormValue]:
        form = serialize_form(self, exclude=(exclude or set()) | {"events"})
        if self.events is not None:
            form["events"] = ",".join(str(event.value if isinstance(event, Enum) else event) for event in self.events)
        return form


class Country(NetLicensingModel):
    code: str | None = None
    name: str | None = None
    vat_percent: Decimal | None = Field(default=None, alias="vatPercent")
    is_eu: bool | None = Field(default=None, alias="isEu")


class ProductModuleValidation(NetLicensingModel):
    product_module_number: str | None = Field(default=None, alias="productModuleNumber")
    valid: bool | None = None
    licensing_model: LicensingModel | str | None = Field(default=None, alias="licensingModel")
    license_type: LicenseType | str | None = Field(default=None, alias="licenseType")
    warning_level: str | None = Field(default=None, alias="warningLevel")

    def is_valid(self) -> bool:
        return self.valid is True


class ValidationResult(NetLicensingModel):
    validations: list[ProductModuleValidation] = Field(default_factory=list)
    ttl: int | None = None

    def is_valid(self) -> bool:
        """Return true when every module validation is explicitly valid."""

        return bool(self.validations) and all(validation.is_valid() for validation in self.validations)

    def by_product_module(self, product_module_number: str) -> ProductModuleValidation | None:
        for validation in self.validations:
            if validation.product_module_number == product_module_number:
                return validation
        return None


class ValidationParameters(NetLicensingModel):
    product_number: str | None = Field(default=None, alias="productNumber")
    licensee_name: str | None = Field(default=None, alias="licenseeName")
    licensee_secret: str | None = Field(default=None, alias="licenseeSecret")
    for_offline_use: bool | None = Field(default=None, alias="forOfflineUse")
    dry_run: bool | None = Field(default=None, alias="dryRun")
    licensee_properties: dict[str, Any] = Field(default_factory=dict)
    product_module_parameters: dict[str, dict[str, Any] | None] = Field(default_factory=dict)

    def to_form(self, *, exclude: set[str] | None = None) -> dict[str, FormValue]:
        form = serialize_form(
            self,
            exclude=(exclude or set()) | {"licensee_properties", "product_module_parameters"},
        )
        form.update(serialize_form(self.licensee_properties))
        for index, (module_number, parameters) in enumerate(self.product_module_parameters.items()):
            form[f"productModuleNumber{index}"] = module_number
            for key, value in (parameters or {}).items():
                serialized = serialize_form({key: value})
                form[f"{key}{index}"] = serialized[key]
        return form
