'''
Created on 7/01/2014

@author: Jorge Salcedo
'''
import logging
import urllib
import webapp2
from webapp2_extras import sessions, jinja2, auth
from jinja2.exceptions import TemplateNotFound
from minidetector.useragents import search_strings
import os
from webengine.utils import DateTimeEncoder, get_app_host
import jinja2 as global_jinja2
from jinja2 import Template
import json
import webengine
from google.appengine.ext import ndb, blobstore
from google.appengine.ext.webapp import blobstore_handlers



def jinja2_factory(app):
    j = jinja2.Jinja2(app)
    j.environment.filters.update({
        # Set filters.
        # ...
    })
    
    j.environment.globals.update({
        # Set global variables.
        'uri_for': webapp2.uri_for,
        'request': app.request,
        'api_host': get_app_host(include_version=False),
        'admin_views': {key:value for key, value in sorted(webengine.WSGIWebEngine.get_admin_views().iteritems(), key=lambda (k,v): v['order'], reverse=True)}

        # ...
    })
    j.environment.loader = global_jinja2.FileSystemLoader(['templates', os.path.join('webengine','templates')])
    return j

class BaseRequestHandler(webapp2.RequestHandler):
    def dispatch(self):
        # Get a session store for this request.
        self.session_store = sessions.get_store(request=self.request)
        self.request.mobile = False
        try:
            if self.request.headers.has_key("X-OperaMini-Features"):
                #Then it's running opera mini. 'Nuff said.
                #Reference from:
                # http://dev.opera.com/articles/view/opera-mini-request-headers/
                self.request.mobile = True
    
            if self.request.headers.has_key("Accept"):
                s = self.request.headers["Accept"].lower()
                if 'application/vnd.wap.xhtml+xml' in s:
                    # Then it's a wap browser
                    self.request.mobile = True
            if self.request.headers.has_key("User-Agent"):
                # This takes the most processing. Surprisingly enough, when I
                # Experimented on my own machine, this was the most efficient
                # algorithm. Certainly more so than regexes.
                # Also, Caching didn't help much, with real-world caches.
                s = self.request.headers["User-Agent"].lower()
                for ua in search_strings:
                    if ua in s:
                        self.request.mobile = True
    
            #Otherwise it's not a mobile
            webapp2.RequestHandler.dispatch(self)
        finally:
            # Save all sessions.
            self.session_store.save_sessions(self.response)
  
    def handle_exception(self, exception, debug):
        # Log the error.
        logging.exception(exception)

        # Set a custom message.
        #self.response.write('An error occurred.')

        # If the exception is a HTTPException, use its error code.
        # Otherwise use a generic 500 error code.
        if isinstance(exception, webapp2.HTTPException):
            code = exception.code    
        else:
            code = 500
            
        self.render("%s.html" % code, {'exception':exception})
        self.response.set_status(code)
  
    @webapp2.cached_property    
    def jinja2(self):
        """Returns a Jinja2 renderer cached in the app registry"""
        return jinja2.get_jinja2(app=self.app, factory=jinja2_factory)
    
    @webapp2.cached_property
    def session(self):
        """Returns a session using the default cookie key"""
        return self.session_store.get_session()
    
    @webapp2.cached_property
    def auth(self):
        return auth.get_auth()
  
    @webapp2.cached_property
    def current_user(self):
        """Returns currently logged in user"""
        user_dict = self.auth.get_user_by_session()
        if user_dict is not None:
            return ndb.Key(self.auth.store.user_model, user_dict['user_id']).get()
        else:
            return None
      
    @webapp2.cached_property
    def logged_in(self):
        """Returns true if a user is currently logged in, false otherwise"""
        return self.auth.get_user_by_session() is not None
  
    def json_response(self, obj):
        self.response.headers['Content-Type'] = 'application/json'   
        self.response.out.write(json.dumps(obj, cls=DateTimeEncoder))
      
    def render(self, template_name, template_vars={}):
        # read the template or 404.html
        try:
            self.response.write(self.jinja2.render_template(template_name, **template_vars))
        except TemplateNotFound:
                self.abort(404)
    
    def render_string(self, template_string, template_vars={}):
        self.response.write(self.jinja2.environment.from_string(template_string).render(**template_vars))
        
    def head(self, *args):
        """Head is used by Twitter. If not there the tweet button shows 0"""
        pass


class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        upload_files = self.get_uploads('file')  # 'file' is file upload field in the form
        blob_info = upload_files[0]
        self.redirect('/serve/%s' % blob_info.key())

class ServeHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, resource):
        resource = str(urllib.unquote(resource))
        blob_info = blobstore.BlobInfo.get(resource)
        self.send_blob(blob_info)