# -*- coding: utf-8 -*-
import os
import sys
sys.path.insert(1, os.path.join(os.path.abspath('.'), 'lib'))
import endpoints
from protorpc import remote
from protorpc import messages
import uuid
from ardux.models import ResourceDevice

class String(messages.Message):
    value = messages.StringField(1)

class StringList(messages.Message):
    items = messages.MessageField(String, 1, repeated=True)

@endpoints.api(name='devices', version='v1', description='Eforcers ResourceDevice API')
class ResourceDeviceApi(remote.Service):

    @ResourceDevice.method(path='device/register',
                        http_method='POST',
                        name='device.register')
    def ResourceDeviceRegister(self, device):
        if device.uuid is None:
            device.uuid = str(uuid.uuid1())
        #device.put()
        return device


    @ResourceDevice.method(path='device',
                        http_method='POST',
                        name='device.insert')
    def ResourceDeviceInsert(self, device):
        if device.uuid is None:
            device.uuid = str(uuid.uuid1())
        device.put()
        return device

    @ResourceDevice.query_method(query_fields=('limit', 'order', 'pageToken'),
                          path='devices',
                          name='devices.list')
    def ResourceDeviceList(self, query):
        return query