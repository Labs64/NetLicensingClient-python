"""Shared model helpers."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
import json
from typing import Any

from pydantic import BaseModel, ConfigDict

FormValue = str | list[str]


class NetLicensingModel(BaseModel):
    """Base model that accepts NetLicensing custom properties."""

    model_config = ConfigDict(extra="allow", populate_by_name=True, arbitrary_types_allowed=True)

    def to_form(self, *, exclude: set[str] | None = None) -> dict[str, FormValue]:
        """Serialize the model for NetLicensing form-encoded requests."""

        return serialize_form(self, exclude=exclude)


def serialize_form(data: NetLicensingModel | Mapping[str, Any] | None, *, exclude: set[str] | None = None) -> dict[str, FormValue]:
    """Convert model or mapping data into form values accepted by NetLicensing."""

    if data is None:
        return {}

    exclude = exclude or set()
    if isinstance(data, NetLicensingModel):
        raw = data.model_dump(by_alias=True, exclude_none=True, exclude=exclude)
    else:
        raw = {k: v for k, v in data.items() if k not in exclude and v is not None}

    form: dict[str, FormValue] = {}
    for key, value in raw.items():
        if value is None:  # pragma: no cover
            continue
        form[str(key)] = _serialize_value(value)
    return form


def _serialize_value(value: Any) -> FormValue:
    if isinstance(value, Enum):
        return str(value.value)
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, Decimal):
        return format(value, "f")
    if isinstance(value, (str, int, float)):
        return str(value)
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [_serialize_scalar(item) for item in value]
    try:
        return json.dumps(value)
    except TypeError:
        return str(value)


def _serialize_scalar(value: Any) -> str:
    serialized = _serialize_value(value)
    if isinstance(serialized, list):
        return ",".join(serialized)
    return serialized
