"""Python client for the Labs64 NetLicensing RESTful API."""

from __future__ import annotations

from netlicensing.client import NetLicensing, NetLicensingClient
from netlicensing.config import NetLicensingConfig
from netlicensing.exceptions import (
    NetLicensingAuthError,
    NetLicensingError,
    NetLicensingHTTPError,
    NetLicensingNetworkError,
    NetLicensingTimeoutError,
    NetLicensingValidationError,
)
from netlicensing.models import (
    ApiKeyRole,
    Bundle,
    Country,
    License,
    LicenseTemplate,
    LicenseType,
    Licensee,
    LicenseeSecretMode,
    LicensingModel,
    Notification,
    NotificationEvent,
    NotificationProtocol,
    Page,
    PaymentMethod,
    Product,
    ProductDiscount,
    ProductModule,
    Token,
    TokenType,
    Transaction,
    TransactionSource,
    TransactionStatus,
    ValidationParameters,
    ValidationResult,
)

__all__ = [
    "ApiKeyRole",
    "Bundle",
    "Country",
    "License",
    "LicenseTemplate",
    "LicenseType",
    "Licensee",
    "LicenseeSecretMode",
    "LicensingModel",
    "NetLicensing",
    "NetLicensingAuthError",
    "NetLicensingClient",
    "NetLicensingConfig",
    "NetLicensingError",
    "NetLicensingHTTPError",
    "NetLicensingNetworkError",
    "NetLicensingTimeoutError",
    "NetLicensingValidationError",
    "Notification",
    "NotificationEvent",
    "NotificationProtocol",
    "Page",
    "PaymentMethod",
    "Product",
    "ProductDiscount",
    "ProductModule",
    "Token",
    "TokenType",
    "Transaction",
    "TransactionSource",
    "TransactionStatus",
    "ValidationParameters",
    "ValidationResult",
]

__version__ = "0.1.0"
