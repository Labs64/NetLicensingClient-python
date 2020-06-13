"""Base classes for NetLicensing services."""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from typing import Any, Generic, TypeVar

from netlicensing.models import Page
from netlicensing.models.base import NetLicensingModel
from netlicensing.models.response import model_from_response, page_from_response
from netlicensing.services.helpers import clean_params, encode_filter, merge_payload

ModelT = TypeVar("ModelT", bound=NetLicensingModel)


class ResourceService(Generic[ModelT]):
    """Generic CRUD helper for NetLicensing resources."""

    endpoint: str
    item_type: str
    model: type[ModelT]
    supports_delete = True
    supports_create = True
    supports_update = True

    def __init__(self, client: Any) -> None:
        self.client = client

    def get(self, number: str) -> ModelT:
        payload = self.client._request("GET", f"{self.endpoint}/{number}")
        return model_from_response(payload, model=self.model, item_type=self.item_type)

    def list(
        self,
        filter: str | Mapping[str, str | bool | int | float] | None = None,
        *,
        params: Mapping[str, Any] | None = None,
        **query: Any,
    ) -> Page[ModelT]:
        request_params = clean_params(params, **query)
        encoded_filter = encode_filter(filter)
        if encoded_filter:
            request_params["filter"] = encoded_filter
        payload = self.client._request("GET", self.endpoint, params=request_params)
        return page_from_response(payload, model=self.model, item_type=self.item_type)

    def iterate(
        self,
        filter: str | Mapping[str, str | bool | int | float] | None = None,
        *,
        params: Mapping[str, Any] | None = None,
        **query: Any,
    ) -> Iterator[ModelT]:
        """Iterate all items returned by the current API page.

        NetLicensing exposes pagination metadata but no stable public paging
        parameter contract in the client libraries, so this keeps paging
        explicit while still giving callers a simple iterator over each page.
        """

        yield from self.list(filter, params=params, **query).items

    def _create_resource(self, resource: ModelT | Mapping[str, Any] | None = None, **properties: Any) -> ModelT:
        payload = self.client._request("POST", self.endpoint, data=merge_payload(resource, **properties))
        return model_from_response(payload, model=self.model, item_type=self.item_type)

    def _update_resource(
        self,
        number: str,
        resource: ModelT | Mapping[str, Any] | None = None,
        **properties: Any,
    ) -> ModelT:
        payload = self.client._request("POST", f"{self.endpoint}/{number}", data=merge_payload(resource, **properties))
        return model_from_response(payload, model=self.model, item_type=self.item_type)

    def delete(self, number: str, *, force_cascade: bool = False) -> bool:
        params = {"forceCascade": force_cascade} if force_cascade else None
        self.client._request("DELETE", f"{self.endpoint}/{number}", params=params, expected_status={200, 202, 204})
        return True
