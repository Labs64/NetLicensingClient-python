"""Bundle service."""

from __future__ import annotations

from typing import Any

from netlicensing.models import Bundle, License, Page
from netlicensing.models.response import page_from_response
from netlicensing.services.base import ResourceService


class BundleService(ResourceService[Bundle]):
    """CRUD and obtain operations for bundles."""

    endpoint = "bundle"
    item_type = "Bundle"
    model = Bundle

    def create(
        self,
        bundle: Bundle | dict[str, Any] | None = None,
        *,
        number: str | None = None,
        active: bool | None = None,
        name: str | None = None,
        license_template_numbers: list[str] | None = None,
        **properties: Any,
    ) -> Bundle:
        return self._create_resource(
            bundle,
            number=number,
            active=active,
            name=name,
            licenseTemplateNumbers=",".join(license_template_numbers) if license_template_numbers is not None else None,
            **properties,
        )

    def update(
        self,
        number: str,
        bundle: Bundle | dict[str, Any] | None = None,
        *,
        active: bool | None = None,
        name: str | None = None,
        license_template_numbers: list[str] | None = None,
        **properties: Any,
    ) -> Bundle:
        return self._update_resource(
            number,
            bundle,
            active=active,
            name=name,
            licenseTemplateNumbers=",".join(license_template_numbers) if license_template_numbers is not None else None,
            **properties,
        )

    def obtain(self, number: str, licensee_number: str, *, transaction_number: str | None = None) -> Page[License]:
        payload = self.client._request(
            "POST",
            f"{self.endpoint}/{number}/obtain",
            data={"licenseeNumber": licensee_number, "transactionNumber": transaction_number},
        )
        return page_from_response(payload, model=License, item_type="License")
