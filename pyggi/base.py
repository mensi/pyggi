
import functools

from pyggi.lib.decorators import templated
import pyggi.lib.filters
from flask import Blueprint, redirect

base = Blueprint('base', __name__)
get = functools.partial(base.route, methods=['GET'])
post = functools.partial(base.route, methods=['POST'])

@get("/favicon.ico")
def favicon():
    return redirect(pyggi.lib.filters.static_url_for("favicon.ico"))

@get("/404")
@templated("404.xhtml")
def not_found():
    pass

