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

def format_filesize(value):
	for x in ['bytes', 'kb', 'mb', 'gb', 'tb']:
		if value < 1024.0:
			return "%3.1f %s" % (value, x)
		value /= 1024.0

def is_git_tree(value):
	from git import Tree
	return isinstance(value, Tree)

