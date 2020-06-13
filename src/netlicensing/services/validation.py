"""Validation service."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any
from typing import TYPE_CHECKING

from netlicensing.models import ValidationParameters, ValidationResult

if TYPE_CHECKING:
    from netlicensing.client import NetLicensingClient


class ValidationService:
    """Convenience wrapper for licensee validation endpoints."""

    def __init__(self, client: "NetLicensingClient") -> None:
        self.client = client

    def validate(
        self,
        licensee_number: str,
        parameters: ValidationParameters | Mapping[str, Any] | None = None,
        **extra_parameters: Any,
    ) -> ValidationResult:
        return self.client.licensees.validate(licensee_number, parameters, **extra_parameters)
