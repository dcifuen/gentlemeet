# -*- coding: utf-8 -*-
import os
import sys
from endpoints.api_exceptions import NotFoundException
import logging

sys.path.insert(1, os.path.join(os.path.abspath('.'), 'lib'))
import endpoints
from protorpc import remote
from protorpc import messages
import uuid
from ardux.models import ResourceDevice, ResourceCalendar, ResourceEvent


class String(messages.Message):
    value = messages.StringField(1)

class StringList(messages.Message):
    items = messages.MessageField(String, 1, repeated=True)

@endpoints.api(name='devices', version='v1', description='ResourceDevice API')
class ResourceDeviceApi(remote.Service):

    @ResourceDevice.method(path='device',
                        http_method='POST',
                        name='device.insert')
    def ResourceDeviceInsert(self, device):
        if device.uuid is None:
            device.uuid = str(uuid.uuid1())
        device.put()
        return device

    @ResourceDevice.method(path='device/{uuid_query}',
                        http_method='GET',
                        name='device.get')
    def ResourceDeviceGet(self, device):
        logging.info(device.to_dict())
        return device

    @ResourceDevice.method(path='device/{uuid_query}',
                        http_method='PUT',
                        request_fields=('name', 'resource_id'),
                        name='device.update')
    def ResourceDeviceUpdate(self, device):
        device.put()
        return device

    @ResourceDevice.query_method(query_fields=('limit', 'order', 'pageToken'),
                          path='devices',
                          name='devices.list')
    def ResourceDeviceList(self, query):
        return query

    @ResourceCalendar.query_method(query_fields=('limit', 'order', 'pageToken'),
                          path='resources',
                          name='resources.list')
    def CalendarResourceList(self, query):
        return query

    @ResourceEvent.query_method(query_fields=('limit', 'order', 'pageToken', 'resource_id'),
                          path='events',
                          name='events.list')
    def CalendarEventList(self, query):
        return query