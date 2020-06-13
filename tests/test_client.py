from __future__ import annotations

import base64

import httpx
import pytest

from netlicensing import NetLicensingAuthError, NetLicensingClient, NetLicensingNetworkError, NetLicensingTimeoutError
from netlicensing.config import NetLicensingConfig
from tests.conftest import envelope, validation_envelope


def test_api_key_auth_header(make_client, requests_seen):
    client = make_client(lambda request: httpx.Response(204, request=request))

    assert client.products.delete("P-1")

    auth = requests_seen[0].headers["Authorization"]
    scheme, token = auth.split(" ", 1)
    assert scheme == "Basic"
    assert base64.b64decode(token).decode() == "apiKey:secret-api-key"
    assert str(requests_seen[0].url) == "https://example.test/core/v2/rest/product/P-1"


def test_username_password_auth_header(requests_seen):
    def handler(request: httpx.Request) -> httpx.Response:
        requests_seen.append(request)
        return httpx.Response(204, request=request)

    client = NetLicensingClient(
        username="admin",
        password="secret",
        base_url="https://example.test/core/v2/rest",
        retries=0,
        transport=httpx.MockTransport(handler),
    )
    client.products.delete("P-1")

    auth = requests_seen[0].headers["Authorization"]
    scheme, token = auth.split(" ", 1)
    assert scheme == "Basic"
    assert base64.b64decode(token).decode() == "admin:secret"


def test_config_reads_environment(monkeypatch):
    monkeypatch.setenv("NETLICENSING_API_KEY", "env-key")
    monkeypatch.setenv("NETLICENSING_VENDOR_NUMBER", "VENDOR-1")

    config = NetLicensingConfig.from_env()

    assert config.api_key == "env-key"
    assert config.vendor_number == "VENDOR-1"
    assert config.base_url == "https://go.netlicensing.io/core/v2/rest"


def test_http_error_maps_auth_error(make_client):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            403,
            json={"infos": {"info": [{"id": "403", "type": "ERROR", "value": "Access is denied"}]}},
            request=request,
        )

    client = make_client(handler)

    with pytest.raises(NetLicensingAuthError) as exc:
        client.products.get("P-1")

    assert exc.value.status_code == 403
    assert "Access is denied" in str(exc.value)


def test_network_error_is_wrapped(requests_seen):
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("dns failed", request=request)

    client = NetLicensingClient(
        api_key="secret-api-key",
        base_url="https://example.test/core/v2/rest",
        retry_backoff=0,
        retries=0,
        transport=httpx.MockTransport(handler),
    )

    with pytest.raises(NetLicensingNetworkError):
        client.products.get("P-1")


def test_timeout_error_is_wrapped():
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.TimeoutException("timed out", request=request)

    client = NetLicensingClient(
        api_key="key",
        base_url="https://example.test/core/v2/rest",
        retries=0,
        retry_backoff=0,
        transport=httpx.MockTransport(handler),
    )
    with pytest.raises(NetLicensingTimeoutError):
        client.products.get("P-1")


def test_context_manager_closes_client():
    call_log: list[str] = []
    handler = lambda req: httpx.Response(204, request=req)  # noqa: E731

    with NetLicensingClient(
        api_key="key",
        base_url="https://example.test/core/v2/rest",
        retries=0,
        transport=httpx.MockTransport(handler),
    ) as client:
        assert client is not None


def test_about_returns_string():
    client = NetLicensingClient(
        api_key="key",
        base_url="https://example.test/core/v2/rest",
        retries=0,
    )
    about = client.about()
    assert "NetLicensing" in about
    client.close()


def test_retry_on_server_error(requests_seen):
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        requests_seen.append(request)
        calls["n"] += 1
        if calls["n"] < 3:
            return httpx.Response(503, request=request)
        return httpx.Response(200, json=envelope("Product", {"number": "P-1", "active": True}), request=request)

    client = NetLicensingClient(
        api_key="key",
        base_url="https://example.test/core/v2/rest",
        retries=2,
        retry_backoff=0,
        transport=httpx.MockTransport(handler),
    )
    product = client.products.get("P-1")
    assert product.number == "P-1"
    assert len(requests_seen) == 3


def test_validate_shortcut(make_client):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=validation_envelope(True), request=request)

    client = make_client(handler)
    result = client.validate("CUST-1")
    assert result.is_valid()


def test_get_licensee_shortcut(make_client):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=envelope("Licensee", {"number": "CUST-1", "active": "true"}), request=request)

    client = make_client(handler)
    licensee = client.get_licensee("CUST-1")
    assert licensee.number == "CUST-1"


def test_delete_licensee_shortcut(make_client):
    client = make_client(lambda req: httpx.Response(204, request=req))
    assert client.delete_licensee("CUST-1") is True


def test_api_error_info_in_200_response_raises(make_client):
    """A 200 response that contains ERROR infos should still raise."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "infos": {"info": [{"id": "EX001", "type": "ERROR", "value": "Something went wrong"}]},
                "items": {"item": []},
            },
            request=request,
        )

    client = make_client(handler)
    from netlicensing import NetLicensingHTTPError

    with pytest.raises(NetLicensingHTTPError, match="Something went wrong"):
        client.products.get("P-1")


def test_config_env_numeric_overrides(monkeypatch):
    monkeypatch.setenv("NETLICENSING_TIMEOUT", "60")
    monkeypatch.setenv("NETLICENSING_RETRIES", "5")
    monkeypatch.setenv("NETLICENSING_RETRY_BACKOFF", "1.5")

    config = NetLicensingConfig.from_env()

    assert config.timeout == 60.0
    assert config.retries == 5
    assert config.retry_backoff == 1.5

