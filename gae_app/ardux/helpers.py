# -*- coding: utf-8 -*-
# vim: set fileencoding=utf-8

import logging

import httplib2

from gdata.calendar_resource.client import CalendarResourceClient
import gdata
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.client import Credentials
from apiclient.discovery import build
from ardux import app
import constants


class OAuthDanceHelper:
    """ OAuth dance helper class"""
    flow = None

    def __init__(self, redirect_uri='', approval_prompt='auto',
                 scope=None):
        scope = constants.OAUTH2_SCOPE
        self.flow = OAuth2WebServerFlow(
            client_id=constants.OAUTH2_CLIENT_ID,
            client_secret=app.config.get(
                'OAUTH2_CLIENT_SECRET'),
            scope=scope,
            redirect_uri=redirect_uri,
            approval_prompt=approval_prompt)

    def step1_get_authorize_url(self):
        return self.flow.step1_get_authorize_url()

    def step2_exchange(self, code):
        return self.flow.step2_exchange(code)

    def get_credentials(self, credentials_json):
        return Credentials.new_from_json(credentials_json)


class OAuthServiceHelper:
    """ OAuth services base helper class"""
    credentials = None
    service = None

    def __init__(self, credentials_json, refresh_token=None):
        oOAuthHelper = OAuthDanceHelper()
        self.credentials = oOAuthHelper.get_credentials(credentials_json)
        if refresh_token and self.credentials.refresh_token is None:
            self.credentials.refresh_token = refresh_token
        self.http = self.credentials.authorize(httplib2.Http())


class CalendarResourceHelper(OAuthServiceHelper):
    def __init__(self, credentials_json, refresh_token=None, domain=None):
        OAuthServiceHelper.__init__(self, credentials_json, refresh_token)
        auth2token = gdata.gauth.OAuth2TokenFromCredentials(self.credentials)
        self.client = CalendarResourceClient(
            domain=domain, auth_token=self.credentials.access_token)
        self.client = auth2token.authorize(self.client)

    def get_all_resources(self):
        return self.client.GetResourceFeed().entry


class CalendarHelper(OAuthServiceHelper):
    """ Google Calendar API helper class"""

    def __init__(self, credentials_json, refresh_token=None):
        OAuthServiceHelper.__init__(self, credentials_json, refresh_token)
        self.service = build('calendar', 'v3', http=self.http)


    def delete_calentar_event(self, calendar_id, envent_id):
        self.service.events().delete(
            calendarId=calendar_id,
            eventId=envent_id,
            sendNotifications=True,
        ).execute()

    def add_event_attendees(self, calendar_id, envent_id, attendees=list()):
        event = {'id': envent_id}
        attendees_list = [{'email': attendee} for attendee in attendees]
        event.update({'attendees': attendees_list})
        return self.service.events().update(calendarId=calendar_id,
                                            eventId=event['id'],
                                            body=event).execute()

    def insert_or_update_event(self, calendar_id, summary=None, start_date=None,
                               end_date=None, description=None, location=None,
                               attendees=list(), event_id=None):
        if event_id:
            event = self.service.events().get(calendarId=calendar_id,
                                              eventId=event_id).execute()
        else:
            event = {}

        attendees_list = [{'email': attendee} for attendee in attendees]
        if description:
            event.update({'description': description})
        if location:
            event.update({'location': location})
        if len(attendees_list) > 0 :
            event.update({'attendees': attendees_list})
        if start_date:
            event.update({'start': {
                'dateTime': start_date.strftime(constants.CALENDAR_DATE_TIME),
                'timeZone': "UTC"}})
        if end_date:
            event.update({
                'end': {'dateTime': end_date.strftime(constants.CALENDAR_DATE_TIME),
                        'timeZone': "UTC"}})
        if summary:
            event.update({'summary': summary})
        if event_id:
            return self.service.events().update(calendarId=calendar_id,
                                                sendNotifications=True,
                                                eventId=event_id,
                                                body=event).execute()
        else:
            return self.service.events().insert(calendarId=calendar_id,
                                                sendNotifications=True,
                                                body=event).execute()

    def is_calendar_available(self, calendar_id, start_date, end_date):
        response = self.service.freebusy().query(
            body={'timeMin': start_date.strftime(constants.CALENDAR_DATE_TIME),
                  'timeMax': end_date.strftime(constants.CALENDAR_DATE_TIME),
                  'items': [{'id': calendar_id}]
            }).execute()
        return len(response['calendars'][calendar_id]['busy']) == 0

    def get_event(self, calendar_id, even_id):
        return self.service.events().get(calendarId=calendar_id,
                                         eventId=even_id).execute()

    def list_events(self, calendar_id, **kwargs):
        events = []
        page_token = None
        # TODO: Pagination the right way
        while True:
            if page_token:
                tem_events = self.service.events().list(
                    calendarId=calendar_id,
                    pageToken=page_token,
                    **kwargs).execute()
            else:
                tem_events = self.service.events().list(
                    calendarId=calendar_id,
                    **kwargs).execute()
            events.extend(tem_events['items'])
            page_token = tem_events.get('nextPageToken')
            if not page_token:
                break

        return events

    def clear_calendar(self, calendar_id):
        events = self.list_events(calendar_id)
        logging.info("Deleting all calendar events")
        for event in events:
            self.delete_calentar_event(calendar_id, event['id'])

