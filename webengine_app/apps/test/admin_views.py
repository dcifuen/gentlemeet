'''
Created on 29/01/2014

@author: Jorge Salcedo
'''
from apps.visor.models import Photo, Bucket, Template
from webengine import route
from webapp2_extras import routes
from webengine.models import User

@route(r'/admin',
       admin_name="Home",
       admin_order=1,
       roles=[User.ROLE_ADMIN], strict_slash=True)
def admin_index(handler, *args, **kwargs):
    template = 'admin/index.html'
    handler.render(template, {'user': handler.current_user})

