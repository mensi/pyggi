
def create_app(**kwargs):
    """
        create a WSGI application that can be used in the
        modules.
    """

    from flask import Flask
    from pyggi.lib.config import config
    import logging

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
        module, prefix = module_desc
        if not prefix.endswith('/'):
            prefix += '/'
        module, attribute = module.rsplit('.', 1)

        # now we try to import the module and register it
        # in our application. otherwise ignore and continue
        try:
            _import = __import__(module, globals(), locals(), [attribute], -1)
            app.register_blueprint(getattr(_import, attribute))
        except Exception as e:
            logging.critical("could not load module '%s': %s", module_desc[0], e)

    # register some filters
    from pyggi.lib.filters import format_datetime, format_diff, is_text
    app.jinja_env.filters['dateformat'] = format_datetime
    app.jinja_env.filters['diffformat'] = format_diff
    app.jinja_env.tests['text'] = is_text

    return app

