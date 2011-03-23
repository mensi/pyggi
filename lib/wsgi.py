from flask import Flask

def create_app(**kwargs):
	"""
		create a WSGI application that can be used in the
		modules.

		@param kwargs
			config=<filename> the application is configured by using the passed
							  configfile
	"""
	app = Flask(__name__)

	# if a config file was specified, then let it flask know
	if 'config' in kwargs:
		app.config.from_pyfile(kwargs['config'])

	# register modules to application. the modules come
	# from the configuration file. there is a list of
	# modules to be imported. an item in this list has the
	# form ("module:name","prefix") where name is the name of the module
	# object that should be imported
	if 'MODULES' in app.config:
		for module_desc,prefix in app.config['MODULES']:
			# split at ':'
			module_name, module_import = module_desc.split(':', 1)

			# now we try to import the module and register it
			# in our application. otherwise ignore and continue
			try:
				_import = __import__(module_name, globals(), locals(), [module_import], -1)
				app.register_module(getattr(_import, module_import), url_prefix=prefix)
			except:
				pass

	# register some filters
	from lib.filters import format_datetime
	app.jinja_env.filters['dateformat'] = format_datetime

	return app
