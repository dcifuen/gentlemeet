from protorpc import remote
from google.appengine.ext import endpoints
from ardux.models import ResourceDevice
import uuid

@endpoints.api(name='devices', version='v1', description='Eforcers ResourceDevice API')
class ResourceDeviceApi(remote.Service):

    @ResourceDevice.method(path='device',
                        http_method='POST',
                        name='device.insert')
    def ResourceDeviceInsert(self, device):
        if device.uuid is None:
            device.uuid = str(uuid.uuid1())
        device.put()
        return device

    @ResourceDevice.query_method(query_fields=('limit', 'order', 'pageToken'),
                          path='device',
                          name='device.list')
    def ResourceDeviceList(self, query):
        return query


application = endpoints.api_server([ResourceDeviceApi], restricted=False)