# -*- coding: utf-8 -*-

"""
    :copyright: (c) 2011 by Tobias Heinzen
    :license: BSD, see LICENSE for more details
"""

class Pygglet(object):
    def register_main_menu_entry(self, template):
        """
        """
        self.menues.append(template)

    def __init__(self):
        self.menues = []

pygglet = Pygglet()
