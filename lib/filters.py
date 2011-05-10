# -*- coding: utf-8 -*-

"""
    :copyright: (c) 2011 by Tobias Heinzen
    :license: BSD, see LICENSE for more details
"""

import time

html_escape_table = {
    "&": "&amp;",
    '"': "&quot;",
    "'": "&apos;",
    ">": "&gt;",
    "<": "&lt;",
}

def format_datetime(value, format='iso8601'):
    # convert format to iso8601 compliant
    if format == 'iso8601':
        format = "%Y-%m-%d %H:%M:%S"

    # convert format to iso8601 compliant (full)
    if format == 'iso8601-full':
        format = "%a %b %d %H:%M:%S %Z %Y"

    # if we have a timestamp, we have to convert it
    # to a time_struct
    if isinstance(value, int):
        from datetime import datetime
        value = datetime.fromtimestamp(value).timetuple()

    return time.strftime(format, value)

def format_diff(value):
    # escape HTML, because format_diff shall be used with 'safe'
    value = unicode(value, 'utf-8') # correct?
    value = "".join(html_escape_table.get(c,c) for c in value)

    if value.startswith("+") and not value.startswith("+++"):
        return '<div class="diff-add">%s&nbsp;</div>' % value
    elif value.startswith("-") and not value.startswith("---"):
        return '<div class="diff-remove">%s&nbsp;</div>' % value
    elif value.startswith("@@"):
        return '<div class="diff-change">%s&nbsp;</div>' % value

    return '<div>%s</div>' % value

