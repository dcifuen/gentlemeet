from google.appengine.ext import ndb
from endpoints_proto_datastore.ndb.model import EndpointsModel

class Client(ndb.Model):
    credentials = ndb.TextProperty()
    customer_id = ndb.StringProperty()
    refresh_token = ndb.StringProperty()
    installer_user = ndb.StringProperty()

class User(ndb.Model):
    is_admin = ndb.BooleanProperty()


#*********** API Models ***************

class ResourceDevice(EndpointsModel):
    name = ndb.StringProperty()
    uuid = ndb.StringProperty()


class ResourceCalendar(EndpointsModel):
    id = ndb.StringProperty()

