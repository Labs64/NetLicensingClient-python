# Changelog

## 0.1.0

- Rebuilt the package around a `src/` layout and `pyproject.toml` packaging.
- Added `httpx`-based `NetLicensingClient` with API-key and username/password authentication.
- Added typed Pydantic models for core NetLicensing entities.
- Added services for products, product modules, licensees, license templates, licenses, tokens, transactions, payment methods, bundles, notifications, utility data, and validation.
- Added deterministic pytest coverage using `httpx.MockTransport`.
- Added demo CLI for validation and shop-token flows.
