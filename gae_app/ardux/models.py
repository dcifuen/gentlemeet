import re
import datetime

from google.appengine.ext import ndb
from protorpc import messages
from google.appengine.api.datastore_errors import BadValueError

from constants import CHECK_IN
from endpoints_proto_datastore.ndb.model import EndpointsModel, \
    EndpointsAliasProperty
import constants


def validate_email(property, value):
    if value is None:
        return value
    elif not re.match(constants.EMAIL_REGEXP, value):
        raise BadValueError
    return value.lower()


def get_domain_from_email(entity):
    if entity.installer_user:
        domain = re.search("@[\w.]+", entity.installer_user)
        return domain.group()[1:]
    else:
        return None


class Client(ndb.Model):
    """Container of the general settings and the authorization stuff"""
    credentials = ndb.TextProperty(indexed=False)
    customer_id = ndb.StringProperty(indexed=False)
    refresh_token = ndb.StringProperty(indexed=False)
    installer_user = ndb.StringProperty(indexed=False, validator=validate_email)
    # FIXME: What if user is in a secondary domain?
    domain = ndb.ComputedProperty(get_domain_from_email, indexed=False)


class User(ndb.Model):
    """Both admins and event participants are users of the system"""
    is_admin = ndb.BooleanProperty(default=False, indexed=False)
    email = ndb.StringProperty(required=True, indexed=False)
    # The properties below are useful for Google+ interaction
    google_user_id = ndb.StringProperty(indexed=False)
    google_display_name = ndb.StringProperty(indexed=False)
    google_public_profile_url = ndb.StringProperty(indexed=False)
    google_public_profile_photo_url = ndb.StringProperty(indexed=False)
    google_credentials = ndb.TextProperty(indexed=False)


# *********** API Models ***************

class ResourceCalendar(EndpointsModel):
    """A replica of the actual Google Calendar resource, but with more
    information and relation with devices
    """
    _message_fields_schema = ('id', 'name', 'email', 'description', 'type')

    name = ndb.StringProperty(required=True, indexed=False)
    email = ndb.StringProperty(indexed=False)
    description = ndb.StringProperty(indexed=False)
    type = ndb.StringProperty(indexed=False)

    @EndpointsAliasProperty
    def id(self):
        return self.key.id()

    def get_today_events(self):
        today = datetime.datetime.today()
        today_start = datetime.datetime.combine(
            today, datetime.datetime.min.time())
        today_end = datetime.datetime.combine(
            today, datetime.datetime.max.time())
        # TODO: Cache the daily events results?
        #Since two inequality filters are not possible, get today events
        return ResourceEvent.query(
            ResourceEvent.original_start_date_time > today_start,
            ResourceEvent.original_start_date_time < today_end,
            ResourceEvent.resource_key == self.key
        ).fetch()

    def get_next_events_today(self):
        today = datetime.datetime.today()
        now = datetime.datetime.now()
        today_end = datetime.datetime.combine(
            today, datetime.datetime.max.time())
        # TODO: Cache the daily events results?
        #Since two inequality filters are not possible, get today events
        return ResourceEvent.query(
            ResourceEvent.original_start_date_time > now,
            ResourceEvent.original_start_date_time < today_end,
            ResourceEvent.resource_key == self.key
        ).fetch()


    def get_current_event(self):
        #Since two inequality filters are not possible, have to filter in memory
        today_events = self.get_today_events()
        now = datetime.datetime.now()
        for event in today_events:
            if (event.original_start_date_time < now <
                    event.original_end_date_time):
                return event
        return None

    def will_be_available(self, minutes):
        #Check that the resource is available or not in the given minutes
        today_events = self.get_today_events()
        now = datetime.datetime.now()
        end_time = now + datetime.timedelta(minutes=minutes)
        for event in today_events:
            if (event.start_date_time < now < event.end_date_time or
                    event.start_date_time < end_time < event.end_date_time):
                return False
        return True


