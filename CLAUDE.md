# CLAUDE.md — NetLicensing Python Client

This document gives Claude Code everything it needs to navigate, modify, and extend this codebase efficiently.

---

## Project at a Glance

| Item | Value |
|---|---|
| Package name | `netlicensing-client` |
| PyPI import name | `import netlicensing` |
| Python requirement | `>= 3.11` |
| Runtime dependencies | `httpx >= 0.25, < 1` · `pydantic >= 2.5, < 3` |
| Project layout | `src/` layout — library lives in `src/netlicensing/` |
| Entry point | `src/netlicensing/__init__.py` re-exports everything public |
| Type checking | mypy strict mode (`pyproject.toml` `[tool.mypy]`) |
| Formatting | black + isort, line length 120 |

---

## Repository Layout

```
src/netlicensing/
├── __init__.py          # All public symbols re-exported here
├── client.py            # NetLicensingClient — the main class
├── config.py            # NetLicensingConfig (frozen dataclass) + env-var helpers
├── exceptions.py        # Full exception hierarchy
├── py.typed             # PEP 561 marker — do not delete
├── models/
│   ├── __init__.py      # Re-exports all entity models, enums, Page
│   ├── base.py          # NetLicensingModel base, serialize_form(), FormValue
│   ├── entities.py      # All entity models + all enums
│   ├── pagination.py    # Page[T] generic model
│   └── response.py      # NetLicensingResponse envelope parser + helpers
└── services/
    ├── __init__.py      # Re-exports all service classes
    ├── base.py          # ResourceService[ModelT] generic CRUD base
    ├── helpers.py       # encode_filter(), merge_payload(), clean_params()
    ├── bundle.py        # BundleService — extra: obtain()
    ├── license.py       # LicenseService
    ├── license_template.py  # LicenseTemplateService
    ├── licensee.py      # LicenseeService — extra: validate(), transfer()
    ├── notification.py  # NotificationService
    ├── payment_method.py # PaymentMethodService
    ├── product.py       # ProductService
    ├── product_module.py # ProductModuleService
    ├── token.py         # TokenService — extra: create_shop_token(), create_api_key_token()
    ├── transaction.py   # TransactionService
    ├── utility.py       # UtilityService — list_countries(), list_license_types(), list_licensing_models()
    └── validation.py    # ValidationService — thin delegate to licensees.validate()

tests/
├── conftest.py          # Shared fixtures: make_client, envelope helpers, form_body
├── test_client.py       # NetLicensingClient unit tests
├── test_internals.py    # Fine-grained coverage: config, serialize_form, response parsing, helpers
├── test_models.py       # Model + enum unit tests
├── test_services.py     # Service method tests (23 tests, covers all services)
└── test_live_demo.py    # Skipped unless NETLICENSING_LIVE_DEMO=1

demo/
└── app.py               # CLI demo: `validate` and `shop-token` subcommands
```

---

## Development Setup

```bash
pip install -e ".[dev]"   # editable install with all dev deps
pytest                     # run tests + coverage
mypy                       # type-check
python -m build            # build wheel + sdist
twine check dist/*         # verify package metadata
```

---

## Running Tests

```bash
pytest                          # all tests (101 pass, 1 skipped)
pytest tests/test_services.py   # only service tests
pytest -k "token"               # filter by name
pytest --no-cov                 # skip coverage (faster)
NETLICENSING_LIVE_DEMO=1 pytest tests/test_live_demo.py  # live API tests
```

Coverage is reported automatically (`--cov=src/netlicensing --cov-report=term-missing`).  
Target: 99%+ (only 3 genuinely unreachable lines are excluded with `# pragma: no cover`).

---

## Core Architecture

### 1. `NetLicensingClient` (`client.py`)

The single entry point. Instantiated directly by consumers:

```python
from netlicensing import NetLicensingClient
client = NetLicensingClient(api_key="...", base_url="https://...")
```

