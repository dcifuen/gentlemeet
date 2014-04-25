import endpoints
from apps.test.models import Test
from settings import ENDPOINTS_AUTH_CONFIG
from webengine.sevices import AuthRemoteService
from protorpc import remote


@endpoints.api(name='testApi',
               version='v1',
               description='testApi Endpoint',
               auth=ENDPOINTS_AUTH_CONFIG)
class TestApi(remote.Service, AuthRemoteService):
    pass