class ResourceDevice(EndpointsModel):
    """The representation of the physical or web device that is at the
    calendar resource.
    """
    _message_fields_schema = (
        'name', 'uuid', 'uuid_query', 'type', 'state', 'last_sync', 'online',
        'resource_id', 'resource')

    name = ndb.StringProperty()
    uuid = ndb.StringProperty(required=True, indexed=False)
    type = ndb.StringProperty(choices=constants.DEVICE_CHOICES,
                              required=True, indexed=False)
    # TODO: Refactor states to use Fysom
    state = ndb.StringProperty(choices=constants.DEVICE_STATE_CHOICES,
                               indexed=False)
    last_sync = ndb.DateTimeProperty(auto_now_add=True)
    resource_key = ndb.KeyProperty(ResourceCalendar, indexed=False)

    @EndpointsAliasProperty(property_type=ResourceCalendar.ProtoModel())
    def resource(self):
        if self.resource_key:
            return self.resource_key.get()
        else:
            return None

    def ResourceSet(self, value):
        if value:
            self.resource_key = ndb.Key(ResourceCalendar, value)

    @EndpointsAliasProperty(setter=ResourceSet)
    def resource_id(self):
        if self.resource_key:
            return self.resource_key.id()
        else:
            return None

    @EndpointsAliasProperty(property_type=messages.BooleanField)
    def online(self):
        if self.last_sync:
            return self.last_sync >= datetime.datetime.now() - datetime.timedelta(
                minutes=6)
        else:
            return False

    def UuidSet(self, value):
        device = ResourceDevice.get_by_uuid(value)
        self.UpdateFromKey(device.key)

    @EndpointsAliasProperty(setter=UuidSet)
    def uuid_query(self):
        return self.uuid

    @staticmethod
    def get_by_uuid(uuid):
        devices = ResourceDevice.query(ResourceDevice.uuid == uuid).fetch()
        if len(devices) > 0:
            return devices[0]
        else:
            return None

    def to_dict(self, *args, **kwargs):
        result = super(ResourceDevice, self).to_dict(*args, **kwargs)
        resource = self.resource
        if resource:
            result['resource'] = self.resource.to_dict(include=('name',))
            result['events'] = [
                event.to_dict(exclude=('resource_key', 'attendees'))
                for event in ResourceEvent.query(
                    ResourceEvent.resource_key == ndb.Key(ResourceCalendar,
                                                          self.resource_id)
                ).fetch()
            ]
        return result


class ResourceEvent(EndpointsModel):
    """A replica of the actual Google Calendar event, needed for analysis
    and sync purposes. All day or recurrent events are not supported
    """
    organizer = ndb.StringProperty(indexed=False)
    original_start_date_time = ndb.DateTimeProperty(required=True)
    original_end_date_time = ndb.DateTimeProperty(required=True)
    actual_start_date_time = ndb.DateTimeProperty(indexed=False)
    actual_end_date_time = ndb.DateTimeProperty(indexed=False)
    actual_attendees = ndb.StringProperty(repeated=True, indexed=False)
    yes_attendees = ndb.StringProperty(repeated=True, indexed=False)
    no_attendees = ndb.StringProperty(repeated=True, indexed=False)
    maybe_attendees = ndb.StringProperty(repeated=True, indexed=False)
    no_response_attendees = ndb.StringProperty(repeated=True, indexed=False)
    resource_key = ndb.KeyProperty(ResourceCalendar)
    title = ndb.StringProperty(indexed=False)
    summary = ndb.StringProperty(indexed=False)
    description = ndb.StringProperty(indexed=False)
    is_express = ndb.BooleanProperty(indexed=False)
    state = ndb.StringProperty(choices=constants.EVENT_STATE_CHOICES,
                               indexed=False)

    def ResourceSet(self, value):
        if value:
            self.resource_key = ndb.Key(ResourceCalendar, value)

    @EndpointsAliasProperty(setter=ResourceSet)
    def resource_id(self):
        if self.resource_key:
            return self.resource_key.id()
        else:
            return None

    @property
    def start_date_time(self):
        return self.actual_start_date_time if self.actual_start_date_time else self.original_start_date_time

    @property
    def end_date_time(self):
        return self.actual_end_date_time if self.actual_end_date_time else self.original_end_date_time

    @property
    def attendees(self):
        return list(set(self.actual_attendees + self.yes_attendees +
                        self.no_attendees + self.maybe_attendees +
                        self.no_response_attendees))

    @property
    def remaining_time(self):
        now = datetime.datetime.now()
        if (self.state == constants.STATE_IN_PROGRESS and
                self.original_end_date_time and self.original_end_date_time > now):
            return int((self.original_end_date_time - now).total_seconds())
        return None


class CheckInOut(EndpointsModel):
    """Records the check ins and check outs of the attendees and based on that
    marks the resource as free or busy. The event is the parent
    """
    attendee = ndb.StringProperty(required=True)
    date_time = ndb.DateTimeProperty(required=True, auto_now_add=True,
                                     indexed=False)
    type = ndb.StringProperty(choices=constants.CHECK_CHOICES,
                              required=True)

    @classmethod
    def already_checked(cls, type, attendee_email, event):
        """
        Check if the user has already check in or not
        @param attendee_email: email address of the attendee
        @param event: parent event
        @return: true if there is a check in record, false if not
        """
        previous_check = CheckInOut.query(ndb.AND(
            CheckInOut.type == type,
            CheckInOut.attendee == attendee_email
        ), ancestor=event.key).fetch(
            1,
            keys_only=True
        )
        if len(previous_check) > 0:
            return True
        return False

    @classmethod
    def checked_in_before(cls, attendee_email, event, when):
        previous_checkin = CheckInOut.query(ndb.AND(
            CheckInOut.type == CHECK_IN,
            CheckInOut.attendee == attendee_email
        ), ancestor=event.key).get()
        if previous_checkin:
            return previous_checkin.date_time < when
        return False


@ndb.transactional
def store_check_in(event, user_email):
    """
    Store the attendee as an actual attendee in the event and store the
    check in entity
    @param event: parent event
    @param user_email: email address of the attendee
    """
    if user_email not in event.actual_attendees:
        event.actual_attendees.append(user_email)
        event.put()
    CheckInOut(parent=event.key, attendee=user_email,
               type=CHECK_IN).put()