Key points:
- Wraps `httpx.Client` — **synchronous only**
- Auth is HTTP Basic: API key → `BasicAuth("apiKey", key)`, username/password → `BasicAuth(username, password)`
- All 12 services are lazy-installed as attributes in `_install_services()`
- `_request(method, path, *, params, data, json, headers, expected_status)` is the **single HTTP gateway** — all service code calls this
- Retry loop: max `config.retries + 1` attempts; backs off with `config.retry_backoff * 2^attempt` seconds; retries on timeout, network errors, and `{408, 429, 500, 502, 503, 504}` for idempotent methods only (`GET`, `HEAD`, `OPTIONS`)
- `_handle_response()` raises on non-2xx AND on 2xx responses that contain ERROR-level infos in the envelope
- `NetLicensing` is an alias for `NetLicensingClient` (backwards compat)
- Shortcuts: `client.validate(...)`, `client.get_licensee(...)`, `client.delete_licensee(...)`

### 2. Configuration (`config.py`)

`NetLicensingConfig` is a **frozen dataclass** (`frozen=True, slots=True`). Never mutate it; create a new one.

Environment variables (all optional):

| Env var | Config field | Default |
|---|---|---|
| `NETLICENSING_API_KEY` | `api_key` | `None` |
| `NETLICENSING_USERNAME` | `username` | `None` |
| `NETLICENSING_PASSWORD` | `password` | `None` |
| `NETLICENSING_VENDOR_NUMBER` | `vendor_number` | `None` |
| `NETLICENSING_BASE_URL` | `base_url` | `https://go.netlicensing.io/core/v2/rest` |
| `NETLICENSING_TIMEOUT` | `timeout` | `30.0` |
| `NETLICENSING_CONNECT_TIMEOUT` | `connect_timeout` | `10.0` |
| `NETLICENSING_RETRIES` | `retries` | `2` |
| `NETLICENSING_RETRY_BACKOFF` | `retry_backoff` | `0.25` |
| `NETLICENSING_VERIFY` | `verify` | `True` |

`config.has_auth` → `True` if `api_key` is set, or both `username` + `password` are set.

### 3. Exception Hierarchy (`exceptions.py`)

```
NetLicensingError
├── NetLicensingNetworkError        # DNS, connection refused, etc.
│   └── NetLicensingTimeoutError    # httpx.TimeoutException
├── NetLicensingHTTPError           # Non-2xx HTTP or API-level error info
│   └── NetLicensingAuthError       # 401 / 403
└── NetLicensingValidationError     # Client-side parse / missing item
```

`NetLicensingHTTPError` carries: `status_code`, `payload`, `method`, `url`, `request_id`.

### 4. Models (`models/`)

**`NetLicensingModel`** (base for all entity models):
- Pydantic `BaseModel` with `extra="allow"` — custom (vendor-defined) properties survive round-trips via `model_extra`
- `populate_by_name=True` — use either Python name (`licensee_number`) or API alias (`licenseeNumber`)
- `to_form()` method — serializes the model for `application/x-www-form-urlencoded` POST bodies

**`serialize_form(data, *, exclude)`** (`models/base.py`):
- Converts a `NetLicensingModel` or plain `dict` to `dict[str, str | list[str]]`
- Handles `Enum`, `bool`, `datetime`, `date`, `Decimal`, `Sequence`, JSON fallback
- `FormValue = str | list[str]` type alias

**`Page[T]`** (`models/pagination.py`):
- Generic model: `items`, `page_number`, `items_number`, `total_pages`, `total_items`, `has_next`
- Supports `__iter__`, `__len__`, `__bool__`

**`NetLicensingResponse`** (`models/response.py`):
Parses the NetLicensing JSON envelope:
```json
{
  "infos": {"info": [{"id": "...", "type": "ERROR", "value": "..."}]},
  "items": {
    "pagenumber": "0", "itemsnumber": "1", "totalpages": "1", "totalitems": "1", "hasnext": "false",
    "item": [{"type": "Product", "property": [{"name": "number", "value": "P-1"}], "list": []}]
  },
  "ttl": 1440
}
```

Key helpers:
- `item_to_dict(item)` — flattens `[{"name": k, "value": v}]` property list into `{"k": v}` dict; also handles nested `list` entries
- `_cast_value(v)` — coerces `"true"`/`"false"`/`"null"` strings and valid JSON strings to native Python
- `model_from_response(payload, model, item_type)` — raises `NetLicensingValidationError` if no matching items
- `page_from_response(payload, model, item_type)` — returns `Page[ModelT]`
- `validation_from_response(payload)` — returns `ValidationResult`

