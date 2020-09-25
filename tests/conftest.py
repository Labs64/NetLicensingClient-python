from pytest import fixture

from netlicensing import NetLicensing

TEST_API_KEY = 'ebe1dbfb-cefd-42ba-abec-a2fe0b15487b'

def pytest_addoption(parser):
    parser.addoption('--nlic-apikey', default=TEST_API_KEY,
                     help='NetLicensing API Key'
                          '[default: %default]')
                          
@fixture
def netlicensing(request):
    nlic_apikey = request.config.getoption('--nlic-apikey')
    return NetLicensing(nlic_apikey=nlic_apikey)
