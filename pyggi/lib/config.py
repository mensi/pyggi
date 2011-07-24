# -*- coding: utf-8 -*-

"""
    :copyright: (c) 2011 by Tobias Heinzen
    :license: BSD, see LICENSE for more details
"""

import ConfigParser
import os

config = ConfigParser.SafeConfigParser()

def load_config():
    path = os.path.abspath(os.path.dirname(__file__))
    config_file = os.path.abspath(os.path.join(path, '../../config.cfg'))
    config.read(config_file)

