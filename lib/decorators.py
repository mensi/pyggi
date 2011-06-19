# -*- coding: utf-8 -*-

"""
    :copyright: (c) 2011 by Tobias Heinzen
    :license: BSD, see LICENSE for more details
"""

from flask import render_template
from functools import wraps

def method_shortcut(application, method='GET'):
    def ruler(route, endpoint=None, **options):
        def decorator(f):
            application.add_url_rule(route, endpoint, f, **options)
            return f
        return decorator
    return ruler

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

            # add the page name into the context
            context['page_name'] = config.getstring('general', 'name')

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

