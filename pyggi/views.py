# -*- coding: utf-8 -*-

"""
    :copyright: (c) 2011 by Tobias Heinzen
    :license: BSD, see LICENSE for more details
"""

import os

from lib.decorators import templated, cached, method_shortcut
from lib.repository.gitr import GitRepository
from flask import Module, redirect, url_for
from lib.config import config

frontend = Module(__name__, 'pyggi', url_prefix=None)
get = method_shortcut(frontend, 'GET')
post = method_shortcut(frontend, 'POST')

def cache_keyfn(prefix, additional_fields=[]):
    def test(*args, **kwargs):
        id = GitRepository.resolve_ref(GitRepository.path(kwargs['repository']), kwargs['tree'])

        path = ""
        for field in additional_fields:
            path = path + "-" + kwargs[field]

        if id is not None:
            return prefix+"-"+kwargs['repository']+"-"+id+path
        return None
    return test

@get("/favicon.ico/")
def favicon():
    return redirect(url_for('static', filename="favicon.ico"))

@get("/style/", endpoint='style')
def style():
    from flask import render_template
    from flask import make_response

    data = render_template("pyggi/style/common.css")
    response = make_response(data)
    response.mimetype = 'text/css'

    return response

@get("/404", endpoint='not_found')
@templated("pyggi/404.xhtml")
def not_found():
    pass

@get("/", endpoint='index')
@templated("pyggi/repositories.xhtml")
def index():
    # compute the names of repositories
    repnames = [name \
        for name in os.walk(config.get('general','GIT_REPOSITORIES')).next()[1] \
        if GitRepository.isRepository(name)
    ]

    return dict( \
        repositories = [ \
            GitRepository(repository=GitRepository.path(name)) for name in repnames
        ]
    )

@get("/<repository>/", endpoint='repository')
def repository(repository):
    repo = GitRepository(repository=GitRepository.path(repository))
    return redirect(url_for('overview', repository=repository, tree=repo.active_branch))


@get("/<repository>/overview/<tree>/", endpoint='overview')
@cached(cache_keyfn('overview'))
@templated("pyggi/overview.xhtml")
def overview(repository, tree):
    return ""

@get("/<repository>/tree/<tree>/", endpoint='browse')
@cached(cache_keyfn('browse'))
@templated("pyggi/browse.xhtml")
def browse(repository, tree):
    repo = GitRepository(repository=GitRepository.path(repository))

    return dict( \
        repository = repo,
        treeid = tree,
        browse = True
    )

@get("/<repository>/tree/<tree>/<path:path>/", endpoint='browse_sub')
@cached(cache_keyfn('tree', ['path']))
@templated("pyggi/browse.xhtml")
def browse_sub(repository, tree, path):
    repo = GitRepository(repository=GitRepository.path(repository))

    return dict( \
        repository = repo,
        treeid = tree,
        breadcrumbs = path.split("/"),
        browse = True
    )

@get("/<repository>/commit/<tree>/", endpoint='commit')
@cached(cache_keyfn('commit'))
@templated("pyggi/commit-info.xhtml")
def commit(repository, tree):
    repo = GitRepository(repository=GitRepository.path(repository))

    return dict( \
        repository = repo,
        treeid = tree,
    )

@get("/<repository>/history/<tree>/<path:path>", endpoint='history')
@cached(cache_keyfn('history', ['path']))
@templated("pyggi/history.xhtml")
def history(repository, tree, path):
    repo = GitRepository(repository=GitRepository.path(repository))

    return dict( \
        repository = repo,
        treeid = tree,
        breadcrumbs = path.split("/")
    )

@get("/<repository>/blob/<tree>/<path:path>", endpoint='blob')
@cached(cache_keyfn('blob', ['path']))
@templated("pyggi/blob.xhtml")
def blob(repository, tree, path):
    repo = GitRepository(repository=GitRepository.path(repository))

    return dict( \
        repository = repo,
        treeid = tree,
        breadcrumbs = path.split("/")
    )

@get("/<repository>/blame/<tree>/<path:path>", endpoint='blame')
@cached(cache_keyfn('blame', ['path']))
@templated("pyggi/blame.xhtml")
def blame(repository, tree, path):
    repo = GitRepository(repository=GitRepository.path(repository))

    return dict( \
        repository = repo,
        treeid = tree,
        breadcrumbs = path.split("/")
    )

@get("/<repository>/raw/<tree>/<path:path>", endpoint='raw')
@cached(cache_keyfn('raw', ['path']))
def raw(repository, tree, path):
    repo = GitRepository(repository=GitRepository.path(repository))
    blob = repo.blob('/'.join([tree,path]))

    # create a response with the correct mime type
    from flask import make_response
    response = make_response(blob.data)
    response.mimetype = blob.mime_type
    return response

@get("/<repository>/download/<tree>", endpoint='download')
@cached(cache_keyfn('download'))
def download(repository, tree):
    repo = GitRepository(repository=GitRepository.path(repository))
    data = repo.archive(tree)

    # create a response with the correct mime type
    # and a better filename
    from flask import make_response
    response = make_response(data)
    response.mimetype = 'application/x-gzip'
    response.headers['Content-Disposition'] = "attachment; filename=%s-%s.tar.gz" % (repository, tree[:8])

    return response


