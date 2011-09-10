# -*- coding: utf-8 -*-

"""
    :copyright: (c) 2011 by Tobias Heinzen
    :license: BSD, see LICENSE for more details
"""

def create_app(**kwargs):
    """
        create a WSGI application that can be used in the
        modules.
    """

    from flask import Flask
    from pyggi.lib.config import config
    import logging

    static_base = '/static'
    if config.has_option('general', 'static_url_base'):
        static_base = config.get('general', 'static_url_base')
    app = Flask(__name__, static_url_path=static_base)

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
        module, prefix = module_desc
        module, attribute = module.rsplit('.', 1)

        # now we try to import the module and register it
        # in our application. otherwise ignore and continue
        try:
            _import = __import__(module, globals(), locals(), [attribute], -1)
            app.register_blueprint(getattr(_import, attribute), url_prefix="/"+prefix.strip('/'))
        except Exception as e:
            logging.critical("could not load module '%s': %s", module_desc[0], e)

    # register some filters
    import lib.filters
    app.jinja_env.filters['dateformat'] = lib.filters.format_datetime
    app.jinja_env.filters['diffformat'] = lib.filters.format_diff
    app.jinja_env.filters['timesince'] = lib.filters.humanize_timesince
    app.jinja_env.filters['force_unicode'] = lib.filters.force_unicode
    app.jinja_env.filters['first_line'] = lib.filters.first_line
    app.jinja_env.tests['text'] = lib.filters.is_text
    app.context_processor(lambda: dict(static_url_for=lib.filters.static_url_for))

    return app

