#-*- coding: utf-8 -*-
# vim: set fileencoding=utf-8

import logging
from xml.dom.minidom import Document, Element

from oauth2client.client import OAuth2WebServerFlow
from oauth2client.client import Credentials
from suds.client import Client
from suds.transport.http import HttpAuthenticated
from apiclient.discovery import build
from settings import get_setting
import pytz
from pytz import timezone

import httplib2


class AutoTaskHelper:
    """AutoTask API helper class"""
    client = None

    def __init__(self):
        logging.info('Connecting to AutoTask API')
        url = get_setting('AUTOTASK_API_URL')
        t = HttpAuthenticated(username=get_setting(
            'AUTOTASK_API_USERNAME'), password=get_setting(
            'AUTOTASK_API_PASSWORD'))
        self.client = Client(url, transport=t)
        self.query_xml_helper = QueryXmlHelper()

    def get_all_projects(self):
        projects = []

        result = self.get_entities("Project", DomQueryField(id__greaterthan=-1))
        projects.extend(result)
        while len(result) >= 500:
            #Max number of autotask entities is 500
            result = self.get_entities("Project", DomQueryField(id__greaterthan=result[-1].id))
            projects.extend(result)
        return projects

    def get_project(self, project_id):
        result = self.get_entities("Project", DomQueryField(id__equals=project_id))
        if len(result) == 1:
            return result[0]

    def get_all_project_tasks(self, project_id):
        tasks = []
        result = self.get_entities("Task", DomQueryField(projectid__equals=project_id))
        tasks.extend(result)
        while len(result) >= 500:
            #Max number of autotask entities is 500
            result = self.get_entities("Task", DomQueryField(projectid__equals=project_id) & DomQueryField(id__greaterthan=result[-1].id))
            tasks.extend(result)
        return tasks

    def get_resource(self, resource_id):
        return self.get_entities("Resource", DomQueryField(id__equals=resource_id))[0]

    def _process_response(self, response):
        if response.ReturnCode == 1 and len(response.EntityResults) > 0:
            return response.EntityResults[0]
        else:
            return []

    def get_entities(self, entity_name, query_field):
        query = self.query_xml_helper.buildQueryXml(entity_name,query_field)
        result = self.client.service.query(query)
        return self._process_response(result)


    def _fill_entity_values(self,entity,**kwargs):
        for key, value in kwargs.items():
            key = key.replace("_"," ").title().replace("Id","ID").replace(" ","")
            if hasattr(entity,key):
                setattr(entity,key, value)

    def add_task(self, project_id, title,  department_id, allocation_code_id, **kwargs):
        project = self.get_project(project_id)
        task = self.client.factory.create('Task')
        task.AllocationCodeID = 29687389 #allocation_code_id
        task.DepartmentID = project.Department #department_id
        task.id = 0 #New
        task.ProjectID = project_id
        #logging.info(app.config['AUTOTASK_NEW_STATUS'])
        #logging.info(app.config['AUTOTASK_FIXED_WORK_TASK_TYPE'])
        task.Status = 1#app.config['AUTOTASK_NEW_STATUS']
        task.TaskType= 1 #app.config['AUTOTASK_FIXED_WORK_TASK_TYPE']
        task.Title = title

        self._fill_entity_values(task,**kwargs)

        taskArray = self.client.factory.create('ArrayOfEntity')
        taskArray.Entity.append(task)

        response = self.client.service.create(taskArray)
        logging.info(response)
        return self._process_response(response)[0]

class OAuthDanceHelper:
    """ OAuth dance helper class"""
    flow = None

    def __init__(self, redirect_uri='', approval_prompt='auto',
                 scope=None):
        scope = get_setting('OAUTH2_DOMAIN_SCOPE')
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

class ResellerHelper(OAuthServiceHelper):
    """ Google Apps Reseller API helper class"""

    def __init__(self, credentials_json, refresh_token=None):
        super(ResellerHelper, self).__init__(credentials_json, refresh_token)
        self.service = build('reseller', 'v1', http=self.http)


class QueryXmlHelper():

    def buildQueryXml(self,entity_name, query_field):
        if not isinstance(query_field, DomQueryField):
            raise TypeError(query_field)
        doc = Document()
        queryxml = doc.createElement('queryxml')
        entity = doc.createElement('entity')
        query = doc.createElement('query')
        content = doc.createTextNode(entity_name)
        entity.appendChild(content)
        queryxml.appendChild(entity)
        queryxml.appendChild(query)
        query.appendChild(query_field)
        return queryxml.toxml()

class DomQueryField(Element):

    conditions = ["equals",
                  "notequal",
                  "greaterthan",
                  "lessthan",
                  "greaterthanorequals",
                  "lessthanorequals",
                  "beginswith",
                  "endswith",
                  "contains",
                  "isnotnull",
                  "isnull",
                  "isthisday",
                  "like",
                  "notlike",
                  "soundslike"]

    AND = "AND"
    OR = "OR"

    def __init__(self, *args, **kwargs):
        if len(kwargs) == 1:
            try:
                field_expression = kwargs.iterkeys().next()
                fieldname, expression_str = field_expression.split("__")
                if expression_str in self.conditions:
                    self.fieldname = fieldname
                    self.expression = expression_str
                    self.value = kwargs.get(field_expression)
                    self.ownerDocument = Document()
                    Element.__init__(self,"field")
                    name = self.ownerDocument.createTextNode(fieldname)
                    self.appendChild(name)
                    expression = self.ownerDocument.createElement("expression")
                    expression.setAttribute("op",self.expression)
                    expression_value = self.ownerDocument.createTextNode(str(self.value))
                    expression.appendChild(expression_value)
                    self.appendChild(expression)
                else:
                    raise Exception("Invalid expression, options are %s" % self.conditions)
            except ValueError:
                raise Exception("Invalid key word argument name, should be fieldname__expression")
        else:
            raise Exception("Invalid number of arguments, should be only one key word argument")

    def _combine(self, other, conn):
        if not isinstance(other, DomQueryField):
            raise TypeError(other)
        copy = self.cloneNode(deep=True)
        other_copy = other.cloneNode(deep=True)
        Element.__init__(self,"condition")
        if copy.tagName == "field":
            condition = self.ownerDocument.createElement("condition")
            condition.appendChild(copy)
        else:
            condition = copy

        if other_copy.tagName == "field":
            condition2 = self.ownerDocument.createElement("condition")
            condition2.appendChild(other_copy)
        else:
            condition2 = other_copy


        condition2.setAttribute("operator",conn)
        self.appendChild(condition)
        self.appendChild(condition2)
        return self

    def __and__(self, other):
        return self._combine(other,self.AND)

    def __or__(self, other):
        return self._combine(other,self.OR)