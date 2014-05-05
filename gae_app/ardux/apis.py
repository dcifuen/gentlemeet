# -*- coding: utf-8 -*-
from datetime import datetime
import logging
import uuid

import endpoints
from protorpc import remote

from api_messages import CheckInOutMessage, ID_RESOURCE
import constants
from ardux.models import ResourceDevice, ResourceCalendar, ResourceEvent, \
    CheckInOut, store_check_in


@endpoints.api(name='gentlemeet', version='v1',
               description='GentleMeet API',
               allowed_client_ids=[constants.OAUTH2_CLIENT_ID,
                                   endpoints.API_EXPLORER_CLIENT_ID])
class GentleMeetApi(remote.Service):
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

    @ResourceEvent.query_method(query_fields=('limit', 'order', 'pageToken',
                                              'resource_id'),
                                path='events',
                                name='events.list')
    def CalendarEventList(self, query):
        return query

    @endpoints.method(ID_RESOURCE, CheckInOutMessage,
                      path='events/{id}/checkin',
                      name='events.checkIn',
                      http_method='POST')
    def check_in(self, request):
        """
        Checks a user in a meeting. If there is not a logged in user throws an
        exception. If the event doesn't exists throws an exception. If the user
        is already checked in throws an exception.
        """
        current_user = endpoints.get_current_user()
        if current_user is None:
            raise endpoints.UnauthorizedException(
                'Invalid token. Please authenticate first')
        logging.info('Checking in user: [%s] event ID: [%s]',
                     current_user.email(), request.id)
        event = ResourceEvent.get_by_id(request.id)
        if not event:
            raise endpoints.BadRequestException(
                'Unable to find event with id %s' % request.id)

        if CheckInOut.already_checked(constants.CHECK_IN, current_user.email(),
                                      event):
            raise endpoints.BadRequestException(
                'User have already checked in')

        # Check time stuff
        now = datetime.datetime.now()

        if event.actual_end_date_time and event.actual_end_date_time < now:
            raise endpoints.BadRequestException(
                'The event has already finished')

        if (not event.actual_start_date_time and event.state == constants
                .STATE_SCHEDULED):
            if (event.original_start_date_time < now or
                event.original_start_date_time - datetime.timedelta(
                    minutes=constants.EARLY_CHECK_IN_MINUTES) < now):
                #Event should be marked as started
                event.actual_start_date_time = now
                event.state = constants.STATE_IN_PROGRESS
            else:
                raise endpoints.BadRequestException(
                    'The event has not started')

            # Here goes the actual check in logic
            store_check_in(event, current_user.email())

            return CheckInOutMessage(userEmail=current_user.email())


        @endpoints.method(ID_RESOURCE, CheckInOutMessage,
                          path='event/{id}/checkout',
                          name='event.checkOut',
                          http_method='POST')
        def check_out(self, request):
            """
            Checks a user out of a meeting. If there is not a logged in user
            throws an exception. If the event doesn't exists throws an exception. If
            the user has already checked out throws an exception. If the user hasn't
            checked in throws an exception.
            """
            current_user = endpoints.get_current_user()
            if current_user is None:
                raise endpoints.UnauthorizedException(
                    'Invalid token. Please authenticate first')

            logging.info('Checking out user: [%s] event ID: [%s]',
                         current_user, request.id)

            event = ResourceEvent.get_by_id(request.id)
            if not event:
                raise endpoints.BadRequestException(
                    'Unable to find event with id %s' % request.id)

            if CheckInOut.already_checked(constants.CHECK_OUT, current_user
                    .email(), event):
                raise endpoints.BadRequestException(
                    'User have already checked out')

            if not CheckInOut.checked_in_before(current_user.email(), event,
                                                datetime.datetime.now()):
                raise endpoints.BadRequestException(
                    'The user did not checked in or checked in the future')

            # TODO: Check if the event should be marked as finished

            CheckInOut(parent=event.key, attendee=current_user.email(),
                       type=constants.CHECK_OUT).put()

            return CheckInOutMessage(userEmail=current_user.email())