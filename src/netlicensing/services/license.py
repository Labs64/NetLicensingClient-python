"""License service."""

from __future__ import annotations

from typing import Any

from netlicensing.models import License
from netlicensing.services.base import ResourceService


class LicenseService(ResourceService[License]):
    """CRUD operations for licenses."""

    endpoint = "license"
    item_type = "License"
    model = License

    def create(
        self,
        license: License | dict[str, Any] | None = None,
        *,
        licensee_number: str | None = None,
        license_template_number: str | None = None,
        transaction_number: str | None = None,
        number: str | None = None,
        active: bool | None = None,
        name: str | None = None,
        **custom_properties: Any,
    ) -> License:
        return self._create_resource(
            license,
            licenseeNumber=licensee_number,
            licenseTemplateNumber=license_template_number,
            transactionNumber=transaction_number,
            number=number,
            active=active,
            name=name,
            **custom_properties,
        )

    def update(
        self,
        number: str,
        license: License | dict[str, Any] | None = None,
        *,
        transaction_number: str | None = None,
        active: bool | None = None,
        name: str | None = None,
        **custom_properties: Any,
    ) -> License:
        return self._update_resource(
            number,
            license,
            transactionNumber=transaction_number,
            active=active,
            name=name,
            **custom_properties,
        )
