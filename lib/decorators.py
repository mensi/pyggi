# -*- coding: utf-8 -*-

"""
	:copyright: (c) 2011 by Tobias Heinzen 
	:license: BSD, see LICENSE for more details
"""

from flask import render_template
from functools import wraps

def templated(template):
	def decorator(f):
		@wraps(f)
		def template_function(*args, **kwargs):
			# error when no template is given
			if template is None:
				raise Exception("no template given")

			# get the context from the executed function
			context = None
			context = f(*args, **kwargs)

			if context is None:
				context = {}
			elif not isinstance(context, dict):
				return context

			# render the context using given template
			response = render_template(template, **context)
			return response

		return template_function
	return decorator

def cached(keyfn):
	def decorator(f):
		@wraps(f)
		def cache_function(*args, **kwargs):
			key = keyfn(*args, **kwargs)
			if key is None:
				result = f(*args, **kwargs)
			else:
				from lib.utils import cache
				from lib.config import config
				result = cache.get(key)
				if result is None:
					result = f(*args, **kwargs)
					cache.set(key, result, timeout=config.getint('cache','timeout'))
			return result

		return cache_function
	return decorator

