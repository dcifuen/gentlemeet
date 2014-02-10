import logging
from google.appengine.ext import ndb
from endpoints_proto_datastore.ndb.model import EndpointsModel, EndpointsAliasProperty
from protorpc import messages
from settings import get_setting
import re
from google.appengine.api.datastore_errors import BadValueError
import datetime

def validate_email(property, value):
    if value is None:
        return value
    elif not re.match(get_setting('EMAIL_REGEXP'), value):
        raise BadValueError
    return value.lower()

class Client(ndb.Model):
    """Container of the general settings and the authorization stuff"""
    credentials = ndb.TextProperty(indexed=False)
    customer_id = ndb.StringProperty(indexed=False)
    refresh_token = ndb.StringProperty(indexed=False)
    installer_user = ndb.StringProperty(indexed=False, validator=validate_email)


class User(ndb.Model):
    """Both admins and event participants are users of the system"""
    is_admin = ndb.BooleanProperty(default=False, indexed=False)
    email = ndb.StringProperty(required=True, indexed=False)
    #The properties below are useful for Google+ interaction
    google_user_id = ndb.StringProperty(indexed=False)
    google_display_name = ndb.StringProperty(indexed=False)
    google_public_profile_url = ndb.StringProperty(indexed=False)
    google_public_profile_photo_url = ndb.StringProperty(indexed=False)
    google_credentials = ndb.TextProperty(indexed=False)


#*********** API Models ***************

class ResourceDevice(EndpointsModel):
    """The representation of the physical or web device that is at the
    calendar resource.
    """
    _message_fields_schema = ('name', 'uuid','type','state', 'last_sync' , 'online')

    TYPE_PHYSICAL = 'PHYSICAL'
    TYPE_WEB = 'WEB'
    TYPE_CHOICES = [
        TYPE_PHYSICAL,
        TYPE_WEB,
    ]

    STATE_REGISTERED = 'REGISTERED'
    STATE_ACTIVE = 'ACTIVE'
    STATE_INACTIVE = 'INACTIVE'
    STATE_CHOICES = [
        STATE_REGISTERED,
        STATE_ACTIVE,
        STATE_INACTIVE,
    ]

    name = ndb.StringProperty()
    uuid = ndb.StringProperty()
    type = ndb.StringProperty(choices=TYPE_CHOICES, indexed=False)
    state = ndb.StringProperty(choices=STATE_CHOICES, indexed=False)
    last_sync = ndb.DateTimeProperty(auto_now_add=True)

    @EndpointsAliasProperty(property_type=messages.BooleanField)
    def online(self):
        if self.last_sync:
            return self.last_sync >= datetime.datetime.now()-datetime.timedelta(seconds=30)
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



class ResourceCalendar(EndpointsModel):
    """A replica of the actual Google Calendar resource, but with more
    information and relation with devices
    """
    id = ndb.StringProperty(required=True, indexed=False)
    name = ndb.StringProperty(required=True, indexed=False)
    device = ndb.KeyProperty(ResourceDevice, indexed=False)
    #False means that is busy
    is_free = ndb.BooleanProperty(default=True, indexed=False)


class ResourceEvent(EndpointsModel):
    """A replica of the actual Google Calendar event, needed for analysis
    and sync purposes. All day or recurrent events are not supported
    """
    id = ndb.StringProperty(required=True, indexed=False)
    organizer = ndb.StringProperty(indexed=False)
    start_date_time = ndb.DateTimeProperty(indexed=False)
    end_date_time = ndb.DateTimeProperty(indexed=False)
    attendees = ndb.StringProperty(repeated=True, indexed=False)
    resource = ndb.KeyProperty(ResourceCalendar, indexed=False)


class CheckIO(EndpointsModel):
    """Records the check ins and check outs of the attendees and based on that
    marks the resource as free or busy.
    """
    TYPE_IN = 'IN'
    TYPE_OUT = 'OUT'
    TYPE_CHOICES = [
        TYPE_IN,
        TYPE_OUT,
    ]

    attendee = ndb.StringProperty(indexed=False)
    date_time = ndb.DateTimeProperty(required=True, auto_now_add=True,
                                     indexed=False)
    type = ndb.StringProperty(choices=TYPE_CHOICES, required=True,
                              indexed=False)
    event = ndb.KeyProperty(ResourceEvent, indexed=False)
    resource = ndb.KeyProperty(ResourceCalendar, required=True, indexed=False)
