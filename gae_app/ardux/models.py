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
    domain = ndb.ComputedProperty(get_domain_from_email, indexed=False)


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

class ResourceCalendar(EndpointsModel):
    _message_fields_schema = ('id', 'name', 'email', 'description', 'type')
    """A replica of the actual Google Calendar resource, but with more
    information and relation with devices
    """
    name = ndb.StringProperty(indexed=False)
    email = ndb.StringProperty(indexed=False)
    description = ndb.StringProperty(indexed=False)
    type = ndb.StringProperty(indexed=False)

    @EndpointsAliasProperty
    def id(self):
        return self.key.id()


class ResourceDevice(EndpointsModel):
    """The representation of the physical or web device that is at the
    calendar resource.
    """
    _message_fields_schema = ('name', 'uuid', 'uuid_query','type','state', 'last_sync', 'online', 'resource_id', 'resource')

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
            return self.last_sync >= datetime.datetime.now()-datetime.timedelta(minutes=6)
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
        result = super(ResourceDevice,self).to_dict(*args, **kwargs)
        resource = self.resource
        if resource:
            result['resource'] = self.resource.to_dict(include=('name',))
            result['events'] = [event.to_dict(exclude=('resource_key','attendees')) for event in ResourceEvent.query(ResourceEvent.resource_key == ndb.Key(ResourceCalendar,self.resource_id)).fetch()]
        return result

class ResourceEvent(EndpointsModel):
    """A replica of the actual Google Calendar event, needed for analysis
    and sync purposes. All day or recurrent events are not supported
    """
    organizer = ndb.StringProperty(indexed=False)
    start_date_time = ndb.DateTimeProperty(indexed=False)
    end_date_time = ndb.DateTimeProperty(indexed=False)
    attendees = ndb.StringProperty(repeated=True, indexed=False)
    resource_key = ndb.KeyProperty(ResourceCalendar)
    summary = ndb.StringProperty(indexed=False)

    def ResourceSet(self, value):
        if value:
            self.resource_key = ndb.Key(ResourceCalendar, value)

    @EndpointsAliasProperty(setter=ResourceSet)
    def resource_id(self):
        if self.resource_key:
            return self.resource_key.id()
        else:
            return None



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
