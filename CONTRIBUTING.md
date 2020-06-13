# Contributing

## Add features or fix bugs

* Fork the repo
* Check out a feature or bug branch
* Add your changes
* Update README when needed
* Submit a pull request to upstream repo
* Add description of your changes
* Ensure tests are passing
* Ensure branch is mergeable

## Setup

```bash
pip install -e ".[dev]"
```

## Test

Testing is set up using [pytest](http://pytest.org) and coverage is handled with the pytest-cov plugin.

Run your tests with:

```bash
pytest
```

Coverage is reported in the terminal after each run.
To view a detailed HTML report open `htmlcov/index.html` after running the tests.

To run the optional live integration tests against the NetLicensing demo account:

```bash
NETLICENSING_LIVE_DEMO=1 pytest tests/test_live_demo.py -q
```

## Type checking

```bash
mypy src/netlicensing
```

## Release

Create a source distribution and wheel:

```bash
python -m build
```

Verify the distribution before uploading:

```bash
twine check dist/*
```

Upload to TestPyPI first, then PyPI:

```bash
# Test PyPI
twine upload -r testpypi dist/*
# PyPI
twine upload dist/*
```