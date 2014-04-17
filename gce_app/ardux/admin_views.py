from ardux.helpers import OAuthDanceHelper
from flask.ext.admin import BaseView, expose
from flask.ext.admin.base import AdminIndexView, expose_plugview
from werkzeug.routing import RequestRedirect
import logging
from flask import abort, redirect, helpers, request
from settings import get_setting



class AdminIndex(AdminIndexView):
    @expose('/')
    def index(self):
        return self.render('admin_index.html')

