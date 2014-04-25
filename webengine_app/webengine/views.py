'''
Created on 7/01/2014

@author: Jorge Salcedo
'''
import settings
from importlib import import_module
from webengine import route, WSGIWebEngine
import logging

@route('/_ah/warmup')
def warmup(handler):
    for app in settings.APPS:
        for name in ('views', 'models', 'apis', 'admin_views'):
            try:
                module = 'apps.%s.%s' % (app, name)
                import_module(module)
            except ImportError:
                logging.info("Could not import [%s], error:",module)
                
    return "warming up..."

def handle_401(request, response, exception):
    logging.exception(exception)
    response.write('Oops! I could swear this page was here!')
    response.set_status(401)
    
def handle_404(request, response, exception):
    logging.exception(exception)
    response.write('Oops! I could swear this page was here!')
    response.set_status(404)

def handle_500(request, response, exception):
    logging.exception(exception)
    response.write('A server error occurred!')
    response.set_status(500)


WSGIWebEngine._instance.error_handlers[401] = handle_401  # @UndefinedVariable
WSGIWebEngine._instance.error_handlers[404] = handle_404  # @UndefinedVariable
WSGIWebEngine._instance.error_handlers[500] = handle_500  # @UndefinedVariable