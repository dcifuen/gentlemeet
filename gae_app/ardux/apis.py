# -*- coding: utf-8 -*-
import os
import sys
import logging
from api_messages import CheckInOutMessage
import constants

sys.path.insert(1, os.path.join(os.path.abspath('.'), 'lib'))
import endpoints
from protorpc import remote

import uuid
from ardux.models import ResourceDevice, ResourceCalendar, ResourceEvent


@endpoints.api(name='devices', version='v1', description='ResourceDevice API',
               allowed_client_ids=[constants.OAUTH2_CLIENT_ID,
                                   endpoints.API_EXPLORER_CLIENT_ID])
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

    @endpoints.method(CheckInOutMessage, CheckInOutMessage,
                      path='events/checkIn',
                      name='events.checkIn',
                      http_method='POST')
    def check_in(self, request):
        """
        Checks a user in a meeting. If the user is already checked in it
        throws an exception.
        @param request:
        @return: Checkin message @raise endpoints.UnauthorizedException: if
        no OAuth credentials or if there is not a logged in user
        """
        current_user = endpoints.get_current_user()
        if current_user is None:
            raise endpoints.UnauthorizedException(
                'Invalid token. Please authenticate first')
        logging.info('Current user: %s', current_user)
        #Here goes the actual check in logic
        return request