### 5. Services (`services/`)

**`ResourceService[ModelT]`** (`services/base.py`) — generic base for all resource services:

| Method | HTTP | Path |
|---|---|---|
| `get(number)` | GET | `/{endpoint}/{number}` |
| `list(filter, *, params, **query)` | GET | `/{endpoint}` |
| `iterate(filter, ...)` | GET | `/{endpoint}` (yields items, no multi-page) |
| `_create_resource(resource, **props)` | POST | `/{endpoint}` |
| `_update_resource(number, resource, **props)` | POST | `/{endpoint}/{number}` |
| `delete(number, *, force_cascade)` | DELETE | `/{endpoint}/{number}` |

All concrete services call `_create_resource` / `_update_resource` from their `create()` / `update()` methods after mapping Python kwargs to API camelCase field names.

**Service → endpoint → model mapping:**

| `client.` attribute | Endpoint | Model |
|---|---|---|
| `products` | `product` | `Product` |
| `product_modules` | `productmodule` | `ProductModule` |
| `licensees` | `licensee` | `Licensee` |
| `license_templates` | `licensetemplate` | `LicenseTemplate` |
| `licenses` | `license` | `License` |
| `tokens` | `token` | `Token` |
| `transactions` | `transaction` | `Transaction` |
| `payment_methods` | `paymentmethod` | `PaymentMethod` |
| `bundles` | `bundle` | `Bundle` |
| `notifications` | `notification` | `Notification` |
| `utility` | — | various |
| `validation` | — | delegates to `licensees.validate()` |

**Service helpers** (`services/helpers.py`):
- `encode_filter(filter_)` — `{"active": True}` → `"active=True"` (semicolon-separated)
- `merge_payload(resource, **properties)` — calls `resource.to_form()` then merges serialized kwargs
- `clean_params(params, **extra)` — merges dict + kwargs into serialized form dict

---

## Adding a New Service

1. Create `src/netlicensing/services/myresource.py`:
   ```python
   from netlicensing.models import MyModel  # or add to entities.py first
   from netlicensing.services.base import ResourceService

   class MyResourceService(ResourceService[MyModel]):
       endpoint = "myresource"
       item_type = "MyResource"
       model = MyModel

       def create(self, *, number: str | None = None, **props: Any) -> MyModel:
           return self._create_resource(None, number=number, **props)

       def update(self, number: str, **props: Any) -> MyModel:
           return self._update_resource(number, None, **props)
   ```

2. Export from `src/netlicensing/services/__init__.py`.

3. Install in `client.py` `_install_services()`: `self.myresources = MyResourceService(self)`.

4. Export `MyResourceService` + `MyModel` from `src/netlicensing/__init__.py` and add to `__all__`.

5. Add model to `src/netlicensing/models/__init__.py`.

---

## Adding a New Entity Model

Add to `src/netlicensing/models/entities.py`:

```python
class MyEntity(NetLicensingModel):
    active: bool | None = None
    number: str | None = None
    name: str | None = None
    some_field: str | None = Field(default=None, alias="someField")   # camelCase API name

    def to_form(self, *, exclude: set[str] | None = None) -> dict[str, FormValue]:
        # override only if you need to exclude read-only fields or transform values
        return serialize_form(self, exclude=(exclude or set()) | {"read_only_field"})
```

Rules:
- All fields `| None = None` (partial updates are the norm)
- Use `Field(alias="camelCase")` for any API field that differs from the Python name
- `in_use` is always excluded from `to_form()` — it's a read-only computed field
- Enums: subclass `_StrEnum` so `str(enum_value)` gives the raw string

---

## Writing Tests

All tests use `httpx.MockTransport` — **no real network calls**.

### Fixtures (`conftest.py`)

```python
# Build a client wired to a custom handler
def test_something(make_client, requests_seen):
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=envelope("Product", {"number": "P-1"}), request=request)

    client = make_client(handler)
    product = client.products.get("P-1")
    assert product.number == "P-1"
    assert requests_seen[0].method == "GET"
```

### Envelope helpers

```python
# Single-item response
envelope("Product", {"number": "P-1", "active": True})

# Paginated response
page_envelope("Licensee", [{"number": "C-1"}, {"number": "C-2"}])

# Validation response
validation_envelope(valid=True)   # includes one ProductModuleValidation item

# Parse form body sent in a POST
form_body(requests_seen[0])  # -> {"number": "P-1", "active": "true"}
```

