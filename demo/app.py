from __future__ import annotations

import argparse
import json
from typing import Any

from netlicensing import NetLicensingClient


def main() -> None:
    parser = argparse.ArgumentParser(description="NetLicensing Python client demo")
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate", help="Validate a licensee")
    validate.add_argument("licensee_number")
    validate.add_argument("--product-number")
    validate.add_argument("--module", dest="product_module_number")
    validate.add_argument("--node-secret")
    validate.add_argument("--session-id")
    validate.add_argument("--action")

    shop = subparsers.add_parser("shop-token", help="Create a NetLicensing Shop token")
    shop.add_argument("licensee_number")
    shop.add_argument("--product-number")
    shop.add_argument("--license-template-number")
    shop.add_argument("--success-url")
    shop.add_argument("--cancel-url")

    args = parser.parse_args()
    client = NetLicensingClient()

    if args.command == "validate":
        module_parameters: dict[str, dict[str, Any]] = {}
        if args.product_module_number:
            values = {
                key: value
                for key, value in {
                    "nodeSecret": args.node_secret,
                    "sessionId": args.session_id,
                    "action": args.action,
                }.items()
                if value is not None
            }
            module_parameters[args.product_module_number] = values

        result = client.validation.validate(
            args.licensee_number,
            product_number=args.product_number,
            product_module_parameters=module_parameters or None,
        )
        print(json.dumps(result.model_dump(mode="json", by_alias=True), indent=2))
        return

    if args.command == "shop-token":
        token = client.tokens.create_shop_token(
            args.licensee_number,
            product_number=args.product_number,
            license_template_number=args.license_template_number,
            success_url=args.success_url,
            cancel_url=args.cancel_url,
        )
        print(token.shop_url or token.model_dump_json(by_alias=True, indent=2))


if __name__ == "__main__":
    main()
