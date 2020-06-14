**WARNING:** Package status: "work-in-progress" - stay tuned at NetLicensing [#changelog](https://netlicensing.io/wiki/changelog) for the latest NetLicensing news.

---

<a href="https://netlicensing.io"><img src="https://netlicensing.io/img/netlicensing-stage-twitter.jpg" alt="Innovative License Management Solution"></a>

# [Labs64 NetLicensing](https://netlicensing.io) Client (Python)

[![CI Status](https://github.com/Labs64/NetLicensingClient-python/workflows/Python%20Client%20CI/badge.svg)](https://github.com/Labs64/NetLicensingClient-python/actions?query=workflow%3A%22Python+Client+CI%22)
[![PyPI](https://img.shields.io/pypi/v/netlicensing-client.svg)](https://pypi.org/project/netlicensing-client/)
[![PyVer](https://img.shields.io/pypi/pyversions/netlicensing-client.svg)](https://pypi.org/project/netlicensing-client)
[![codecov](https://codecov.io/gh/Labs64/NetLicensingClient-python/branch/master/graph/badge.svg)](https://codecov.io/gh/Labs64/NetLicensingClient-python)


Python wrapper for Labs64 NetLicensing [RESTful API](http://l64.cc/nl10)

Visit Labs64 NetLicensing at https://netlicensing.io

## Install

The NetLicensing python package can be installed by executing:

```bash
pip install netlicensing-client
```

Alternatively, you can install the latest development version directly from GitHub via:

```bash
pip install -e git+https://github.com/Labs64/NetLicensingClient-python#egg=netlicensing
```

## How to Use

To access NetLicensing RESTful API services a valid vendor account is needed.
The recommended way to access API services is *'API Key'*.
API Key can be obtained via the NetLicensing [Management Console](https://ui.netlicensing.io/#/settings).

Depending on API services different [API Key Role](https://netlicensing.io/wiki/security#api-key-identification) needs to be used.

```python
from netlicensing import NetLicensing

# sample variables need to be replaced using yours
API_KEY = '2f8459a9-08dc-4d70-882a-1bc27d1ae9a8'
CUSTOMER_NUMBER = 'CUST-11'

nlic = NetLicensing(API_KEY)
response = nlic.validate(CUSTOMER_NUMBER)

print(response)
```

## How to Contribute

Everyone is welcome to [contribute](CONTRIBUTING.md) to this project!
Once you're done with your changes send a pull request and check [CI Status](https://github.com/Labs64/NetLicensingClient-python/actions).
Thanks!

## Bugs and Feedback

For bugs, questions and discussions please use the [GitHub Issues](https://github.com/Labs64/NetLicensingClient-python/issues).

## License

This boilerplate is open-sourced software licensed under the [Apache License Version 2.0](LICENSE).

---

Visit Labs64 NetLicensing at https://netlicensing.io
