"""License template service."""

from __future__ import annotations

from typing import Any

from netlicensing.models import LicenseTemplate, LicenseType
from netlicensing.services.base import ResourceService


class LicenseTemplateService(ResourceService[LicenseTemplate]):
    """CRUD operations for license templates."""

    endpoint = "licensetemplate"
    item_type = "LicenseTemplate"
    model = LicenseTemplate

    def create(
        self,
        license_template: LicenseTemplate | dict[str, Any] | None = None,
        *,
        product_module_number: str | None = None,
        number: str | None = None,
        active: bool | None = None,
        name: str | None = None,
        license_type: LicenseType | str | None = None,
        **custom_properties: Any,
    ) -> LicenseTemplate:
        return self._create_resource(
            license_template,
            productModuleNumber=product_module_number,
            number=number,
            active=active,
            name=name,
            licenseType=license_type,
            **custom_properties,
        )

    def update(
        self,
        number: str,
        license_template: LicenseTemplate | dict[str, Any] | None = None,
        *,
        active: bool | None = None,
        name: str | None = None,
        **custom_properties: Any,
    ) -> LicenseTemplate:
        return self._update_resource(number, license_template, active=active, name=name, **custom_properties)
