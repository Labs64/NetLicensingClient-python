"""Product module service."""

from __future__ import annotations

from typing import Any

from netlicensing.models import LicensingModel, ProductModule
from netlicensing.services.base import ResourceService


class ProductModuleService(ResourceService[ProductModule]):
    """CRUD operations for product modules."""

    endpoint = "productmodule"
    item_type = "ProductModule"
    model = ProductModule

    def create(
        self,
        product_module: ProductModule | dict[str, Any] | None = None,
        *,
        product_number: str | None = None,
        number: str | None = None,
        active: bool | None = None,
        name: str | None = None,
        licensing_model: LicensingModel | str | None = None,
        **custom_properties: Any,
    ) -> ProductModule:
        return self._create_resource(
            product_module,
            productNumber=product_number,
            number=number,
            active=active,
            name=name,
            licensingModel=licensing_model,
            **custom_properties,
        )

    def update(
        self,
        number: str,
        product_module: ProductModule | dict[str, Any] | None = None,
        *,
        active: bool | None = None,
        name: str | None = None,
        **custom_properties: Any,
    ) -> ProductModule:
        return self._update_resource(number, product_module, active=active, name=name, **custom_properties)
