from lib.decorators import templated
from flask import Module

frontend = Module(__name__, 'frontend')

@frontend.route("/")
@templated("frontend/base.xhtml")
def index():
	return dict()
