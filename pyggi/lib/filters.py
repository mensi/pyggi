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

def force_unicode(txt):
    try:
        return unicode(txt)
    except UnicodeDecodeError:
        pass
    orig = txt
    if type(txt) != str:
        txt = str(txt)
    for args in [('utf-8',), ('latin1',), ('ascii', 'replace')]:
        try:
            return txt.decode(*args)
        except UnicodeDecodeError:
            pass
    raise ValueError("Unable to force %s object %r to unicode" % (type(orig).__name__, orig))

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

def humanize_timesince(when):
    import datetime

    # convert when to datetime
    if type(when) == int:
        when = datetime.datetime.utcfromtimestamp(when)
    else:
        when = datetime.datetime(*when[:6])

    now = datetime.datetime.utcnow()
    difference = now - when
    if difference < datetime.timedelta(minutes=2):
        return "%s seconds ago" % difference.seconds
    elif difference < datetime.timedelta(hours=2):
        return "%s minutes ago" % (difference.seconds / 60)
    elif difference < datetime.timedelta(days=2):
        return "%s hours ago" % (difference.days * 24 + difference.seconds / 3600)
    elif difference < datetime.timedelta(days=2*7):
        return "%s days ago" % difference.days
    elif difference < datetime.timedelta(days=2*30):
        return "%s weeks ago" % (difference.days / 7)
    elif difference < datetime.timedelta(days=2*365):
        return "%s months ago" % (difference.days / 30)
    else:
        return "%s years ago" % (difference.days / 365)

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

    # javascript documents
    if mimetype == "application/javascript":
        return True

    return False

def first_line(string):
    string = string.replace('\r', '\n', 1)
    try:
        return string[:string.index('\n')]
    except ValueError:
        return string

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
