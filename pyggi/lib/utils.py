# -*- coding: utf-8 -*-

"""
    :copyright: (c) 2011 by Tobias Heinzen
    :license: BSD, see LICENSE for more details
"""

from flask import current_app
from pyggi.lib.config import config
import logging

class DummyCache(object):
    def get(*args, **kwargs):
        pass
    def set(*args, **kwargs):
        pass

if not (config.has_option('cache', 'enabled') and config.getboolean('cache','enabled')):
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
            logging.critical("could not connect to memcache daemon - disabling caching")

def get_repository_base():
    from flask import request
    return request.environ.get('wsgiorg.routing_args', (None, {}))[1].get('repository_base') or config.get('general', 'git_repositories')

def get_repository_path(name):
    import os
    return os.path.join(get_repository_base(), name)


