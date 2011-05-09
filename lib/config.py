# -*- coding: utf-8 -*-

import ConfigParser
import os

config_file = os.path.join(os.getcwd(), 'config.cfg')
config = ConfigParser.ConfigParser()
config.read(config_file)

