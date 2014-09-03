from datetime import datetime, timedelta
import logging

from google.appengine.ext import ndb, deferred

from ardux.helpers import CalendarResourceHelper, CalendarHelper
from ardux.models import Client, ResourceCalendar, ResourceEvent
from dateutil.parser import parse
import pytz
import constants


def sync_resources():
    client = Client.get_by_id(1)
    if client:
        try:
            if client.credentials and client.refresh_token:
                helper = CalendarResourceHelper(client.credentials,
                                                client.refresh_token,
                                                client.domain)
                resources = helper.get_all_resources()
                resource_keys = ResourceCalendar.query().fetch(keys_only=True)
                resources_ids = []
                for resource in resources:
                    resource_id = resource.GetResourceId()
                    logging.info("Adding or updating resource %s" % resource_id)
                    resources_ids.append(resource_id)
                    db_resource = ResourceCalendar()
                    db_resource.UpdateFromKey(
                        ndb.Key(ResourceCalendar, resource_id))
                    db_resource.name = resource.GetResourceCommonName()
                    db_resource.description = resource.GetResourceDescription()
                    db_resource.email = resource.GetResourceEmail()
                    db_resource.type = resource.GetResourceType()
                    db_resource.put()
                    deferred.defer(sync_resource_events, resource_id,
                                   db_resource.email)

                resources_db_ids = [resource_key.id() for resource_key in
                                    resource_keys]
                delete_ids = list(set(resources_db_ids) - set(resources_ids))
                delete_keys = [ndb.Key(ResourceCalendar, id) for id in
                               delete_ids]
                ndb.delete_multi(delete_keys)

                logging.info(
                    "Deleted %s resources from data store" % len(delete_keys))

            else:
                logging.warn("Application not authorized with Google Apis")
        except Exception, e:
            logging.exception("Error ocurred syncing resources")
    else:
        logging.warn("No client found for resources sync")


# TODO: Check if instead (or in addition) to polling we can use web hooks
def sync_resource_events(resource_id, resource_email):
    client = Client.get_by_id(1)
    if client:
        try:
            if client.credentials and client.refresh_token:

                today = pytz.utc.localize(datetime.now())
                one_week_after = today + timedelta(weeks=1)
                helper = CalendarHelper(client.credentials,
                                        client.refresh_token)
                events = helper.list_events(calendar_id=resource_email,
                                            alwaysIncludeEmail=True,
                                            orderBy="startTime",
                                            singleEvents=True,
                                            timeMax=one_week_after.strftime(
                                                constants.CALENDAR_DATE_TIME),
                                            timeMin=today.strftime(
                                                constants.CALENDAR_DATE_TIME)
                )

                for event in events:
                    event_id = event['id']
                    logging.info("Adding or updating event %s for resource %s",
                                 event_id, resource_id)
                    event_db = ResourceEvent()
                    event_db.UpdateFromKey(ndb.Key(ResourceEvent, event_id))
                    event_db.organizer = event['organizer']['email']
                    event_db.original_start_date_time = pytz.utc.normalize(
                        parse(event['start']['dateTime'])).replace(tzinfo=None)
                    event_db.original_end_date_time = pytz.utc.normalize(
                        parse(event['end']['dateTime'])).replace(tzinfo=None)

                    no_response_attendees = []
                    maybe_attendees = []
                    yes_attendees= []
                    no_attendees=[]

                    for attendee in event.get('attendees',[]):
                        if not attendee.get('resource', False):
                            attendee_email = attendee['email']
                            logging.info('Adding attendee %s response %s',
                                         attendee_email, attendee['responseStatus'])
                            if attendee['responseStatus'] == "accepted":
                                yes_attendees.append(attendee_email)
                            elif attendee['responseStatus'] == "tentative":
                                maybe_attendees.append(attendee_email)
                            elif attendee['responseStatus'] == "declined":
                                no_attendees.append(attendee_email)
                            elif attendee['responseStatus'] == "needsAction":
                                no_response_attendees.append(
                                    attendee_email)
                    event_db.yes_attendees = yes_attendees
                    event_db.maybe_attendees = maybe_attendees
                    event_db.no_attendees = no_attendees
                    event_db.no_response_attendees = no_response_attendees

                    event_db.resource_key = ndb.Key(ResourceCalendar,
                                                    resource_id)
                    event_db.summary = event['summary']
                    event_db.description = event.get('description','')
                    event_db.put()

            else:
                pass
        except Exception, e:
            logging.exception("Error ocurred syncing events")
    else:
        logging.warn("No client found for events sync")


def check_release_resource():
    """
    Checks over all the resources and check for events that haven't started in
    the limit amount  of time and frees the resource for another possible meeting
    """
    for resource in ResourceCalendar.get_all():
        current = resource.get_current_event()
        if current and current.state == constants.STATE_SCHEDULED:
            now = datetime.datetime.now()
            release_delta = datetime.timedelta(minutes=constants.RELEASE_MINUTES)
            if current.start_date_time + release_delta < now:
                logging.info('Event [%s] didnt get check ins, releasing it',
                              current.title)
                current.state = constants.STATE_CANCELLED
                current.put()





