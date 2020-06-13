from __future__ import annotations

import os

import pytest

from netlicensing import ApiKeyRole, NetLicensingClient


pytestmark = pytest.mark.integration


def _live_enabled() -> bool:
    return os.getenv("NETLICENSING_LIVE_DEMO") == "1"


@pytest.mark.skipif(not _live_enabled(), reason="set NETLICENSING_LIVE_DEMO=1 to run live demo-account tests")
def test_demo_user_can_create_temporary_api_key_and_use_it() -> None:
    """Exercise the demo vendor without requiring persistent credentials.

    The temporary API key is the created APIKEY token number. It is deleted in
    the finally block to revoke it after the smoke test.
    """

    base_url = os.getenv("NETLICENSING_BASE_URL", "https://go.netlicensing.io/core/v2/rest")
    admin = NetLicensingClient(
        username=os.getenv("NETLICENSING_DEMO_USERNAME", "demo"),
        password=os.getenv("NETLICENSING_DEMO_PASSWORD", "demo"),
        base_url=base_url,
        retries=1,
    )
    token_number: str | None = None
    try:
        token = admin.tokens.create_api_key_token(api_key_role=ApiKeyRole.ANALYTICS)
        token_number = token.number
        assert token_number

        api_client = NetLicensingClient(api_key=token_number, base_url=base_url, retries=1)
        products = api_client.products.list()
        assert products.items
    finally:
        if token_number:
            admin.tokens.delete(token_number)
