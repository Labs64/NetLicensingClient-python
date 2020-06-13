"""Payment method service."""

from __future__ import annotations

from typing import Any

from netlicensing.models import PaymentMethod
from netlicensing.services.base import ResourceService


class PaymentMethodService(ResourceService[PaymentMethod]):
    """Read and update operations for payment methods."""

    endpoint = "paymentmethod"
    item_type = "PaymentMethod"
    model = PaymentMethod
    supports_create = False
    supports_delete = False

    def create(self, resource: PaymentMethod | dict[str, Any] | None = None, **properties: Any) -> PaymentMethod:
        raise NotImplementedError("NetLicensing does not expose public payment method creation")

    def update(
        self,
        number: str,
        payment_method: PaymentMethod | dict[str, Any] | None = None,
        **properties: Any,
    ) -> PaymentMethod:
        return self._update_resource(number, payment_method, **properties)

    def delete(self, number: str, *, force_cascade: bool = False) -> bool:
        raise NotImplementedError("NetLicensing does not expose public payment method deletion")
