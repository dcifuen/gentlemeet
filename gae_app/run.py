import os
import sys
sys.path.insert(1, os.path.join(os.path.abspath('.'), 'lib'))

from google.appengine.ext import endpoints
from ardux.api import ResourceDeviceApi
from main import app

apis = endpoints.api_server([ResourceDeviceApi], restricted=False)