### Common patterns

```python
# Test a 4xx error raises NetLicensingHTTPError
with pytest.raises(NetLicensingHTTPError) as exc_info:
    ...
assert exc_info.value.status_code == 404

# Test an auth error
with pytest.raises(NetLicensingAuthError):
    ...

# Test retry behaviour (use retry_backoff=0 in make_client — it already does)
call_count = 0
def handler(request):
    nonlocal call_count
    call_count += 1
    if call_count < 3:
        return httpx.Response(503, request=request)
    return httpx.Response(200, json=envelope(...), request=request)

# Test sleep is called
with unittest.mock.patch("netlicensing.client.time.sleep") as mock_sleep:
    ...
    assert mock_sleep.call_count == 2
```

---

## API Field Name Conventions

NetLicensing REST API uses camelCase in JSON/form bodies. Pydantic aliases map between camelCase (API) and snake_case (Python):

| Python | API |
|---|---|
| `licensee_number` | `licenseeNumber` |
| `product_number` | `productNumber` |
| `product_module_number` | `productModuleNumber` |
| `license_template_number` | `licenseTemplateNumber` |
| `licensee_auto_create` | `licenseeAutoCreate` |
| `marked_for_transfer` | `markedForTransfer` |
| `start_date` | `startDate` |
| `date_created` | `dateCreated` |
| `token_type` | `tokenType` |
| `api_key_role` | `apiKeyRole` |
| `shop_url` | `shopURL` |
| `success_url` | `successURL` |

Always use the Python snake_case name in service method kwargs; these are translated to camelCase when passed to `_create_resource`/`_update_resource`.

---

## Common Gotchas

1. **`to_form()` must exclude read-only fields** — `in_use`, `shop_url`, `vendor_number`, etc. are returned by the API but must not be sent back. Always add them to the `exclude` set.

2. **`model_extra` for custom properties** — NetLicensing supports vendor-defined custom properties. They are stored in `model_extra` after parsing and included in `to_form()` automatically via `extra="allow"`.

3. **`filter` parameter encoding** — `list({"active": True})` serialises the filter as `"active=True"` (Python `True`, not lowercase). This is intentional — the API accepts it. The test `assert requests_seen[1].url.params["filter"] == "active=True"` reflects this.

4. **`Transaction.date_created`/`date_closed` have `AliasChoices`** — the API returns both `dateCreated` and `datecreated` (lowercase) depending on the endpoint. Both are handled.

5. **`Bundle.license_template_numbers` serialises as a comma-joined string** — `"LT-1,LT-2"` not a list, because that's what the API expects. The `to_form()` override handles this.

6. **`Notification.events` serialises as comma-joined string** — same pattern as bundles.

7. **`ValidationParameters.to_form()`** is the most complex serializer — it inlines `licensee_properties` at the top level and emits `productModuleNumber{i}` / `{key}{i}` indexed fields for `product_module_parameters`.

8. **Retry only on idempotent methods** — status-code-based retry (`408`, `429`, `5xx`) applies only to `GET`, `HEAD`, `OPTIONS`. Network/timeout errors retry on all methods.

9. **`_parse_payload()` tries JSON even without `Content-Type: application/json`** — some NetLicensing error responses omit the content type header; the fallback attempt ensures they're still parsed.

10. **`py.typed` must not be deleted** — it's a PEP 561 marker. Without it, mypy reports `Package 'netlicensing' cannot be type checked due to missing py.typed marker`.

---

## CI / GitHub Actions

| Workflow | Trigger | What it does |
|---|---|---|
| `netlicensing-python-ci.yml` | push / PR to master | lint (mypy), test matrix (3.11–3.14), build + twine check, Codecov upload |
| `netlicensing-publish-pypi.yml` | release published | test → build → publish to PyPI via OIDC Trusted Publisher |

All workflows use `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24=true` to silence Node.js 20 deprecation warnings (remove once action versions ship native Node 24 support).

Both workflows require `permissions: contents: read` at the workflow level (CodeQL requirement). The publish job additionally needs `id-token: write` for OIDC.

