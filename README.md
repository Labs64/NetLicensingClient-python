<a href="https://netlicensing.io"><img src="https://netlicensing.io/img/netlicensing-stage-twitter.jpg" alt="Innovative License Management Solution"></a>

# [Labs64 NetLicensing](https://netlicensing.io) Client (Python)

[![Python Client - CI](https://github.com/Labs64/NetLicensingClient-python/workflows/Python%20Client%20-%20CI/badge.svg)](https://github.com/Labs64/NetLicensingClient-python/actions?query=workflow%3A%22Python+Client+-+CI%22)
[![PyPI](https://img.shields.io/pypi/v/netlicensing-client.svg)](https://pypi.org/project/netlicensing-client/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/netlicensing-client)](https://pypistats.org/packages/netlicensing-client)
[![PyVer](https://img.shields.io/pypi/pyversions/netlicensing-client.svg)](https://pypi.org/project/netlicensing-client)
[![codecov](https://codecov.io/gh/Labs64/NetLicensingClient-python/graph/badge.svg?token=3J0585YLgO)](https://codecov.io/gh/Labs64/NetLicensingClient-python)
<br>
[![Apache License 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://github.com/Labs64/NetLicensingClient-python/blob/master/LICENSE)
[![📖 Documentation](https://img.shields.io/badge/📖%20Documentation-Wiki-AB6543.svg)](https://netlicensing.io/wiki/restful-api)
[![NetLicensing @ LinkedIn](https://img.shields.io/badge/NetLicensing-0077B5.svg?logo=LinkedIn)](https://www.linkedin.com/showcase/netlicensing)

Python client library for the [Labs64 NetLicensing](https://netlicensing.io) RESTful API.

Built on **Python 3.11+**, [httpx](https://www.python-httpx.org/) and [Pydantic v2](https://docs.pydantic.dev/).
Supports API-key and username/password authentication, automatic retries with exponential back-off,
strongly-typed response models, and transparent pagination.

---

## Table of Contents

- [Installation](#installation)
- [Quickstart](#quickstart)
- [Configuration and Authentication](#configuration-and-authentication)
- [Services](#services)
  - [Products](#products)
  - [Product Modules](#product-modules)
  - [Licensees](#licensees)
  - [Validation](#validation)
  - [License Templates](#license-templates)
  - [Licenses](#licenses)
  - [Tokens](#tokens)
  - [Bundles](#bundles)
  - [Transactions](#transactions)
  - [Payment Methods](#payment-methods)
  - [Notifications](#notifications)
  - [Utility](#utility)
- [Pagination and Iteration](#pagination-and-iteration)
- [Error Handling](#error-handling)
- [Context Manager](#context-manager)
- [Models and Enums](#models-and-enums)
- [Custom Properties](#custom-properties)
- [Demo](#demo)
- [Development](#development)
- [References](#references)
- [How to Contribute](#how-to-contribute)
- [Bugs and Feedback](#bugs-and-feedback)
- [License](#license)

---

## Installation

```bash
pip install netlicensing-client
```

For local development (installs test tools, type checker, and build utilities):

```bash
git clone https://github.com/Labs64/NetLicensingClient-python.git
cd NetLicensingClient-python
pip install -e ".[dev]"
```

---

## Quickstart

```python
from netlicensing import NetLicensingClient

# Authenticate with an API key (or set NETLICENSING_API_KEY in the environment)
client = NetLicensingClient(api_key="YOUR_API_KEY")

result = client.validation.validate(
    "CUSTOMER-1",
    product_number="PRODUCT-1",
    product_module_parameters={
        "MODULE-1": {"nodeSecret": "machine-or-device-id"},
    },
)

if result.is_valid():
    print("✅ License is valid")
else:
    print("❌ License is invalid or expired")
```

---

## Configuration and Authentication

Constructor parameters take precedence over environment variables, which take
precedence over defaults.

### Environment variables

| Variable | Default | Description |
|---|---|---|
| `NETLICENSING_API_KEY` | — | API key (recommended) |
| `NETLICENSING_USERNAME` | — | Username for basic auth |
| `NETLICENSING_PASSWORD` | — | Password for basic auth |
| `NETLICENSING_VENDOR_NUMBER` | — | Vendor number (informational) |
| `NETLICENSING_BASE_URL` | `https://go.netlicensing.io/core/v2/rest` | API base URL |
| `NETLICENSING_TIMEOUT` | `30.0` | Total request timeout in seconds |
| `NETLICENSING_CONNECT_TIMEOUT` | `10.0` | Connection timeout in seconds |
| `NETLICENSING_RETRIES` | `2` | Maximum retry attempts on transient errors |
| `NETLICENSING_RETRY_BACKOFF` | `0.5` | Base back-off in seconds (doubles per attempt) |
| `NETLICENSING_VERIFY` | `true` | Verify TLS certificates |

```bash
export NETLICENSING_API_KEY="YOUR_API_KEY"
export NETLICENSING_VENDOR_NUMBER="VXXXXXXXX"
```

```python
from netlicensing import NetLicensingClient

# No arguments needed — credentials are read from the environment
client = NetLicensingClient()
```

### API-key authentication (recommended)

NetLicensing uses HTTP Basic Auth with username `apiKey` and the key as the
password. Never hard-code API keys — use environment variables, deployment
secrets, or a secrets manager.

```python
client = NetLicensingClient(api_key="YOUR_API_KEY")
```

### Username / password authentication

Suitable for trusted server-side contexts only.

```python
client = NetLicensingClient(username="demo", password="demo")
```

### Advanced constructor parameters

```python
client = NetLicensingClient(
    api_key="YOUR_API_KEY",
    timeout=60.0,
    connect_timeout=15.0,
    retries=3,
    retry_backoff=1.0,
    headers={"X-Custom-Header": "value"},
)
```

---

## Services

The client exposes one service attribute per NetLicensing resource:

| Attribute | Resource | Main operations |
|---|---|---|
| `client.products` | Product | `create`, `get`, `list`, `iterate`, `update`, `delete` |
| `client.product_modules` | ProductModule | `create`, `get`, `list`, `iterate`, `update`, `delete` |
| `client.licensees` | Licensee | `create`, `get`, `list`, `iterate`, `update`, `delete`, `validate`, `transfer` |
| `client.license_templates` | LicenseTemplate | `create`, `get`, `list`, `iterate`, `update`, `delete` |
| `client.licenses` | License | `create`, `get`, `list`, `iterate`, `update`, `delete` |
| `client.tokens` | Token | `create`, `get`, `list`, `iterate`, `delete`, `create_shop_token`, `create_api_key_token` |
| `client.transactions` | Transaction | `get`, `list`, `iterate` |
| `client.payment_methods` | PaymentMethod | `get`, `list`, `iterate` |
| `client.bundles` | Bundle | `create`, `get`, `list`, `iterate`, `update`, `delete`, `obtain` |
| `client.notifications` | Notification | `create`, `get`, `list`, `iterate`, `update`, `delete` |
| `client.utility` | (reference data) | `list_countries`, `list_license_types`, `list_licensing_models` |
| `client.validation` | (shortcut) | `validate` |

---

### Products

```python
from netlicensing import NetLicensingClient

client = NetLicensingClient()

# Create
product = client.products.create(
    number="P-MYAPP-1",
    name="My Application",
    version="2.0",
    active=True,
    description="A great application",
    licensee_auto_create=True,
)

# Read
product = client.products.get("P-MYAPP-1")
print(product.name, product.version)

# List (first page)
page = client.products.list({"active": True})
for p in page:
    print(p.number, p.name)

# Update
product = client.products.update("P-MYAPP-1", name="My Application v2", version="2.1")

# Delete (cascade removes all dependent resources)
client.products.delete("P-MYAPP-1", force_cascade=True)
```

---

### Product Modules

```python
from netlicensing import LicensingModel

module = client.product_modules.create(
    product_number="P-MYAPP-1",
    number="M-MAIN",
    name="Main Module",
    licensing_model=LicensingModel.SUBSCRIPTION,
    active=True,
)

module = client.product_modules.get("M-MAIN")
client.product_modules.update("M-MAIN", name="Main Module (updated)")
client.product_modules.delete("M-MAIN")
```

---

### Licensees

```python
# Create a customer
licensee = client.licensees.create(
    product_number="P-MYAPP-1",
    number="CUSTOMER-42",
    name="Acme Corp",
    active=True,
)

# Read
licensee = client.licensees.get("CUSTOMER-42")

# Update
client.licensees.update("CUSTOMER-42", name="Acme Corporation", active=True)

# Transfer all licenses to another licensee
client.licensees.transfer("CUSTOMER-42", source_licensee_number="CUSTOMER-OLD")

# Delete
client.licensees.delete("CUSTOMER-42")
```

---

### Validation

Use `client.validation.validate()` (or `client.licensees.validate()`) to check
whether a customer holds a valid license.

```python
from netlicensing import ValidationParameters

# Simple call — keyword arguments
result = client.validation.validate(
    "CUSTOMER-42",
    product_number="P-MYAPP-1",
    product_module_parameters={
        "M-FLOATING": {"sessionId": "session-abc123", "action": "checkOut"},
    },
)

# Using a ValidationParameters model
params = ValidationParameters(
    product_number="P-MYAPP-1",
    product_module_parameters={
        "M-NODELOCKED": {"nodeSecret": "hardware-fingerprint"},
    },
)
result = client.validation.validate("CUSTOMER-42", params)

# Inspect the result
print(result.is_valid())          # True if all modules are valid
print(result.ttl)                  # TTL in seconds (for offline use)

module_result = result.by_product_module("M-MAIN")
if module_result:
    print(module_result.valid, module_result.licensing_model, module_result.warning_level)
```

---

### License Templates

```python
from netlicensing import LicenseType

# FEATURE template (perpetual, free)
template = client.license_templates.create(
    product_module_number="M-MAIN",
    number="LT-FEATURE",
    name="Feature License",
    license_type=LicenseType.FEATURE,
    price=0,
    active=True,
    automatic=True,   # auto-assign to new licensees
)

# TIMEVOLUME template (annual subscription, € 99)
template = client.license_templates.create(
    product_module_number="M-SUB",
    number="LT-ANNUAL",
    name="Annual Subscription",
    license_type=LicenseType.TIMEVOLUME,
    price=99.00,
    currency="EUR",
    timeVolume=365,
    timeVolumePeriod="DAY",
)

template = client.license_templates.get("LT-ANNUAL")
client.license_templates.update("LT-ANNUAL", price=79.00)
client.license_templates.delete("LT-ANNUAL")
```

---

### Licenses

```python
from datetime import date

# Assign a license to a customer
license_obj = client.licenses.create(
    licensee_number="CUSTOMER-42",
    license_template_number="LT-ANNUAL",
    active=True,
    startDate=date.today().isoformat(),
)

license_obj = client.licenses.get(license_obj.number)
client.licenses.update(license_obj.number, active=False)
client.licenses.delete(license_obj.number)
```

---

### Tokens

#### NetLicensing Shop token

Generates a one-time checkout URL for the customer-facing NetLicensing Shop.

```python
token = client.tokens.create_shop_token(
    "CUSTOMER-42",
    product_number="P-MYAPP-1",
    success_url="https://vendor.example/success",
    cancel_url="https://vendor.example/cancel",
    success_url_title="Back to the app",
    cancel_url_title="Cancel",
)

print(token.shop_url)   # redirect the customer here
```

#### API key token

```python
from netlicensing import ApiKeyRole

token = client.tokens.create_api_key_token(
    api_key_role=ApiKeyRole.OPERATION,
)

print(token.number)   # use as the api_key for a scoped client
```

#### Token management

```python
# List all active tokens
page = client.tokens.list()

# Revoke a token
client.tokens.delete("TOKEN-NUMBER")
```

---

### Bundles

A bundle groups one or more license templates so they can be sold together.

```python
# Create a bundle
bundle = client.bundles.create(
    number="B-STARTER",
    name="Starter Pack",
    license_template_numbers=["LT-FEATURE-A", "LT-FEATURE-B"],
    price=49.00,
    currency="EUR",
    active=True,
)

bundle = client.bundles.get("B-STARTER")
client.bundles.update("B-STARTER", name="Starter Pack (updated)")

# Obtain — creates licenses from all templates in the bundle for a customer
licenses_page = client.bundles.obtain("B-STARTER", licensee_number="CUSTOMER-42")

client.bundles.delete("B-STARTER")
```

---

### Transactions

Transactions are created automatically by NetLicensing.

```python
# List closed transactions
page = client.transactions.list({"status": "CLOSED"})
for txn in page:
    print(txn.number, txn.status, txn.grand_total, txn.currency)

# Retrieve a single transaction
txn = client.transactions.get("TX-12345")
```

---

### Payment Methods

```python
page = client.payment_methods.list({"active": True})
for pm in page:
    print(pm.number)
```

---

### Notifications

```python
from netlicensing import NotificationProtocol, NotificationEvent

notification = client.notifications.create(
    number="NOTIF-1",
    name="License Events Webhook",
    protocol=NotificationProtocol.WEBHOOK,
    endpoint="https://vendor.example/hooks/netlicensing",
    events=[NotificationEvent.LICENSE_CREATED, NotificationEvent.LICENSE_UPDATED],
    active=True,
)

client.notifications.update("NOTIF-1", name="License Events Webhook (updated)")
client.notifications.delete("NOTIF-1")
```

---

### Utility

```python
# Countries with VAT rates
page = client.utility.list_countries()
for country in page:
    print(country.code, country.name, country.vat_percent, country.is_eu)

# Supported license types and licensing models
print(client.utility.list_license_types())
print(client.utility.list_licensing_models())
```

---

## Pagination and Iteration

All `list()` calls return a `Page[T]` object:

```python
page = client.licensees.list({"active": True})

print(page.page_number)   # 0-based current page
print(page.total_pages)
print(page.total_items)
print(page.has_next)

for licensee in page:     # Page is iterable
    print(licensee.number)

print(len(page))          # number of items on this page
print(bool(page))         # False when the page is empty
```

Use `iterate()` to transparently walk all pages without manual pagination:

```python
for licensee in client.licensees.iterate({"active": True}):
    print(licensee.number, licensee.name)
```

Control pagination explicitly:

```python
page = client.licensees.list(pageNumber=0, itemsNumber=20)
while page.has_next:
    page = client.licensees.list(pageNumber=page.page_number + 1, itemsNumber=20)
    for item in page:
        print(item.number)
```

---

## Error Handling

All exceptions inherit from `NetLicensingError`:

```
NetLicensingError
├── NetLicensingHTTPError       status_code, payload, method, url, request_id
│   └── NetLicensingAuthError   raised on HTTP 401 / 403
├── NetLicensingNetworkError    raised on connection or protocol errors
│   └── NetLicensingTimeoutError  raised when the request times out
└── NetLicensingValidationError raised when a response cannot be parsed
```

```python
from netlicensing import (
    NetLicensingAuthError,
    NetLicensingHTTPError,
    NetLicensingNetworkError,
    NetLicensingTimeoutError,
    NetLicensingValidationError,
)

try:
    product = client.products.get("UNKNOWN")
except NetLicensingAuthError:
    print("Check your API key or permissions")
    raise
except NetLicensingHTTPError as exc:
    print(f"HTTP {exc.status_code}: {exc}")
    print(f"Request: {exc.method} {exc.url}")
    if exc.request_id:
        print(f"Request-ID: {exc.request_id}")
except NetLicensingTimeoutError:
    print("Request timed out — retry later")
except NetLicensingNetworkError:
    print("Network error")
except NetLicensingValidationError:
    print("Unexpected response format")
```

---

## Context Manager

`NetLicensingClient` implements the context manager protocol. The underlying
HTTP connection pool is released on exit.

```python
with NetLicensingClient(api_key="YOUR_API_KEY") as client:
    result = client.validation.validate("CUSTOMER-42")
    print(result.is_valid())
# HTTP client is closed automatically
```

---

## Models and Enums

All public symbols are importable directly from `netlicensing`:

```python
from netlicensing import (
    # Client
    NetLicensingClient,
    NetLicensingConfig,

    # Exceptions
    NetLicensingError,
    NetLicensingAuthError,
    NetLicensingHTTPError,
    NetLicensingNetworkError,
    NetLicensingTimeoutError,
    NetLicensingValidationError,

    # Entity models
    Bundle,
    Country,
    License,
    LicenseTemplate,
    Licensee,
    Notification,
    Page,
    PaymentMethod,
    Product,
    ProductDiscount,
    ProductModule,
    Token,
    Transaction,
    ValidationParameters,
    ValidationResult,

    # Enums
    ApiKeyRole,
    LicenseeSecretMode,
    LicenseType,
    LicensingModel,
    NotificationEvent,
    NotificationProtocol,
    TokenType,
    TransactionSource,
    TransactionStatus,
)
```

### Key enums

| Enum | Values |
|---|---|
| `LicensingModel` | `TRY_AND_BUY`, `SUBSCRIPTION`, `RENTAL`, `FLOATING`, `MULTI_FEATURE`, `PAY_PER_USE`, `PRICING_TABLE`, `QUOTA`, `NODE_LOCKED`, `DISCOUNT` |
| `LicenseType` | `FEATURE`, `TIMEVOLUME`, `FLOATING`, `QUANTITY` |
| `TokenType` | `DEFAULT`, `SHOP`, `APIKEY`, `ACTION` |
| `ApiKeyRole` | `LICENSEE`, `ANALYTICS`, `OPERATION`, `MAINTENANCE`, `ADMIN` |
| `TransactionStatus` | `PENDING`, `CLOSED`, `CANCELLED` |
| `NotificationProtocol` | `EMAIL`, `WEBHOOK` |
| `NotificationEvent` | `TRANSACTION_STATUS_CHANGED`, `LICENSEE_CREATED`, `LICENSEE_UPDATED`, `LICENSE_CREATED`, `LICENSE_UPDATED` |

---

## Custom Properties

NetLicensing supports arbitrary custom properties on most resources. Pass them
as keyword arguments or include them in a model instance:

```python
# As keyword arguments
licensee = client.licensees.create(
    product_number="P-MYAPP-1",
    number="CUSTOMER-99",
    name="Widget Corp",
    companyId="WIDGET-CORP",   # custom property
    tier="enterprise",         # custom property
)

# Via model (extra fields are preserved and round-tripped)
from netlicensing import Licensee

licensee = Licensee(number="CUSTOMER-99", name="Widget Corp", companyId="WIDGET-CORP")
result = client.licensees.update("CUSTOMER-99", licensee)

# Access custom properties
print(licensee.model_extra)   # {'companyId': 'WIDGET-CORP', 'tier': 'enterprise'}
```

---

## Demo

A small command-line demo app is included in [`demo/`](demo/).

```bash
# Validate a licensee
NETLICENSING_API_KEY=YOUR_KEY python demo/app.py validate CUSTOMER-42 \
    --product-number P-MYAPP-1 \
    --module M-MAIN \
    --node-secret "my-hardware-id"

# Generate a Shop checkout URL
NETLICENSING_API_KEY=YOUR_KEY python demo/app.py shop-token CUSTOMER-42 \
    --product-number P-MYAPP-1 \
    --success-url https://vendor.example/success \
    --cancel-url https://vendor.example/cancel
```

---

## Development

```bash
# Run the full test suite (no network access needed — uses httpx.MockTransport)
pytest

# Build distribution packages
python -m build

# Validate the built packages before uploading
twine check dist/*

# Type-check the library
mypy
```

The test suite does not call live NetLicensing servers. To run the demo-account
smoke test when you have internet access:

```bash
NETLICENSING_LIVE_DEMO=1 pytest tests/test_live_demo.py -v
```

That test authenticates as `demo:demo`, creates a temporary `APIKEY` token for
the demo vendor, uses it for a product-list call, and revokes the token.

---

## References

- [NetLicensing RESTful API](https://netlicensing.io/wiki/restful-api)
- [NetLicensing Security / API Key Identification](https://netlicensing.io/wiki/security)
- [NetLicensing Management Console](https://ui.netlicensing.io)
- [NetLicensing Licensing Models](https://netlicensing.io/wiki/licensing-models)

---

## How to Contribute

Everyone is welcome to [contribute](CONTRIBUTING.md) to this project!
Once you're done with your changes, send a pull request and check
[CI Status](https://github.com/Labs64/NetLicensingClient-python/actions).
Thanks!

## Bugs and Feedback

For bugs, questions, and discussions please use
[GitHub Issues](https://github.com/Labs64/NetLicensingClient-python/issues).

## License

This library is open-sourced software licensed under the
[Apache License Version 2.0](LICENSE).

---

Visit Labs64 NetLicensing at https://netlicensing.io
