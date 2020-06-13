"""Pagination model."""

from __future__ import annotations

from collections.abc import Iterator
from typing import Generic, TypeVar

from pydantic import Field

from netlicensing.models.base import NetLicensingModel

T = TypeVar("T")


class Page(NetLicensingModel, Generic[T]):
    """A page of NetLicensing resources."""

    items: list[T] = Field(default_factory=list)
    page_number: int | None = Field(default=None, alias="pagenumber")
    items_number: int | None = Field(default=None, alias="itemsnumber")
    total_pages: int | None = Field(default=None, alias="totalpages")
    total_items: int | None = Field(default=None, alias="totalitems")
    has_next: bool | None = Field(default=None, alias="hasnext")

    def __iter__(self) -> Iterator[T]:  # type: ignore[override]
        return iter(self.items)

    def __len__(self) -> int:
        return len(self.items)

    def __bool__(self) -> bool:
        return bool(self.items)
