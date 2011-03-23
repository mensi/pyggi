# -*- coding: utf-8 -*-

import os

from lib.wsgi import create_app
application = create_app(config=os.path.join(os.getcwd(), 'config.cfg'))

if __name__ == "__main__":
	application.run(port=8080)
