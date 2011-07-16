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
        return '<li class="diff-add">%s&nbsp;</li>' % value
    elif value.startswith("-") and not value.startswith("---"):
        return '<li class="diff-remove">%s&nbsp;</li>' % value
    elif value.startswith("@@"):
        return '<li class="diff-change">%s&nbsp;</li>' % value

    return '<li>%s</li>' % value

def is_text(mimetype):
    """
        determine if a mimetype holds printable text (ascii)
    """

    # all text documents
    if mimetype.startswith("text/"):
        return True

    # xml/html/xhtml documents
    if mimetype.startswith("application/") and \
        (mimetype.find("html") != -1 or mimetype.find("xml") != -1):
        return True

    return False

def static_url_for(filename):
    from flask import url_for, request
    from config import config
    import urllib

    url_base = request.environ.get('wsgiorg.routing_args', ([], {}))[1].get('static_url_base')
    if not url_base and config.has_option('general', 'static_url_base'):
        url_base = config.get('general', 'static_url_base')
    if url_base:
        return url_base.rstrip('/') + '/' + urllib.quote(filename)
    else:
        return url_for('static', filename=filename)
