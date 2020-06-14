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

## Test

Testing is set up using [pytest](http://pytest.org) and coverage is handled with the pytest-cov plugin.

Run your tests with ```py.test``` in the root directory and please make sure all tests pass.

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