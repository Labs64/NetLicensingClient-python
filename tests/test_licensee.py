import pytest, json

def test_get_licensee(netlicensing):
    customer_number = 'CUST-001'
    result = netlicensing.get_licensee(customer_number)
    assert customer_number in json.dumps(result)

def test_validate(netlicensing):
    customer_number = 'CUST-11'
    result = netlicensing.validate(customer_number)
    assert 'ProductModuleValidation' in json.dumps(result)
    assert 'true' in json.dumps(result)
