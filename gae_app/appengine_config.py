# -*- coding: utf-8 -*-

def namespace_manager_default_namespace_for_request():
    """
    Handles the namespace resolution based on the environment. This let us
    test without touching production data while we are in staging
    :return: staging if it is the current environment None otherwise
    """
    from ardux import get_environment, constants
    environment = get_environment()
    namespace = 'staging' if environment == constants.ENV_STAGING else \
        'eforcers.com'
    return namespace


def gae_mini_profiler_should_profile_production():
    """Uncomment the first two lines to enable GAE Mini Profiler on production
    for admin accounts"""
    from google.appengine.api import users
    return users.is_current_user_admin()


def webapp_add_wsgi_middleware(app):
    from google.appengine.ext.appstats import recording
    app = recording.appstats_wsgi_middleware(app)
    return app
