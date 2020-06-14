import pytest

def test_about(netlicensing):
    about_text = netlicensing.about()
    assert u'LaaS' in about_text
