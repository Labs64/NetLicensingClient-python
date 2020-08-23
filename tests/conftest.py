from pytest import fixture

from netlicensing import NetLicensing

# APIKey role: at least 'ROLE_APIKEY_ANALYTICS'; see https://netlicensing.io/wiki/security#api-key-identification
TEST_API_LEY = '85396d4e-13a0-405c-b5a5-cb207c1617ae'

def pytest_addoption(parser):
    parser.addoption('--nlic-apikey', default=TEST_API_LEY,
                     help='NetLicensing API Key'
                          '[default: %default]')
                          
@fixture
def netlicensing(request):
    nlic_apikey = request.config.getoption('--nlic-apikey')
    return NetLicensing(nlic_apikey=nlic_apikey)
