"""Client configuration for NetLicensing."""

from __future__ import annotations

from dataclasses import dataclass, field
import os
from typing import Mapping

DEFAULT_BASE_URL = "https://go.netlicensing.io/core/v2/rest"
DEFAULT_TIMEOUT = 30.0
DEFAULT_CONNECT_TIMEOUT = 10.0
DEFAULT_RETRIES = 2
DEFAULT_RETRY_BACKOFF = 0.25


@dataclass(frozen=True, slots=True)
class NetLicensingConfig:
    """Immutable NetLicensing client configuration.

    Values can be passed explicitly to :class:`netlicensing.NetLicensingClient`
    or loaded from environment variables with :meth:`from_env`.
    """

    base_url: str = DEFAULT_BASE_URL
    api_key: str | None = None
    username: str | None = None
    password: str | None = None
    vendor_number: str | None = None
    timeout: float = DEFAULT_TIMEOUT
    connect_timeout: float = DEFAULT_CONNECT_TIMEOUT
    retries: int = DEFAULT_RETRIES
    retry_backoff: float = DEFAULT_RETRY_BACKOFF
    verify: bool = True
    headers: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "base_url", self.base_url.rstrip("/"))

    @classmethod
    def from_env(
        cls,
        *,
        base_url: str | None = None,
        api_key: str | None = None,
        username: str | None = None,
        password: str | None = None,
        vendor_number: str | None = None,
        timeout: float | None = None,
        connect_timeout: float | None = None,
        retries: int | None = None,
        retry_backoff: float | None = None,
        verify: bool | None = None,
        headers: Mapping[str, str] | None = None,
    ) -> "NetLicensingConfig":
        """Build configuration from explicit arguments and environment defaults."""

        return cls(
            base_url=base_url or os.getenv("NETLICENSING_BASE_URL") or DEFAULT_BASE_URL,
            api_key=api_key or os.getenv("NETLICENSING_API_KEY") or None,
            username=username or os.getenv("NETLICENSING_USERNAME") or None,
            password=password or os.getenv("NETLICENSING_PASSWORD") or None,
            vendor_number=vendor_number or os.getenv("NETLICENSING_VENDOR_NUMBER") or None,
            timeout=timeout if timeout is not None else _float_env("NETLICENSING_TIMEOUT", DEFAULT_TIMEOUT),
            connect_timeout=connect_timeout
            if connect_timeout is not None
            else _float_env("NETLICENSING_CONNECT_TIMEOUT", DEFAULT_CONNECT_TIMEOUT),
            retries=retries if retries is not None else _int_env("NETLICENSING_RETRIES", DEFAULT_RETRIES),
            retry_backoff=retry_backoff
            if retry_backoff is not None
            else _float_env("NETLICENSING_RETRY_BACKOFF", DEFAULT_RETRY_BACKOFF),
            verify=verify if verify is not None else _bool_env("NETLICENSING_VERIFY", True),
            headers=headers or {},
        )

    @property
    def has_auth(self) -> bool:
        return bool(self.api_key or (self.username and self.password))


def _float_env(name: str, default: float) -> float:
    value = os.getenv(name)
    if not value:
        return default
    try:
        return float(value)
    except ValueError:
        return default


def _int_env(name: str, default: int) -> int:
    value = os.getenv(name)
    if not value:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _bool_env(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if not value:
        return default
    return value.lower() not in {"0", "false", "no", "off"}
