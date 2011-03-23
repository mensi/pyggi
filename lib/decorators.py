# -*- coding: utf-8 -*-

from flask import render_template, make_response
from functools import wraps

def templated(template):
	def decorator(f):
		@wraps(f)
		def template_function(*args, **kwargs):
			if template is None:
				# if no template is given, we should rais an error
				#TODO: raise error
				pass

			# get the context from the executed function
			context = f(*args, **kwargs)
			if context is None:
				context = {}
			elif not isinstance(context, dict):
				return context

			# render the context using given template
			return render_template(template, **context)

		return template_function
	return decorator

def response_mimetype(mimetype):
	def decorator(f):
		@wraps(f)
		def wrapped(*args, **kwargs):
			result = f(*args, **kwargs)
			response = make_response(result)
			response.mimetype = mimetype
			return response

		return wrapped
	return decorator
