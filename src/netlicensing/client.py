"""Synchronous NetLicensing REST client."""

from __future__ import annotations

from collections.abc import Mapping
import time
from typing import Any

import httpx

from netlicensing.config import NetLicensingConfig
from netlicensing.exceptions import (
    NetLicensingAuthError,
    NetLicensingHTTPError,
    NetLicensingNetworkError,
    NetLicensingTimeoutError,
)
from netlicensing.models import Licensee, ValidationResult
from netlicensing.models.response import NetLicensingResponse, response_message

try:
    from importlib.metadata import version as _pkg_version

    _CLIENT_VERSION = _pkg_version("netlicensing-client")
except Exception:  # pragma: no cover
    _CLIENT_VERSION = "0.1.0"  # pragma: no cover

JsonObject = Mapping[str, Any]


class NetLicensingClient:
    """Thin Pythonic wrapper around the NetLicensing RESTful API."""

    def __init__(
        self,
        api_key: str | None = None,
        *,
        nlic_apikey: str | None = None,
        username: str | None = None,
        password: str | None = None,
        vendor_number: str | None = None,
        base_url: str | None = None,
        timeout: float | None = None,
        connect_timeout: float | None = None,
        retries: int | None = None,
        retry_backoff: float | None = None,
        headers: Mapping[str, str] | None = None,
        config: NetLicensingConfig | None = None,
        http_client: httpx.Client | None = None,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        api_key = api_key or nlic_apikey
        self.config = config or NetLicensingConfig.from_env(
            api_key=api_key,
            username=username,
            password=password,
            vendor_number=vendor_number,
            base_url=base_url,
            timeout=timeout,
            connect_timeout=connect_timeout,
            retries=retries,
            retry_backoff=retry_backoff,
            headers=headers,
        )
        self._owns_http_client = http_client is None
        self._http = http_client or self._build_http_client(transport=transport)
        self._install_services()

    def _build_http_client(self, *, transport: httpx.BaseTransport | None = None) -> httpx.Client:
        request_headers = {
            "Accept": "application/json",
            "X-Requested-With": "XMLHttpRequest",
            "User-Agent": f"NetLicensing/Python {_CLIENT_VERSION}",
            **dict(self.config.headers),
        }
        auth: httpx.Auth | None = None
        if self.config.api_key:
            auth = httpx.BasicAuth("apiKey", self.config.api_key)
        elif self.config.username and self.config.password:
            auth = httpx.BasicAuth(self.config.username, self.config.password)
        timeout = httpx.Timeout(self.config.timeout, connect=self.config.connect_timeout)
        return httpx.Client(
            base_url=f"{self.config.base_url}/",
            headers=request_headers,
            auth=auth,
            timeout=timeout,
            verify=self.config.verify,
            transport=transport,
        )

    def _install_services(self) -> None:
        from netlicensing.services import (
            BundleService,
            LicenseeService,
            LicenseService,
            LicenseTemplateService,
            NotificationService,
            PaymentMethodService,
            ProductModuleService,
            ProductService,
            TokenService,
            TransactionService,
            UtilityService,
            ValidationService,
        )

        self.products = ProductService(self)
        self.product_modules = ProductModuleService(self)
        self.licensees = LicenseeService(self)
        self.licenses = LicenseService(self)
        self.license_templates = LicenseTemplateService(self)
        self.tokens = TokenService(self)
        self.transactions = TransactionService(self)
        self.payment_methods = PaymentMethodService(self)
        self.bundles = BundleService(self)
        self.notifications = NotificationService(self)
        self.utility = UtilityService(self)
        self.validation = ValidationService(self)

    def close(self) -> None:
        if self._owns_http_client:
            self._http.close()

    def __enter__(self) -> "NetLicensingClient":
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:  # type: ignore[no-untyped-def]
        self.close()

    def _request(
        self,
        method: str,
        path: str,
        *,
        params: Mapping[str, Any] | None = None,
        data: Mapping[str, Any] | None = None,
        json: Any = None,
        headers: Mapping[str, str] | None = None,
        expected_status: set[int] | None = None,
    ) -> Any:
        """Low-level request helper used by services."""

        expected_status = expected_status or set(range(200, 300))
        method = method.upper()
        url_path = path.lstrip("/")
        request_headers = dict(headers or {})
        if data is not None:
            request_headers.setdefault("Content-Type", "application/x-www-form-urlencoded")
        attempts = max(self.config.retries, 0) + 1

        last_error: Exception | None = None
        for attempt in range(attempts):
            try:
                response = self._http.request(
                    method,
                    url_path,
                    params=_drop_none(params),
                    data=_drop_none(data),
                    json=json,
                    headers=request_headers,
                )
            except httpx.TimeoutException as exc:
                last_error = exc
                if attempt + 1 < attempts:
                    self._sleep_before_retry(attempt)
                    continue
                raise NetLicensingTimeoutError(f"NetLicensing request timed out: {method} /{url_path}") from exc
            except httpx.RequestError as exc:
                last_error = exc
                if attempt + 1 < attempts:
                    self._sleep_before_retry(attempt)
                    continue
                raise NetLicensingNetworkError(f"NetLicensing request failed: {method} /{url_path}") from exc

            if (
                response.status_code in {408, 429, 500, 502, 503, 504}
                and method in {"GET", "HEAD", "OPTIONS"}
                and attempt + 1 < attempts
            ):
                self._sleep_before_retry(attempt)
                continue
            return self._handle_response(response, expected_status=expected_status)

        if last_error:  # pragma: no cover
            raise NetLicensingNetworkError(f"NetLicensing request failed: {method} /{url_path}") from last_error
        raise NetLicensingNetworkError(f"NetLicensing request failed: {method} /{url_path}")  # pragma: no cover

    def _handle_response(self, response: httpx.Response, *, expected_status: set[int]) -> Any:
        payload = self._parse_payload(response)
        request_id = response.headers.get("X-Request-Id") or response.headers.get("X-Correlation-Id")
        if response.status_code not in expected_status:
            message = response_message(payload, response.text or response.reason_phrase)
            error_cls = NetLicensingAuthError if response.status_code in {401, 403} else NetLicensingHTTPError
            raise error_cls(
                message,
                status_code=response.status_code,
                payload=payload,
                method=response.request.method,
                url=str(response.request.url),
                request_id=request_id,
            )
        if isinstance(payload, Mapping):
            envelope = NetLicensingResponse.from_payload(payload)
            errors = envelope.error_infos()
            if errors:
                message = "; ".join(info.value or "NetLicensing API error" for info in errors)
                raise NetLicensingHTTPError(
                    message,
                    status_code=response.status_code,
                    payload=payload,
                    method=response.request.method,
                    url=str(response.request.url),
                    request_id=request_id,
                )
        return payload

    def _parse_payload(self, response: httpx.Response) -> Any:
        if response.status_code == 204 or not response.content:
            return None
        content_type = response.headers.get("Content-Type", "")
        if "json" in content_type.lower():
            return response.json()
        try:
            return response.json()
        except ValueError:
            return response.text

    def _sleep_before_retry(self, attempt: int) -> None:
        if self.config.retry_backoff > 0:
            time.sleep(self.config.retry_backoff * (2**attempt))

    def about(self) -> str:
        return (
            "Labs64 NetLicensing is a Licensing-as-a-Service platform for "
            "software vendors and developers integrating license management."
        )

    def validate(self, licensee_number: str, validation_parameters: Any = None) -> ValidationResult:
        return self.licensees.validate(licensee_number, validation_parameters)

    def get_licensee(self, licensee_number: str) -> Licensee:
        return self.licensees.get(licensee_number)

    def delete_licensee(self, licensee_number: str) -> bool:
        return self.licensees.delete(licensee_number)


def _drop_none(values: Mapping[str, Any] | None) -> dict[str, Any] | None:
    if values is None:
        return None
    return {key: value for key, value in values.items() if value is not None}


NetLicensing = NetLicensingClient
