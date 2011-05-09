# -*- coding: utf-8 -*-

"""
	:copyright: (c) 2011 by Tobias Heinzen 
	:license: BSD, see LICENSE for more details
"""

from flask import current_app

if not current_app.config['CACHE_USE']:
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
		from werkzeug.contrib.cache import MemcachedCache
		cache = MemcachedCache(current_app.config['CACHE_URIS'])


