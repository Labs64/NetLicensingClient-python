from pytest import fixture

from netlicensing import NetLicensing

TEST_API_LEY = '88178d92-7657-46e9-912b-30066dc9f419'

def pytest_addoption(parser):
    parser.addoption('--nlic-apikey', default=TEST_API_LEY,
                     help='NetLicensing API Key'
                          '[default: %default]')
                          
@fixture
def netlicensing(request):
    nlic_apikey = request.config.getoption('--nlic-apikey')
    return NetLicensing(nlic_apikey=nlic_apikey)
