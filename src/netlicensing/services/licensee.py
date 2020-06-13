"""Licensee service."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from netlicensing.models import Licensee, ValidationParameters, ValidationResult
from netlicensing.models.response import validation_from_response
from netlicensing.services.base import ResourceService
from netlicensing.services.helpers import merge_payload


class LicenseeService(ResourceService[Licensee]):
    """CRUD, validation, and transfer operations for licensees."""

    endpoint = "licensee"
    item_type = "Licensee"
    model = Licensee

    def create(
        self,
        licensee: Licensee | dict[str, Any] | None = None,
        *,
        product_number: str | None = None,
        number: str | None = None,
        active: bool | None = None,
        name: str | None = None,
        **custom_properties: Any,
    ) -> Licensee:
        return self._create_resource(
            licensee,
            productNumber=product_number,
            number=number,
            active=active,
            name=name,
            **custom_properties,
        )

    def update(
        self,
        number: str,
        licensee: Licensee | dict[str, Any] | None = None,
        *,
        active: bool | None = None,
        name: str | None = None,
        marked_for_transfer: bool | None = None,
        **custom_properties: Any,
    ) -> Licensee:
        return self._update_resource(
            number,
            licensee,
            active=active,
            name=name,
            markedForTransfer=marked_for_transfer,
            **custom_properties,
        )

    def validate(
        self,
        number: str,
        parameters: ValidationParameters | Mapping[str, Any] | None = None,
        *,
        product_number: str | None = None,
        licensee_name: str | None = None,
        for_offline_use: bool | None = None,
        dry_run: bool | None = None,
        product_module_parameters: dict[str, dict[str, Any] | None] | None = None,
        **extra_parameters: Any,
    ) -> ValidationResult:
        validation_parameters = parameters
        if not isinstance(validation_parameters, ValidationParameters):
            validation_parameters = ValidationParameters.model_validate(parameters or {})
        if product_module_parameters:
            validation_parameters.product_module_parameters.update(product_module_parameters)
        data = merge_payload(
            validation_parameters,
            productNumber=product_number,
            licenseeName=licensee_name,
            forOfflineUse=for_offline_use,
            dryRun=dry_run,
            **extra_parameters,
        )
        payload = self.client._request("POST", f"{self.endpoint}/{number}/validate", data=data)
        return validation_from_response(payload)

    def transfer(self, number: str, source_licensee_number: str) -> bool:
        self.client._request(
            "POST",
            f"{self.endpoint}/{number}/transfer",
            data={"sourceLicenseeNumber": source_licensee_number},
        )
        return True
