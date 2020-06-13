from __future__ import annotations

from collections.abc import Callable
from urllib.parse import parse_qs

import httpx
import pytest

from netlicensing import NetLicensingClient


def envelope(item_type: str, properties: dict[str, object], *, ttl: str | None = None) -> dict[str, object]:
    body: dict[str, object] = {
        "infos": {"info": []},
        "items": {
            "item": [
                {
                    "type": item_type,
                    "property": [{"name": key, "value": str(value).lower() if isinstance(value, bool) else str(value)} for key, value in properties.items()],
                    "list": [],
                }
            ]
        },
        "signature": None,
        "ttl": ttl,
    }
    return body


def page_envelope(item_type: str, rows: list[dict[str, object]]) -> dict[str, object]:
    return {
        "infos": {"info": []},
        "items": {
            "pagenumber": "0",
            "itemsnumber": str(len(rows)),
            "totalpages": "1",
            "totalitems": str(len(rows)),
            "hasnext": "false",
            "item": [
                {
                    "type": item_type,
                    "property": [
                        {"name": key, "value": str(value).lower() if isinstance(value, bool) else str(value)}
                        for key, value in row.items()
                    ],
                    "list": [],
                }
                for row in rows
            ],
        },
        "signature": None,
        "ttl": None,
    }


def validation_envelope(valid: bool = True) -> dict[str, object]:
    return {
        "infos": {"info": []},
        "items": {
            "item": [
                {
                    "type": "ProductModuleValidation",
                    "property": [
                        {"name": "productModuleNumber", "value": "MOD-1"},
                        {"name": "valid", "value": str(valid).lower()},
                        {"name": "licensingModel", "value": "Subscription"},
                    ],
                    "list": [],
                }
            ]
        },
        "signature": None,
        "ttl": "1440",
    }


@pytest.fixture
def requests_seen() -> list[httpx.Request]:
    return []


@pytest.fixture
def make_client(requests_seen: list[httpx.Request]) -> Callable[[Callable[[httpx.Request], httpx.Response]], NetLicensingClient]:
    def factory(handler: Callable[[httpx.Request], httpx.Response]) -> NetLicensingClient:
        def transport_handler(request: httpx.Request) -> httpx.Response:
            requests_seen.append(request)
            return handler(request)

        return NetLicensingClient(
            api_key="secret-api-key",
            base_url="https://example.test/core/v2/rest",
            retry_backoff=0,
            transport=httpx.MockTransport(transport_handler),
        )

    return factory


def form_body(request: httpx.Request) -> dict[str, str]:
    parsed = parse_qs(request.content.decode())
    return {key: values[-1] for key, values in parsed.items()}
