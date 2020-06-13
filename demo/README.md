# NetLicensing Python Demo

Set credentials with environment variables:

```bash
export NETLICENSING_API_KEY="..."
export NETLICENSING_VENDOR_NUMBER="..."
export NETLICENSING_BASE_URL="https://go.netlicensing.io/core/v2/rest"
```

For the public NetLicensing demo vendor, use username/password authentication:

```bash
export NETLICENSING_USERNAME="demo"
export NETLICENSING_PASSWORD="demo"
```

Validate a licensee:

```bash
python demo/app.py validate CUSTOMER-1 --product-number PRODUCT-1 --module MODULE-1 --node-secret machine-id
```

Create a NetLicensing Shop token:

```bash
python demo/app.py shop-token CUSTOMER-1 --product-number PRODUCT-1
```

The demo prints the validation result or the generated `shopURL`.
