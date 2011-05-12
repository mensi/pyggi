# -*- coding: utf-8 -*-

"""
    :copyright: (c) 2011 by Tobias Heinzen
    :license: BSD, see LICENSE for more details
"""

from flask import Flask, current_app
from lib.config import config
import logging

def error_handler(error):
    if current_app.debug:
        raise
    else:
        from lib.repository import RepositoryError
        from flask import redirect, url_for

        if not isinstance(error, RepositoryError):
            # TODO: log the error
            pass

        return redirect(url_for('not_found'))

def create_app(**kwargs):
    """
        create a WSGI application that can be used in the
        modules.
    """
    app = Flask(__name__)

    # activate logging
    logging.basicConfig(
        filename = config.get('log', 'file'),
        level = config.get('log', 'level'),
        format = "[%(asctime)s] %(levelname)s: %(message)s",
        datefmt = "%Y-%M-%d %H:%M:%S"
    )

    # register modules to application. the modules come
    # from the configuration file. there is a list of
    # modules to be imported. an item in this list has the
    # form ("module:name","prefix") where name is the name of the module
    # object that should be imported
    for module_desc in config.items('modules'):
        module_name, module_import = module_desc

        # now we try to import the module and register it
        # in our application. otherwise ignore and continue
        try:
            _import = __import__(module_name, globals(), locals(), [module_import], -1)
            app.register_module(getattr(_import, module_import))
        except Exception as e:
            pass

    # register exception handler
    app.handle_exception = error_handler

    # register some filters
    from lib.filters import format_datetime, format_diff
    app.jinja_env.filters['dateformat'] = format_datetime
    app.jinja_env.filters['diffformat'] = format_diff

    return app

