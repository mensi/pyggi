# -*- coding: utf-8 -*-

"""
    :copyright: (c) 2011 by Tobias Heinzen
    :license: BSD, see LICENSE for more details
"""

import os
import functools

from pyggi.lib.decorators import templated, cached
from pyggi.lib.repository.gitr import GitRepository
from flask import Blueprint, redirect, url_for
from pyggi.lib.config import config

frontend = Blueprint('repos', __name__)
get = functools.partial(frontend.route, methods=['GET'])
post = functools.partial(frontend.route, methods=['POST'])

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

@get("/")
@templated("repositories.xhtml")
def index():
    # compute the names of repositories
    repnames = [name \
        for name in os.walk(config.get('general','git_repositories')).next()[1] \
        if GitRepository.isRepository(name)
    ]

    return dict( \
        repositories = [ \
            GitRepository(repository=GitRepository.path(name)) for name in repnames
        ]
    )

@get("/<repository>/")
def repository(repository):
    repo = GitRepository(repository=GitRepository.path(repository))
    return redirect(url_for('.overview', repository=repository, tree=repo.active_branch))


@get("/<repository>/overview/<tree>/")
@cached(cache_keyfn('overview'))
@templated("overview.xhtml")
def overview(repository, tree):
    repo = GitRepository(repository=GitRepository.path(repository))

    return dict( \
        repository = repo,
        treeid = tree
    )

@get("/<repository>/tree/<tree>/")
@cached(cache_keyfn('browse'))
@templated("browse.xhtml")
def browse(repository, tree):
    repo = GitRepository(repository=GitRepository.path(repository))

    return dict( \
        repository = repo,
        treeid = tree,
        browse = True
    )

@get("/<repository>/tree/<tree>/<path:path>/")
@cached(cache_keyfn('tree', ['path']))
@templated("browse.xhtml")
def browse_sub(repository, tree, path):
    repo = GitRepository(repository=GitRepository.path(repository))

    return dict( \
        repository = repo,
        treeid = tree,
        breadcrumbs = path.split("/"),
        browse = True
    )

@get("/<repository>/commit/<tree>/")
@cached(cache_keyfn('commit'))
@templated("commit.xhtml")
def commit(repository, tree):
    repo = GitRepository(repository=GitRepository.path(repository))

    return dict( \
        repository = repo,
        treeid = tree,
    )

@get("/<repository>/blob/<tree>/<path:path>")
@cached(cache_keyfn('blob', ['path']))
@templated("blob.xhtml")
def blob(repository, tree, path):
    repo = GitRepository(repository=GitRepository.path(repository))

    return dict( \
        repository = repo,
        treeid = tree,
        breadcrumbs = path.split("/")
    )

@get("/<repository>/blame/<tree>/<path:path>")
@cached(cache_keyfn('blame', ['path']))
@templated("blame.xhtml")
def blame(repository, tree, path):
    repo = GitRepository(repository=GitRepository.path(repository))

    return dict( \
        repository = repo,
        treeid = tree,
        breadcrumbs = path.split("/")
    )

@get("/<repository>/raw/<tree>/<path:path>")
@cached(cache_keyfn('raw', ['path']))
def raw(repository, tree, path):
    repo = GitRepository(repository=GitRepository.path(repository))
    blob = repo.blob('/'.join([tree,path]))

    # create a response with the correct mime type
    from flask import make_response
    response = make_response(blob.data)
    response.mimetype = blob.mime_type
    return response

@get("/<repository>/download/<tree>")
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

