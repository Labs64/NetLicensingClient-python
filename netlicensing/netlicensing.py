import json
import requests

__all__ = ['NLIC_API_URL', 'NetLicensing']

NLIC_API_URL = 'https://go.netlicensing.io/core/v2/rest/'

class NetLicensing:
    def __init__(self, imp_url=NLIC_API_URL):
        self.imp_url = imp_url
        requests_session = requests.Session()
        requests_adapters = requests.adapters.HTTPAdapter(max_retries=3)
        requests_session.mount('https://', requests_adapters)
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
        if response.status_code != requests.codes.ok:
            raise NetLicensing.HttpError(response.status_code, response.reason)
        result = response.json()
        if result['code'] != 0:
            raise NetLicensing.ResponseError(
                result.get('code'), result.get('message')
            )
        return result.get('response')

    def get_headers(self):
        return {'Accept': 'application/json'}

    def _post(self, url, payload=None):
        headers = self.get_headers()
        response = self.requests_session.post(url, headers=headers, data=payload)
        return self.get_response(response)

    def validate(self, licensee_uid):
        url = f'{self.imp_url}licensee/{licensee_uid}/validate'
        payload = {'licensee_uid': licensee_uid, 'amount': licensee_uid}
        return self._post(url, payload)
