"""Product service."""

from __future__ import annotations

from typing import Any

from netlicensing.models import Product
from netlicensing.services.base import ResourceService


class ProductService(ResourceService[Product]):
    """CRUD operations for NetLicensing products."""

    endpoint = "product"
    item_type = "Product"
    model = Product

    def create(
        self,
        product: Product | dict[str, Any] | None = None,
        *,
        number: str | None = None,
        active: bool | None = None,
        name: str | None = None,
        version: str | None = None,
        description: str | None = None,
        licensing_info: str | None = None,
        licensee_auto_create: bool | None = None,
        **custom_properties: Any,
    ) -> Product:
        return self._create_resource(
            product,
            number=number,
            active=active,
            name=name,
            version=version,
            description=description,
            licensingInfo=licensing_info,
            licenseeAutoCreate=licensee_auto_create,
            **custom_properties,
        )

    def update(
        self,
        number: str,
        product: Product | dict[str, Any] | None = None,
        *,
        active: bool | None = None,
        name: str | None = None,
        version: str | None = None,
        description: str | None = None,
        licensing_info: str | None = None,
        licensee_auto_create: bool | None = None,
        **custom_properties: Any,
    ) -> Product:
        return self._update_resource(
            number,
            product,
            active=active,
            name=name,
            version=version,
            description=description,
            licensingInfo=licensing_info,
            licenseeAutoCreate=licensee_auto_create,
            **custom_properties,
        )
