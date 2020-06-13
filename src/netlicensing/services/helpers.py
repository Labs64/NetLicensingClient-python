"""Service helper functions."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from netlicensing.models.base import FormValue, NetLicensingModel, serialize_form


def encode_filter(filter_: str | Mapping[str, str | bool | int | float] | None) -> str | None:
    if filter_ is None:
        return None
    if isinstance(filter_, str):
        return filter_
    return ";".join(f"{key}={value}" for key, value in filter_.items())


def merge_payload(
    resource: NetLicensingModel | Mapping[str, Any] | None = None,
    /,
    **properties: Any,
) -> dict[str, FormValue]:
    form = resource.to_form() if isinstance(resource, NetLicensingModel) else serialize_form(resource)
    form.update(serialize_form(properties))
    return form


def clean_params(params: Mapping[str, Any] | None = None, **extra: Any) -> dict[str, FormValue]:
    combined: dict[str, Any] = {}
    if params:
        combined.update(params)
    combined.update(extra)
    return serialize_form(combined)
