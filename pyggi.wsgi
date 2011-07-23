# -*- coding: utf-8 -*-

import sys, os, os.path

path = os.path.abspath(os.path.dirname(__file__))
if path not in sys.path:
    sys.path.append(path)

# load configuration before all else
from pyggi.lib.config import load_config
load_config()

try:
    from pyggi import create_app
    application = create_app()
except Exception as e:
    raise

if __name__ == "__main__":
    application.run(port=8080, debug=True)

# vim: set ft=python:
