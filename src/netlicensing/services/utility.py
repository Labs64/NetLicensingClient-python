"""Utility/reference-data service."""

from __future__ import annotations

from netlicensing.models import Country, Page
from netlicensing.models.response import item_to_dict, page_from_response, NetLicensingResponse


class UtilityService:
    """Reference-data endpoints exposed by NetLicensing."""

    def __init__(self, client) -> None:  # type: ignore[no-untyped-def]
        self.client = client

    def list_countries(self, filter: str | None = None) -> Page[Country]:
        params = {"filter": filter} if filter else None
        payload = self.client._request("GET", "utility/countries", params=params)
        return page_from_response(payload, model=Country, item_type="Country")

    def list_license_types(self) -> list[str]:
        payload = self.client._request("GET", "utility/licenseTypes")
        return self._reference_values(payload, "LicenseType")

    def list_licensing_models(self) -> list[str]:
        payload = self.client._request("GET", "utility/licensingModels")
        return self._reference_values(payload, "LicensingModelProperties")

    @staticmethod
    def _reference_values(payload, item_type: str) -> list[str]:  # type: ignore[no-untyped-def]
        response = NetLicensingResponse.from_payload(payload)
        values: list[str] = []
        for item in response.items:
            if item.get("type") == item_type:
                data = item_to_dict(item)
                value = data.get("name") or data.get("number") or data.get("value") or data.get("licenseType")
                if value is not None:
                    values.append(str(value))
        return values
