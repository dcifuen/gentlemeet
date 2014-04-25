'''
Created on 21/01/2014

@author: Jorge Salcedo
'''
from webengine import route
import logging
from secrets import FACEBOOK_APP_ID, FACEBOOK_SCOPE


@route('/auth/js/<provider>.js')
def provider_javascript(handler, provider):
    handler.response.headers['Content-Type'] = 'text/javascript'
    handler.render('auth/js/%s.js' % provider, {'FACEBOOK_APP_ID':FACEBOOK_APP_ID,
                                                'FACEBOOK_SCOPE':FACEBOOK_SCOPE})