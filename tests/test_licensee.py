import pytest, json

def test_get_licensee(netlicensing):
    customer_number = 'CUST-001'
    result = netlicensing.get_licensee(customer_number)
    assert customer_number in json.dumps(result)

def test_get_licensee_not_exiting(netlicensing):
    customer_number = 'CUST-NOT-EXITING'
    with pytest.raises(netlicensing.HttpError):
        netlicensing.get_licensee(customer_number)

def test_validate(netlicensing):
    customer_number = 'CUST-11'
    result = netlicensing.validate(customer_number)
    assert 'ProductModuleValidation' in json.dumps(result)
    assert 'true' in json.dumps(result)

def test_validate_not_exiting(netlicensing):
    customer_number = 'CUST-NOT-EXITING'
    with pytest.raises(netlicensing.HttpError):
        netlicensing.validate(customer_number)

def test_delete_not_exiting(netlicensing):
    customer_number = 'CUST-NOT-EXITING'
    with pytest.raises(netlicensing.HttpError):
        netlicensing.delete_licensee(customer_number)

def test_delete_not_exiting_try(netlicensing):
    customer_number = 'CUST-NOT-EXITING'
    try:
        netlicensing.delete_licensee(customer_number)
    except netlicensing.HttpError as e:
        assert e.code == 400
        assert u'' == e.reason
