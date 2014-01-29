#-*- coding: utf-8 -*-
# vim: set fileencoding=utf-8

import logging
from xml.dom.minidom import Document, Element
from gdata.calendar_resource.client import CalendarResourceClient
import gdata
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.client import Credentials
from suds.client import Client
from suds.transport.http import HttpAuthenticated
from apiclient.discovery import build
from settings import get_setting
import pytz
from pytz import timezone

import httplib2

class OAuthDanceHelper:
    """ OAuth dance helper class"""
    flow = None

    def __init__(self, redirect_uri='', approval_prompt='auto',
                 scope=None):
        scope = get_setting('OAUTH2_SCOPE')
        self.flow = OAuth2WebServerFlow(
            client_id=get_setting('OAUTH2_CLIENT_ID'),
            client_secret=get_setting(
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

    def __init__(self, credentials_json, refresh_token = None):
        oOAuthHelper = OAuthDanceHelper()
        self.credentials = oOAuthHelper.get_credentials(credentials_json)
        if refresh_token and self.credentials.refresh_token is None:
            self.credentials.refresh_token = refresh_token
        self.http = self.credentials.authorize(httplib2.Http())

class CalendarResourceHelper(OAuthServiceHelper):
    def __init__(self, credentials_json, refresh_token = None, domain = None):
        OAuthServiceHelper.__init__(self, credentials_json, refresh_token)
        auth2token = gdata.gauth.OAuth2TokenFromCredentials(self.credentials)
        self.client = CalendarResourceClient(domain=domain, auth_token=self.credentials.access_token)
        self.client = auth2token.authorize(self.client)

    def get_all_resources(self):
        return self.client.GetResourceFeed()

class CalendarHelper(OAuthServiceHelper):
    """ Google Calendar API helper class"""

    def __init__(self, credentials_json, refresh_token = None):
        OAuthServiceHelper.__init__(self, credentials_json, refresh_token)
        self.service = build('calendar', 'v3', http=self.http)


    def delete_calentar_event(self,calendar_id, envent_id):
        self.service.events().delete(
            calendarId=calendar_id,
            eventId=envent_id,
            sendNotifications=True,
        ).execute()

    def add_event_attendees(self, calendar_id, envent_id, attendees = []):
        event = {'id':envent_id}
        attendees_list = [{'email':attendee} for attendee in attendees]
        event.update({'attendees':attendees_list})
        return self.service.events().update(calendarId=calendar_id, eventId=event['id'], body=event).execute()

    def update_calendar_event(self,calendar_id, envent_id, summary, start_date, end_date):
        event = {'id':envent_id}
        event.update({'start':{'dateTime':start_date.strftime(get_setting(
            'CALENDAR_DATE_FORMAT')),
                               'timeZone': "UTC"}})
        event.update({'end':{'dateTime':end_date.strftime(get_setting(
            'CALENDAR_DATE_FORMAT')),
                             'timeZone': "UTC"}})
        event.update({'summary':summary})
        return self.service.events().update(calendarId=calendar_id, eventId=event['id'], body=event).execute()


    def insert_or_update_event(self, calendar_id, summary, start_date,
                               end_date, description=None, location=None,
                               attendees=[], event_id=None):
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
        event.update({'attendees': attendees_list})
        event.update({'start': {'dateTime':start_date.strftime(get_setting(
            'CALENDAR_DATE_FORMAT'))}})
        event.update({'end': {'dateTime':end_date.strftime(get_setting(
            'CALENDAR_DATE_FORMAT'))}})
        event.update({'summary':summary})
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
        response = self.service.freebusy().query(body={'timeMin': start_date
                                    .strftime(get_setting(
                                    'CALENDAR_DATE_FORMAT')),
                                    'timeMax': end_date.strftime(get_setting(
                                    'CALENDAR_DATE_FORMAT')),
                                    'items': [{'id': calendar_id}]
                                    }).execute()
        return len(response['calendars'][calendar_id]['busy']) == 0

    def get_event(self, calendar_id, even_id):
        return self.service.events().get(calendarId=calendar_id,
                                         eventId=even_id).execute()

    def retrieve_all_events(self, calendar_id):
        events = []
        page_token = None
        while True:
            if page_token:
                tem_events = self.service.events().list(calendarId=calendar_id, pageToken=page_token).execute()
            else:
                tem_events = self.service.events().list(calendarId=calendar_id).execute()
            events.extend(tem_events['items'])
            page_token = tem_events.get('nextPageToken')
            if not page_token:
                break

        return events

    def clear_calendar(self, calendar_id):
        events = self.retrieve_all_events(calendar_id)
        logging.info("Deleting all calendar events")
        for event in events:
            self.delete_calentar_event(calendar_id, event['id'])

