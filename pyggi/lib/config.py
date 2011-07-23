# -*- coding: utf-8 -*-

import ConfigParser
import os

config = ConfigParser.SafeConfigParser()

def load_config():
    path = os.path.abspath(os.path.dirname(__file__))
    config_file = os.path.abspath(os.path.join(path, '../../config.cfg'))
    config.read(config_file)

