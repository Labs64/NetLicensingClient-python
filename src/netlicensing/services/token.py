"""Token service."""

from __future__ import annotations

from typing import Any

from netlicensing.models import ApiKeyRole, Token, TokenType
from netlicensing.services.base import ResourceService


class TokenService(ResourceService[Token]):
    """Operations for shop, API key, action, and default tokens."""

    endpoint = "token"
    item_type = "Token"
    model = Token

    def create(
        self,
        token: Token | dict[str, Any] | None = None,
        *,
        token_type: TokenType | str | None = None,
        licensee_number: str | None = None,
        **properties: Any,
    ) -> Token:
        return self._create_resource(token, tokenType=token_type, licenseeNumber=licensee_number, **properties)

    def create_shop_token(
        self,
        licensee_number: str,
        *,
        product_number: str | None = None,
        license_template_number: str | None = None,
        success_url: str | None = None,
        cancel_url: str | None = None,
        success_url_title: str | None = None,
        cancel_url_title: str | None = None,
        **properties: Any,
    ) -> Token:
        """Create a one-time NetLicensing Shop token and return its shop URL."""

        return self.create(
            token_type=TokenType.SHOP,
            licensee_number=licensee_number,
            productNumber=product_number,
            licenseTemplateNumber=license_template_number,
            successURL=success_url,
            cancelURL=cancel_url,
            successURLTitle=success_url_title,
            cancelURLTitle=cancel_url_title,
            **properties,
        )

    def create_api_key_token(
        self,
        *,
        api_key_role: ApiKeyRole | str = ApiKeyRole.LICENSEE,
        licensee_number: str | None = None,
        **properties: Any,
    ) -> Token:
        return self.create(
            token_type=TokenType.APIKEY,
            licensee_number=licensee_number,
            apiKeyRole=api_key_role,
            **properties,
        )

    def delete(self, number: str, *, force_cascade: bool = False) -> bool:
        self.client._request("DELETE", f"{self.endpoint}/{number}", expected_status={200, 202, 204})
        return True
