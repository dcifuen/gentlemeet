from ardux.base_models import BaseDataStoreModel, StringProperty
import ndb

class Device(ndb.Model):
    STATE_REGISTERED = 'REGISTERED'
    STATE_ACTIVE = 'ACTIVE'
    STATE_INACTIVE = 'INACTIVE'

    name = ndb.StringProperty()
    type = ndb.StringProperty()
    state = ndb.StringProperty()