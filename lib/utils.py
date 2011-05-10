# -*- coding: utf-8 -*-

"""
    :copyright: (c) 2011 by Tobias Heinzen
    :license: BSD, see LICENSE for more details
"""

from flask import current_app
from lib.config import config

if not config.getboolean('cache','enabled'):
    class DummyCache(object):
        def get(*args, **kwargs):
            pass
        def set(*args, **kwargs):
            pass

    cache = DummyCache()
else:
    if current_app.debug:
        from werkzeug.contrib.cache import SimpleCache
        cache = SimpleCache()
    else:
        try:
            from werkzeug.contrib.cache import MemcachedCache
            cache = MemcachedCache([x.strip() for x in config.get('cache','uris').split(",") if not len(x.strip()) == 0])
        except:
            cache = DummyCache()
            # TODO: create log message

