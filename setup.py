import setuptools
from netlicensing.version import Version


setuptools.setup(name='netlicensing-python-client',
                 version=Version('0.0.1').number,
                 description='Python wrapper for Labs64 NetLicensing RESTful API',
                 long_description=open('README.md').read().strip(),
                 author='Labs64 NetLicensing',
                 author_email='info@netlicensing.io',
                 url='https://github.com/Labs64/NetLicensingClient-python',
                 py_modules=['netlicensing'],
                 install_requires=[],
                 license='Apache-2.0',
                 zip_safe=False,
                 keywords='labs64 netlicensing licensing licensing-as-a-service license license-management software-license client restful restful-api python wrapper api client',
                 classifiers=['Package', 'Wrapper', 'Client', 'API'])
