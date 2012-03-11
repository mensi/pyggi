# -*- coding: utf-8 -*-

"""
    :copyright: (c) 2012 by Tobias Heinzen
    :license: BSD, see LICENSE for more details
"""

from flask import Blueprint

class PyggletStore(object):
    def __init__(self):
        self.pygglets = []

    def register(self, pygglet):
        assert isinstance(pygglet, Pygglet)
        self.pygglets.append(pygglet)

__pygglets__ = PyggletStore()

class Pygglet(object):
    def __init__(self, name, import_name):
        from pyggi.lib.decorators import templated
        import functools

        self.blueprint = Blueprint(name, import_name, template_folder='templates')
        self.get = functools.partial(self.blueprint.route, methods=['GET'])
        self.post = functools.partial(self.blueprint.route, methods=['POST'])
        self.templated = templated

        __pygglets__.register(self)

        self._main_menu = None

    def set_main_menu(self, template):
        self._main_menu = template

