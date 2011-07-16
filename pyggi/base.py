
import functools

from pyggi.lib.decorators import templated
from flask import Blueprint, redirect, url_for

base = Blueprint('base', __name__)
get = functools.partial(base.route, methods=['GET'])
post = functools.partial(base.route, methods=['POST'])

@get("/favicon.ico")
def favicon():
    return redirect(url_for('static', filename="favicon.ico"))

@get("/style")
def style():
    from flask import render_template
    from flask import make_response

    data = render_template("style/common.css")
    data = data.replace("\n", "")
    data = data.replace("\t", "")

    response = make_response(data)
    response.mimetype = 'text/css'

    return response

@get("/404")
@templated("404.xhtml")
def not_found():
    pass

