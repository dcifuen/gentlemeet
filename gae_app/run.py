import os
import sys
sys.path.insert(1, os.path.join(os.path.abspath('.'), 'lib'))
from google.appengine.ext import endpoints
from google.appengine.ext.webapp.util import run_wsgi_app
from main import app
from main import deferred_app
from ardux.apis import ResourceDeviceApi
api = endpoints.api_server([ResourceDeviceApi], restricted=False,)


