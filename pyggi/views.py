# -*- coding: utf-8 -*-

import os

from lib.decorators import templated, response_mimetype
from lib.repository.gitr import GitRepository
from flask import Module, current_app, redirect, url_for

frontend = Module(__name__, 'pyggi', url_prefix=None)

def method_shortcut(method='GET'):
	def ruler(route, endpoint=None, **options):
		def decorator(f):
			frontend.add_url_rule(route, endpoint, f, **options)
			return f
		return decorator
	return ruler

get = method_shortcut('GET')
post = method_shortcut('POST')

@get("/favicon.ico/")
def favicon():
	return redirect(url_for('static', filename="favicon.ico"))

@get("/", endpoint='index')
@templated("pyggi/repositories.xhtml")
def index():
	# compute the names of repositories
	repnames = [name \
		for name in os.walk(current_app.config['GIT_REPOSITORIES']).next()[1] \
		if GitRepository.isRepository(name)
	]

	return dict( \
		repositories = [ \
			GitRepository(repository=GitRepository.path(name)) for name in repnames
		]
	)

@get("/<repository>/", endpoint='repository')
def repository(repository):
	# check repository
	repo = GitRepository.getRepository(repository)
	if repo is None:
		return redirect(url_for('not_found'))

	return redirect(url_for('browse', repository=repository, tree=repo.repo.active_branch))

@get("/404", endpoint='not_found')
@templated("pyggi/404.xhtml")
def not_found():
	pass

@get("/<repository>/tree/<tree>/", endpoint='browse')
@templated("pyggi/browse.xhtml")
def browse(repository, tree):
	try:
		repo = GitRepository(repository=GitRepository.path(repository))
	except:
		return redirect(url_for('not_found'))

	return dict( \
		repository = repo,
		treeid = tree
	)

@get("/<repository>/commit/<tree>/", endpoint='commit')
@templated("pyggi/commit-info.xhtml")
def commit(repository, tree):
	# check if the repository exists
	repo = GitRepository.getRepository(repository)
	if repo is None:
		return redirect(url_for('not_found'))

	# check for tree
	head = repo.getBranchHead(tree)
	if head is None:
		return redirect(url_for('not_found'))

	return dict( \
		repo = repository,
		treeid = tree,
		commit = head,
		diffs = head.diffs
	)

@get("/<repository>/tree/<tree>/<path:path>/", endpoint='browse_sub')
@templated("pyggi/browse.xhtml")
def browse_sub(repository, tree, path):
	try:
		repo = GitRepository(repository=GitRepository.path(repository))
	except:
		return redirect(url_for('not_found'))

	return dict( \
		repository = repo,
		treeid = tree,
		breadcrumbs = path.split("/")
	)

@get("/<repository>/history/<tree>/<path:path>", endpoint='history')
@templated("pyggi/history.xhtml")
def history(repository, tree, path):
	# check if the repository exists
	repo = GitRepository.getRepository(repository)
	if repo is None:
		return redirect(url_for('not_found'))

	# the complete path, including the treeish
	path = "/".join([tree, path])

	# check for head
	head = repo.getBranchHead(tree)
	if head is None:
		return redirect(url_for('not_found'))

	# get history object
	history = repo.getHistory(path)
	if history is None:
		return redirect(url_for('not_found'))

	return dict( \
		repo = repository,
		treeid = tree,
		commit = head,
		history = history,
		breadcrumbs = path.split("/")[1:]
	)

@get("/<repository>/blob/<tree>/<path:path>", endpoint='blob')
@templated("pyggi/blob.xhtml")
def blob(repository, tree, path):
	# check if the repository exists
	repo = GitRepository.getRepository(repository)
	if repo is None:
		return redirect(url_for('not_found'))

	# the complete path, including the treeish
	path = "/".join([tree,path])

	# check for head
	head = repo.getBranchHead(tree)
	if head is None:
		return redirect(url_for('not_found'))

	# check for blob
	blob = repo.getBlobByPath(path)
	if blob is None:
		return redirect(url_for('not_found'))

	return dict( \
		repo = repository,
		treeid = tree,
		commit = head,
		blob = blob,
		breadcrumbs = path.split("/")[1:]
	)

@get("/<repository>/blame/<tree>/<path:path>", endpoint='blame')
@templated("pyggi/blame.xhtml")
def blame(repository, tree, path):
	# check if the repository exists
	repo = GitRepository.getRepository(repository)
	if repo is None:
		return redirect(url_for('not_found'))

	# the complete path, including the treeish
	path = "/".join([tree,path])

	# check for head
	head = repo.getBranchHead(tree)
	if head is None:
		return redirect(url_for('not_found'))

	# check for blob
	blob = repo.getBlobByPath(path)
	if blob is None:
		return redirect(url_for('not_found'))

	# check for blame
	blame = repo.getBlame(path)
	if blame is None:
		return redirect(url_for('not_found'))

	return dict( \
		repo = repository,
		treeid = tree,
		commit = head,
		blame = blame,
		blob = blob,
		breadcrumbs = path.split("/")[1:]
	)

@get("/<repository>/raw/<tree>/<path:path>", endpoint='raw')
def raw(repository, tree, path):
	# check if the repository exists
	repo = GitRepository.getRepository(repository)
	if repo is None:
		return redirect(url_for('not_found'))

	# the complete path, including the treeish
	path = "/".join([tree,path])

	# check blob
	blob = repo.getBlobByPath(path)
	if blob is None:
		return redirect(url_for('not_found'))

	# create a response with the correct mime type
	from flask import make_response
	response = make_response(blob.data)
	response.mimetype = blob.mime_type
	return response

@get("/<repository>/download/<tree>", endpoint='download')
def download(repository, tree):
	# check if the repository exists
	repo = GitRepository.getRepository(repository)
	if repo is None:
		return redirect(url_for('not_found'))

	# check tar.gz
	data = repo.getTarGz(tree)
	if data is None:
		return redirect(url_for('not_found'))

	# create a response with the correct mime type
	# and a better filename
	from flask import make_response
	response = make_response(data)
	response.mimetype = 'application/x-gzip'
	response.headers['Content-Disposition'] = "attachment; filename=%s-%s.tar.gz" % (repository, tree[:8])

	return response

