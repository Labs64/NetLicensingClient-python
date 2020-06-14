import json
import requests

__all__ = ['NLIC_API_URL', 'NetLicensing']

NLIC_API_URL = 'https://go.netlicensing.io/core/v2/rest/'

class NetLicensing:
    def __init__(self, nlic_apikey, nlic_baseurl=NLIC_API_URL):
        self.nlic_apikey = nlic_apikey
        self.nlic_baseurl = nlic_baseurl

        # https://requests.readthedocs.io/en/master/user/advanced/
        requests_session = requests.Session()
        requests_adapters = requests.adapters.HTTPAdapter(max_retries=3)
        requests_session.mount('https://', requests_adapters)
        # https://netlicensing.io/wiki/security#api-key-identification
        requests_session.auth = ('apiKey', self.nlic_apikey)
        requests_session.headers.update({'Accept': 'application/json'})
        self.requests_session = requests_session

    def about(self):
        return (u'Labs64 NetLicensing is a first-class solution in the Licensing-as-a-Service (LaaS) sector.'
                u'Based on open standards, it provides a cost-effective, integrated and scalable platform for software vendors and developers'
                u'who want to concentrate on their product’s core functionality instead of spending resources on developing an own license management software.')

    class ResponseError(Exception):
        def __init__(self, code=None, message=None):
            self.code = code
            self.message = message

    class HttpError(Exception):
        def __init__(self, code=None, reason=None):
            self.code = code
            self.reason = reason

    @staticmethod
    def get_response(response):
        verbose = False
        if verbose:
            print('NetLicensing response:')
            print(response.url)
            print(response.headers)
            print(response.status_code)
            print(response.elapsed)

        if response.status_code != requests.codes.ok:
            raise NetLicensing.HttpError(response.status_code, response.reason)
        result = response.json()

        return result

    def _get(self, url, payload=None):
        response = self.requests_session.get(url, params=payload)
        return self.get_response(response)

    def _post(self, url, payload=None):
        response = self.requests_session.post(url, headers={'Content-Type': 'application/x-www-form-urlencoded'}, data=payload)
        return self.get_response(response)

    def _delete(self, url, payload=None):
        response = self.requests_session.delete(url, data=payload)
        return self.get_response(response)

    def validate(self, licensee_number):
        url = f'{self.nlic_baseurl}licensee/{licensee_number}/validate'
        return self._post(url)

    def get_licensee(self, licensee_number):
        url = f'{self.nlic_baseurl}licensee/{licensee_number}'
        return self._get(url)

    def delete_licensee(self, licensee_number):
        url = f'{self.nlic_baseurl}licensee/{licensee_number}'
        return self._delete(url)
