from webapp2_extras import sessions
import settings
from webengine.handlers import BaseRequestHandler
from simpleauth.handler import SimpleAuthHandler
import logging
import secrets
from webengine import route
from webengine.models import User

class AuthHandler(BaseRequestHandler, SimpleAuthHandler):
    """Authentication handler for OAuth 2.0, 1.0(a) and OpenID."""

    # Enable optional OAuth 2.0 CSRF guard
    OAUTH2_CSRF_STATE = True

    def _on_signin(self, data, auth_info, provider, register=False):
        """Callback whenever a new or existing user is logging in.
         data is a user info dictionary.
         auth_info contains access token or oauth token and secret.
        """
        auth_id = '%s:%s' % (provider, data['id'])
        logging.info('Looking for a user with id %s', auth_id)
        
        user = self.auth.store.user_model.get_by_auth_id(auth_id)
        _attrs = self.auth.store.user_model._to_user_model_attrs(data, settings.USER_ATTRS[provider])

        if user:
            logging.info('Found existing user to log in')
            # Existing users might've changed their profile data so we update our
            # local model anyway. This might result in quite inefficient usage
            # of the Datastore, but we do this anyway for demo purposes.
            #
            # In a real app you could compare _attrs with user's properties fetched
            # from the datastore and update local user in case something's changed.
            user.populate(**_attrs)
            user.put()
            self.auth.set_session(
                self.auth.store.user_to_dict(user))
      
        else:
            # check whether there's a user currently logged in
            # then, create a new user if nobody's signed in, 
            # otherwise add this auth_id to currently logged in user.

            if self.logged_in:
                logging.info('Updating currently logged in user')
        
                u = self.current_user
                u.populate(**_attrs)
                # The following will also do u.put(). Though, in a real app
                # you might want to check the result, which is
                # (boolean, info) tuple where boolean == True indicates success
                # See webapp2_extras.appengine.auth.models.User for details.
                u.add_auth_id(auth_id)
        
            else:
                logging.info('Creating a brand new user')
                _attrs.update({'roles':[User.ROLE_USER]})
                ok, user = self.auth.store.user_model.create_user(auth_id, **_attrs)
                if ok:
                    self.auth.set_session(self.auth.store.user_to_dict(user))

        # Remember auth data during redirect, just for this demo. You wouldn't
        # normally do this.
        self.session.add_flash(data, 'data - from _on_signin(...)')
        self.session.add_flash(auth_info, 'auth_info - from _on_signin(...)')

        if register:
            self.json_response(user.to_dict())
        else:
            # Go to the profile page
            self.redirect(str(self.session.pop('after_login', '/')))

    def logout(self):
        self.auth.unset_session()
        self.redirect('/')
        
    def _callback_uri_for(self, provider):
        return self.uri_for('auth_callback', provider=provider, _full=True)
    
    def _get_consumer_info_for(self, provider):
        """Returns a tuple (key, secret) for auth init requests."""
        return secrets.AUTH_CONFIG[provider]


route('/logout', handler='%s.AuthHandler:logout' % AuthHandler.__module__, name='logout')()
route('/auth/<provider>', handler='%s.AuthHandler:_simple_auth' % AuthHandler.__module__, name='auth_login')()
route('/auth/<provider>/callback', handler='%s.AuthHandler:_auth_callback' % AuthHandler.__module__ , name='auth_callback')()
route('/auth/<provider>/register', handler='%s.AuthHandler:_auth_register' % AuthHandler.__module__ , name='auth_register')()