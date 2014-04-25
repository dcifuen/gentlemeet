from importlib import import_module
import webapp2
import settings
import logging
from webapp2_extras import sessions, jinja2, auth, routes
from jinja2.exceptions import TemplateNotFound
import inspect
import sys
from protorpc import remote
import endpoints


class WSGIWebEngine(webapp2.WSGIApplication):
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(WSGIWebEngine, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self, *args, **kwargs):
        super(WSGIWebEngine, self).__init__(*args, **kwargs)
        self.apis_list = []
        self.admin_views = {}
        from webengine import views
        from webengine.auth import views, handlers
        for app in settings.APPS:
            for name in ('views', 'models', 'apis', 'admin_views'):
                try:
                    module = 'apps.%s.%s' % (app, name)
                    import_module(module)
                    if name is 'apis':
                        clsmembers = inspect.getmembers(sys.modules[module], inspect.isclass)
                        for name, cls in clsmembers:
                            if issubclass(cls, remote.Service):
                                logging.info("Adding Api %s to webegine configuration", cls.__name__)
                                self.apis_list.append(cls)
                except ImportError, e:
                    pass
                    #logging.info("Could not import [%s], error: %s", module, e)
        self.api = endpoints.api_server(self.apis_list)
        
    @classmethod
    def get_admin_views(cls):
        return cls._instance.admin_views
        
def route(*args, **kwargs):
    def wrapper(func=None):
        from webengine.handlers import BaseRequestHandler
        from webengine.utils import build_login_wrapper
        handler = kwargs.pop('handler', BaseRequestHandler)
        route_type = kwargs.pop('route_type', routes.RedirectRoute)
        admin_name = kwargs.pop('admin_name', False)
        admin_order = kwargs.pop('admin_order', len(WSGIWebEngine._instance.admin_views) + 1)
        roles = kwargs.pop('roles', [])
        if inspect.isclass(handler) and func is not None:
            #handler_class = type('WebEngineHandler', handler.__bases__, dict(handler.__dict__))
            handler_class = handler
            login_required = kwargs.pop('login_required', False)
            handler_func = build_login_wrapper(func, roles, *args, **kwargs) if roles else func
            setattr(handler_class, func.func_name, handler_func)
            setattr(handler_class, 'login_required', login_required)
            if admin_name:
                WSGIWebEngine._instance.admin_views.update({func.func_name:{'title':admin_name,'order':admin_order}})
            WSGIWebEngine._instance.router.add(route_type(handler=handler_class, handler_method=func.func_name, name=func.func_name, *args, **kwargs))
        elif isinstance(handler, str):
            WSGIWebEngine._instance.router.add(route_type(handler=handler, *args, **kwargs))
        return func
    return wrapper