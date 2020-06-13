"""Exception hierarchy for the NetLicensing client."""

from __future__ import annotations

from typing import Any


class NetLicensingError(Exception):
    """Base exception for all NetLicensing client errors."""


class NetLicensingNetworkError(NetLicensingError):
    """Raised for transport-level failures such as DNS and connection errors."""


class NetLicensingTimeoutError(NetLicensingNetworkError):
    """Raised when a NetLicensing request times out."""


class NetLicensingHTTPError(NetLicensingError):
    """Raised for non-success HTTP responses or API-level error payloads."""

    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        payload: Any = None,
        method: str | None = None,
        url: str | None = None,
        request_id: str | None = None,
    ) -> None:
        self.status_code = status_code
        self.payload = payload
        self.method = method
        self.url = url
        self.request_id = request_id
        prefix = f"HTTP {status_code}: " if status_code is not None else ""
        super().__init__(f"{prefix}{message}")


class NetLicensingAuthError(NetLicensingHTTPError):
    """Raised for authentication or authorization failures."""


class NetLicensingValidationError(NetLicensingError):
    """Raised when a client-side validation or response parsing error occurs."""
