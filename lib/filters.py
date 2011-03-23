# -*- coding: utf-8 -*-

import time

def format_datetime(value, format='iso8601'):
	# convert format to iso8601 compliant
	if format == 'iso8601':
		format = "%Y-%m-%d %H:%M:%S"
	
	# convert format to iso8601 compliant (full)
	if format == 'iso8601-full':
		format = "%a %b %d %H:%M:%S %Z %Y"

	return time.strftime(format, value)
