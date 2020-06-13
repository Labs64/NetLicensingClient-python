"""Transaction service."""

from __future__ import annotations

from typing import Any

from netlicensing.models import Transaction, TransactionSource, TransactionStatus
from netlicensing.services.base import ResourceService


class TransactionService(ResourceService[Transaction]):
    """Read and admin operations for transactions."""

    endpoint = "transaction"
    item_type = "Transaction"
    model = Transaction
    supports_delete = False

    def create(
        self,
        transaction: Transaction | dict[str, Any] | None = None,
        *,
        status: TransactionStatus | str | None = None,
        source: TransactionSource | str | None = None,
        active: bool | None = None,
        number: str | None = None,
        **properties: Any,
    ) -> Transaction:
        return self._create_resource(
            transaction,
            status=status,
            source=source,
            active=active,
            number=number,
            **properties,
        )

    def update(
        self,
        number: str,
        transaction: Transaction | dict[str, Any] | None = None,
        *,
        status: TransactionStatus | str | None = None,
        active: bool | None = None,
        **properties: Any,
    ) -> Transaction:
        return self._update_resource(number, transaction, status=status, active=active, **properties)

    def delete(self, number: str, *, force_cascade: bool = False) -> bool:
        raise NotImplementedError("NetLicensing does not expose public transaction deletion")
