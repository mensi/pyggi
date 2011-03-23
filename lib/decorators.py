from flask import render_template
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
