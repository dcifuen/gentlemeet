from google.appengine.ext import ndb
from endpoints_proto_datastore.ndb.model import EndpointsModel


class Client(ndb.Model):
    """Container of the general settings and the authorization stuff"""
    credentials = ndb.TextProperty(indexed=False)
    customer_id = ndb.StringProperty(indexed=False)
    refresh_token = ndb.StringProperty(indexed=False)
    installer_user = ndb.EmailProperty(indexed=False)


class User(ndb.Model):
    """Both admins and event participants are users of the system"""
    is_admin = ndb.BooleanProperty(default=False, indexed=False)
    email = ndb.EmailProperty(required=True, indexed=False)
    #The properties below are useful for Google+ interaction
    google_user_id = ndb.StringProperty(indexed=False)
    google_display_name = ndb.StringProperty(indexed=False)
    google_public_profile_url = ndb.LinkProperty(indexed=False)
    google_public_profile_photo_url = ndb.LinkProperty(indexed=False)
    google_credentials = ndb.TextProperty(indexed=False)


#*********** API Models ***************

class ResourceDevice(EndpointsModel):
    """The representation of the physical or web device that is at the
    calendar resource.
    """
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
    organizer = ndb.EmailProperty(indexed=False)
    start_date_time = ndb.DateTimeProperty(indexed=False)
    end_date_time = ndb.DateTimeProperty(indexed=False)
    attendees = ndb.EmailProperty(repeated=True, indexed=False)
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

    attendee = ndb.EmailProperty(indexed=False)
    date_time = ndb.DateTimeProperty(required=True, auto_now_add=True,
                                     indexed=False)
    type = ndb.StringProperty(choices=TYPE_CHOICES, required=True,
                              indexed=False)
    event = ndb.KeyProperty(ResourceEvent, indexed=False)
    resource = ndb.KeyProperty(ResourceCalendar, required=True, indexed=False)
