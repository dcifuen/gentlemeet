'''
Created on 15/01/2014

@author: Jorge Salcedo
'''
import time
from google.appengine.api import memcache
import webapp2_extras.appengine.auth.models
from google.appengine.ext import ndb
from webapp2_extras import security
import decimal
from endpoints_proto_datastore.ndb.model import EndpointsModel
import re
from slugify import slugify


class DecimalProperty(ndb.StringProperty):
    # data_type = decimal.Decimal
    def _validate(self, value):
        if not isinstance(value, decimal.Decimal):
            if not isinstance(value, str):
                if not isinstance(value, unicode):
                    if not isinstance(value, float):
                        raise TypeError("expected Decimal or String, got %s." % repr(value))

    def _to_base_type(self, value):
        return str(value)

    # def make_value_from_datastore(self, value):
    def _from_base_type(self, value):
        return decimal.Decimal(value)

class BaseModel(EndpointsModel):
    created = ndb.DateTimeProperty(auto_now_add=True, indexed=False)
    modified = ndb.DateTimeProperty(auto_now=True, indexed=False)



class SlugifyModel(ndb.Model):

    _slug_property = None
    slug = ndb.StringProperty()

    def _post_put_hook(self, future):
        entity = future.get_result().get()
        slugs = self.get_slugs()
        slugs[entity.key.urlsafe()] = entity.slug
        memcache.set("%s_slugs" % self.__class__.__name__, slugs)  # @UndefinedVariable

    def _pre_put_hook(self):
        self.slug = self._slugify()

    def _slugify(self):
        if self._slug_property:
            slugs = self.get_slugs()
            slug = slugify(getattr(self, self._slug_property))
            count = 0
            counter = False
            for key, value in slugs.iteritems():
                if self.key.urlsafe() != key and value.startswith(slug):
                    counter = True
                    m = re.search('([-]\d+)$', value)
                    if m:
                        number = int(m.group(0)[1:])
                        if number > count:
                            count = number
            if counter:
                count += 1
                slug = "-".join([slug, str(count)])
            return slug

    @classmethod
    def get_by_slug(cls, slug):
        slugs = cls.get_slugs()
        for key, value in slugs.iteritems():
            if value == slug:
                return ndb.Key(urlsafe=key).get()
        return None

    @classmethod
    def get_slugs(cls):
        slugs = memcache.get("%s_slugs" % cls.__name__)  # @UndefinedVariable
        if slugs is None:
            entities = cls.query().fetch()
            slugs = {entity.key.urlsafe(): entity.slug for entity in entities
                     if entity.slug}
            memcache.set("%s_slugs" % cls.__name__, slugs)  # @UndefinedVariable
        return slugs



class User(EndpointsModel, webapp2_extras.appengine.auth.models.User):
    ROLE_USER="USER"
    ROLE_ADMIN="ADMIN"
    ROLE_SUPERADMIN="SUPERADMIN"
    ROLE_CLIENT="CLIENT"
    ROLES = [ROLE_USER,
             ROLE_ADMIN,
             ROLE_SUPERADMIN,
             ROLE_CLIENT]
    
    roles = ndb.StringProperty(repeated=True, choices=ROLES)



    def set_password(self, raw_password):
        """Sets the password for the current user
     
        :param raw_password:
            The raw password which will be hashed and stored
        """
        self.password = security.generate_password_hash(raw_password, length=12)
 
    @classmethod
    def get_by_auth_token(cls, user_id, token, subject='auth'):
        """Returns a user object based on a user ID and token.
     
        :param user_id:
            The user_id of the requesting user.
        :param token:
            The token string to be verified.
        :returns:
            A tuple ``(User, timestamp)``, with a user object and
            the token timestamp, or ``(None, None)`` if both were not found.
        """
        token_key = cls.token_model.get_key(user_id, subject, token)
        user_key = ndb.Key(cls, user_id)
        # Use get_multi() to save a RPC call.
        valid_token, user = ndb.get_multi([token_key, user_key])
        if valid_token and user:
            timestamp = int(time.mktime(valid_token.created.timetuple()))
            return user, timestamp
 
        return None, None

    def get_provider_id(self, provider):
        for auth_id in self.auth_ids:
            if auth_id.startswith(provider):
                return auth_id.split(":")[1]
        return None

    @classmethod
    def _to_user_model_attrs(cls, data, attrs_map):
        """Get the needed information from the provider dataset."""
        user_attrs = {}
        for k, v in attrs_map.iteritems():
            attr = (v, data.get(k)) if isinstance(v, str) else v(data.get(k))
            user_attrs.setdefault(*attr)
        return user_attrs

    def is_admin(self):
        return self.ROLE_ADMIN in self.roles or self.ROLE_SUPERADMIN in self.roles