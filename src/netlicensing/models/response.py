"""NetLicensing response envelope parsing."""

from __future__ import annotations

from collections.abc import Mapping
from enum import Enum
import json
from typing import Any, TypeVar

from pydantic import Field

from netlicensing.exceptions import NetLicensingValidationError
from netlicensing.models.base import NetLicensingModel
from netlicensing.models.entities import ProductModuleValidation, ValidationResult
from netlicensing.models.pagination import Page


class InfoType(str, Enum):
    ERROR = "ERROR"
    WARNING = "WARNING"
    INFO = "INFO"


class Info(NetLicensingModel):
    id: str | None = None
    type: InfoType | str | None = None
    value: str | None = None


class NetLicensingResponse(NetLicensingModel):
    signature: str | None = None
    infos: list[Info] = Field(default_factory=list)
    items: list[dict[str, Any]] = Field(default_factory=list)
    ttl: int | None = None
    pagination: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_payload(cls, payload: Mapping[str, Any] | None) -> "NetLicensingResponse":
        payload = payload or {}
        infos_raw = _ensure_list(_dig(payload, "infos", "info"))
        items_obj = payload.get("items") if isinstance(payload, Mapping) else {}
        items_raw = _ensure_list(_dig(payload, "items", "item"))
        pagination: dict[str, Any] = {}
        if isinstance(items_obj, Mapping):
            for key in ("pagenumber", "itemsnumber", "totalpages", "totalitems", "hasnext"):
                if key in items_obj and items_obj[key] is not None:
                    pagination[key] = items_obj[key]
        return cls(
            signature=payload.get("signature"),
            infos=[Info.model_validate(info) for info in infos_raw if isinstance(info, Mapping)],
            items=[dict(item) for item in items_raw if isinstance(item, Mapping)],
            ttl=_cast_int(payload.get("ttl")),
            pagination=pagination,
        )

    def error_infos(self) -> list[Info]:
        return [info for info in self.infos if str(info.type) == InfoType.ERROR.value]


ModelT = TypeVar("ModelT", bound=NetLicensingModel)


def page_from_response(
    payload: Mapping[str, Any] | None,
    *,
    model: type[ModelT],
    item_type: str,
) -> Page[ModelT]:
    response = NetLicensingResponse.from_payload(payload)
    items = [model.model_validate(item_to_dict(item)) for item in response.items if item.get("type") == item_type]
    return Page[ModelT](items=items, **response.pagination)


def model_from_response(
    payload: Mapping[str, Any] | None,
    *,
    model: type[ModelT],
    item_type: str,
) -> ModelT:
    page = page_from_response(payload, model=model, item_type=item_type)
    if not page.items:
        raise NetLicensingValidationError(f"Response did not contain item of type {item_type!r}")
    return page.items[0]


def validation_from_response(payload: Mapping[str, Any] | None) -> ValidationResult:
    response = NetLicensingResponse.from_payload(payload)
    validations = [
        ProductModuleValidation.model_validate(item_to_dict(item))
        for item in response.items
        if item.get("type") == "ProductModuleValidation"
    ]
    return ValidationResult(validations=validations, ttl=response.ttl)


def item_to_dict(item: Mapping[str, Any] | None) -> dict[str, Any]:
    """Convert an API item/list envelope to a flat Python mapping."""

    if not item:
        return {}
    result: dict[str, Any] = {}
    for prop in _ensure_list(item.get("property")):
        if isinstance(prop, Mapping) and "name" in prop:
            result[str(prop["name"])] = _cast_value(prop.get("value"))
    for list_item in _ensure_list(item.get("list")):
        if isinstance(list_item, Mapping) and "name" in list_item:
            name = str(list_item["name"])
            result.setdefault(name, [])
            result[name].append(item_to_dict(list_item))
    return result


def response_message(payload: Any, fallback: str) -> str:
    if isinstance(payload, Mapping):
        response = NetLicensingResponse.from_payload(payload)
        errors = [info.value for info in response.error_infos() if info.value]
        if errors:
            return "; ".join(errors)
        infos = [info.value for info in response.infos if info.value]
        if infos:
            return "; ".join(infos)
    return fallback


def _dig(mapping: Mapping[str, Any], *path: str) -> Any:
    value: Any = mapping
    for part in path:
        if not isinstance(value, Mapping):
            return None
        value = value.get(part)
    return value


def _ensure_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def _cast_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _cast_value(value: Any) -> Any:
    if value is None:
        return None
    if not isinstance(value, str):
        return value
    stripped = value.strip()
    if stripped == "true":
        return True
    if stripped == "false":
        return False
    if stripped == "null":
        return None
    if (stripped.startswith("{") and stripped.endswith("}")) or (stripped.startswith("[") and stripped.endswith("]")):
        try:
            return json.loads(stripped)
        except json.JSONDecodeError:
            return value
    return value
