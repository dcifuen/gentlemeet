# -*- coding: utf-8 -*-

def namespace_manager_default_namespace_for_request():
    """
    Handles the namespace resolution based on the environment. This let us
    test without touching production data while we are in staging
    :return: staging if it is the current environment None otherwise
    """
    from settings import get_environment, Config
    environment = get_environment()
    namespace = 'staging' if environment == Config.ENV_STAGING else None
    return namespace