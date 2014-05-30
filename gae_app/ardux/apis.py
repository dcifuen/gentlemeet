# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import logging
import uuid

import endpoints
from protorpc import remote
from google.appengine.ext import ndb

from api_messages import CheckInOutMessage, ID_RESOURCE, EventsResponseMessage, \
    EventMessage, event_db_to_rcp
import constants
from ardux.models import ResourceDevice, ResourceCalendar, ResourceEvent, \
    CheckInOut, store_check_in
from helpers import CalendarHelper
from models import Client


@endpoints.api(name='gentlemeet', version='v1',
               documentation='http://docs.gentlemeet.com',
               title='GentleMeet API',
               description='Backend API for managing rooms and meetings with '
                           'GentleMeet',
               allowed_client_ids=[constants.OAUTH2_CLIENT_ID,
                                   constants.OAUTH2_ANDROID_CLIENT_ID,
                                   endpoints.API_EXPLORER_CLIENT_ID],
               audiences=[constants.OAUTH2_CLIENT_ID])
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

    @endpoints.method(ID_RESOURCE, CheckInOutMessage,
                      path='events/{id}/checkIn',
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
        now = datetime.now()

        if event.actual_end_date_time and event.actual_end_date_time < now:
            raise endpoints.BadRequestException(
                'The event has already finished')

        if (not event.actual_start_date_time and event.state == constants
                .STATE_SCHEDULED):
            if (event.original_start_date_time < now or
                            event.original_start_date_time - timedelta(
                                minutes=constants.EARLY_CHECK_IN_MINUTES) < now):
                # Event should be marked as started
                event.actual_start_date_time = now
                event.state = constants.STATE_IN_PROGRESS
            else:
                raise endpoints.BadRequestException(
                    'The event has not started')

        # Here goes the actual check in logic
        store_check_in(event, current_user.email())

        return CheckInOutMessage(userEmail=current_user.email())


    @endpoints.method(ID_RESOURCE, CheckInOutMessage,
                      path='event/{id}/checkOut',
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

        if CheckInOut.already_checked(constants.CHECK_OUT, current_user.email(),
                                      event):
            raise endpoints.BadRequestException(
                'User have already checked out')

        if not CheckInOut.checked_in_before(current_user.email(), event,
                                            datetime.now()):
            raise endpoints.BadRequestException(
                'The user did not checked in or checked in the future')

        CheckInOut(parent=event.key, attendee=current_user.email(),
                   type=constants.CHECK_OUT).put()

        return CheckInOutMessage(userEmail=current_user.email())

    @endpoints.method(ID_RESOURCE, EventMessage,
                      path='event/{id}/finish',
                      name='event.finish',
                      http_method='POST')
    def finish_event(self, request):
        """
        Mark an event as finished and set the actual end time as right now.
        """
        logging.info('Someone just marked event ID [%s] as finished',
                     request.id)

        event = ResourceEvent.get_by_id(request.id)
        if not event:
            raise endpoints.BadRequestException(
                'Unable to find event with id %s' % request.id)

        event.state = constants.STATE_FINISHED
        event.actual_end_date_time = datetime.now()
        event.put()
        return event_db_to_rcp(event)


    @endpoints.method(ID_RESOURCE, EventsResponseMessage,
                      path='resource/{id}/events/today',
                      name='resource.nextEventsToday',
                      http_method='GET')
    def next_events_today(self, request):
        """
        Retrieves the list of events that are taking place in a resource during
        the day. If the resource doesn't exists throws an exception.
        """
        logging.info('Getting daily events for resource ID: [%s]',
                     request.id)

        resource = ResourceCalendar.get_by_id(request.id)
        if not resource:
            raise endpoints.BadRequestException(
                'Unable to find resource with id %s' % request.id)

        items = []
        for resource_event in resource.get_next_events_today():
            items.append(event_db_to_rcp(resource_event))
        return EventsResponseMessage(items=items)


    @endpoints.method(ID_RESOURCE, EventMessage,
                      path='resource/{id}/events/current',
                      name='resource.eventCurrent',
                      http_method='GET')
    def current_event(self, request):
        """
        Retrieves the current event that is taking place at this moment in the
        resource. If the resource doesn't exists throws an exception. If
        calendar access is not granted throws an exception.
        """
        logging.info('Getting the current event happening in resource ID: [%s]',
                     request.id)

        resource = ResourceCalendar.get_by_id(request.id)
        if not resource:
            raise endpoints.BadRequestException(
                'Unable to find resource with id %s' % request.id)

        resource_event = resource.get_current_event()
        if not resource_event:
            raise endpoints.BadRequestException(
                'There is no event happening at the resource now')
        return event_db_to_rcp(resource_event)


    @endpoints.method(ID_RESOURCE, EventMessage,
                      path='resource/{id}/events/quickAdd',
                      name='resource.quickAdd',
                      http_method='POST')
    def book_resource(self, request):
        """
        Let an anonymous user book a resource in the moment, create a calendar
        event and checks the user in. If the resource doesn't exists throws an
        exception. If there is an event happening throws an exception.
        """
        logging.info('Someone is creating a quick event at [%s]',
                     request.id)
        resource = ResourceCalendar.get_by_id(request.id)
        if not resource:
            raise endpoints.BadRequestException(
                'Unable to find resource with id %s' % request.id)

        if not resource.will_be_available(constants.QUICK_ADD_MINUTES):
            raise endpoints.BadRequestException(
                'There is an event happening at the resource')

        now = datetime.now()
        end_time = now + timedelta(minutes=constants.QUICK_ADD_MINUTES)

        # Create event in Google Calendar
        client = Client.get_by_id(1)
        if not client or not client.credentials or not client.refresh_token:
            raise endpoints.BadRequestException(
                'Domain calendar access is not yet configured')

        calendar_helper = CalendarHelper(
            client.credentials, client.refresh_token
        )
        calendar_event = calendar_helper.insert_or_update_event(
            calendar_id=resource.email, summary=constants.QUICK_ADD_TITLE,
            description=constants.QUICK_ADD_DESCRIPTION, start_date=now,
            end_date=end_time,
            location=resource.name
        )
        # Save in datastore
        resource_event = ResourceEvent(
            organizer=client.installer_user,
            original_start_date_time=now,
            original_end_date_time=end_time,
            actual_start_date_time=now,
            resource_key=resource.key,
            title=constants.QUICK_ADD_TITLE,
            is_express=True,
            state=constants.STATE_IN_PROGRESS,
        )
        resource_event.UpdateFromKey(ndb.Key(ResourceEvent, calendar_event[
            'id']))
        resource_event.put()
        return event_db_to_rcp(resource_event)