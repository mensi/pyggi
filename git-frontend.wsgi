# -*- coding: utf-8 -*-

import os

try:
	from lib.wsgi import create_app
	application = create_app(config=os.path.join(os.getcwd(), 'config.cfg'))
except e:
	print e
	raise

if __name__ == "__main__":
	application.run(port=8080, debug=True)
