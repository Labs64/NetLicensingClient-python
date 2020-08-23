from pytest import fixture

from netlicensing import NetLicensing

TEST_API_LEY = '8d4282ba-a331-4b84-9deb-59dbbc75e5df'

def pytest_addoption(parser):
    parser.addoption('--nlic-apikey', default=TEST_API_LEY,
                     help='NetLicensing API Key'
                          '[default: %default]')
                          
@fixture
def netlicensing(request):
    nlic_apikey = request.config.getoption('--nlic-apikey')
    return NetLicensing(nlic_apikey=nlic_apikey)
