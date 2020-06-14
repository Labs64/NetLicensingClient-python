from pytest import fixture

from netlicensing import NetLicensing

@fixture
def netlicensing(request):
    return NetLicensing()
