# -*- coding: utf-8 -*-

"""
    :copyright: (c) 2011 by Tobias Heinzen
    :license: BSD, see LICENSE for more details
"""

from flask import Flask, current_app
from pyggi.lib.config import config
import logging

def error_handler(error):
    if current_app.debug:
        raise
    else:
        from pyggi.lib.repository import RepositoryError
        from flask import redirect, url_for

        if not isinstance(error, RepositoryError):
            logging.error("error in handling request: %s", error)
        else:
            logging.warning("repository error: %s", error)

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
        level = logging.WARNING,
        format = "[%(asctime)s] %(levelname)s: %(message)s",
        datefmt = "%Y-%m-%d %H:%M:%S"
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
            logging.critical("could not load module '%s': %s", module_desc[0], e)

    # register exception handler
    app.handle_exception = error_handler

    # register some filters
    from pyggi.lib.filters import format_datetime, format_diff, is_text
    app.jinja_env.filters['dateformat'] = format_datetime
    app.jinja_env.filters['diffformat'] = format_diff
    app.jinja_env.tests['text'] = is_text

    return app

