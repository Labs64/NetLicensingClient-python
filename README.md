**WARNING:** Package status: "work-in-progress" - stay tuned at [NetLicensing #changelog](https://netlicensing.io/wiki/changelog) for the latest NetLicensing news.

<a href="https://netlicensing.io"><img src="https://netlicensing.io/img/netlicensing-stage-twitter.jpg" alt="Innovative License Management Solution"></a>

# [Labs64 NetLicensing](https://netlicensing.io) Client (Python)

[![CI Status](https://github.com/Labs64/NetLicensingClient-python/workflows/Test%20Python%20Package/badge.svg)](https://github.com/Labs64/NetLicensingClient-python/actions?query=workflow%3A%22Test+Python+Package%22)
[![PyPI](https://img.shields.io/pypi/v/netlicensing-python-client.svg)](https://pypi.org/project/netlicensing-python-client/)
[![PyVer](https://img.shields.io/pypi/pyversions/netlicensing-python-client.svg)](https://pypi.org/project/netlicensing-python-client)
[![Docs](https://img.shields.io/readthedocs/netlicensing-python-client)](https://netlicensing-python-client.readthedocs.io)
[![Requires.io](https://requires.io/github/mtchavez/NetLicensingClient-python/requirements.svg?branch=master)](https://requires.io/github/mtchavez/NetLicensingClient-python/requirements?branch=master)
[![Codecov](https://img.shields.io/codecov/c/github/pypa/twine)](https://codecov.io/gh/pypa/twine)


Python wrapper for Labs64 NetLicensing [RESTful API](http://l64.cc/nl10)

Visit Labs64 NetLicensing at https://netlicensing.io

## Install

The NetLicensing python package can be installed by executing:

```bash
pip install netlicensing
```

Alternatively, you can install the latest development version directly from GitHub via:

```bash
pip install -e git+https://github.com/Labs64/NetLicensingClient-python#egg=netlicensing
```

## Test

Testing is set up using [pytest](http://pytest.org) and coverage is handled with the pytest-cov plugin.

Run your tests with ```py.test``` in the root directory.

Coverage is ran by default and is set in the ```pytest.ini``` file.
To see an html output of coverage open ```htmlcov/index.html``` after running the tests.

## Release

Install [Twine](https://twine.readthedocs.io):

```bash
pip install twine
```

Create distributions:

```bash
python setup.py sdist bdist_wheel
```

Upload to TestPyPI/PyPI:

```bash
# Test PyPi
twine upload -r testpypi dist/*
# PyPi
twine upload dist/*
```

## How to Contribute

Everyone is welcome to contribute to this project!
Once you're done with your changes send a pull request and check [CI Status](https://github.com/Labs64/NetLicensingClient-python/actions).
Thanks!

## Bugs and Feedback

For bugs, questions and discussions please use the [GitHub Issues](https://github.com/Labs64/NetLicensingClient-python/issues).

## License

This boilerplate is open-sourced software licensed under the [Apache License Version 2.0](LICENSE).

---

Visit Labs64 NetLicensing at https://netlicensing.io
