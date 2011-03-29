# -*- coding: utf-8 -*-

import os

from lib.decorators import templated, response_mimetype
from lib.repository import GitRepository
from flask import Module, current_app, redirect, url_for

frontend = Module(__name__, 'pyggi', url_prefix="/pyggi")

def method_shortcut(method='GET'):
	def ruler(route, endpoint=None, **options):
		def decorator(f):
			frontend.add_url_rule(route, endpoint, f, **options)
			return f
		return decorator
	return ruler

get = method_shortcut('GET')
post = method_shortcut('POST')

@get("/", endpoint='index')
@templated("pyggi/repositories.xhtml")
def index():
	# compute the names of repositories
	repnames = [GitRepository.getRepositoryFolder(name) \
		for name in os.walk(current_app.config['GIT_REPOSITORIES']).next()[1] \
		if GitRepository.isGitRepository(name)
	]

	return dict( \
		repositories = [ \
			GitRepository(repo=name) for name in repnames
		]
	)

@get("/<repository>/", endpoint='repository')
def repository(repository):
	# check repository
	repo_folder = GitRepository.getRepositoryFolder(repository)
	if repo_folder is None:
		return redirect(url_for('not_found'))
	repo = GitRepository(repo=repo_folder)

	return redirect(url_for('browse', repository=repository, tree=repo.repo.active_branch))

@get("/404", endpoint='not_found')
@templated("pyggi/404.xhtml")
def not_found():
	pass

@get("/<repository>/tree/<tree>/", endpoint='browse')
@templated("pyggi/browse.xhtml")
def browse(repository, tree):
	# check if the repository exists
	repo_folder = GitRepository.getRepositoryFolder(repository)
	if repo_folder is None:
		return redirect(url_for('not_found'))
	repo = GitRepository(repo=repo_folder)

	# check if we can get the branch head
	head = repo.getBranchHead(tree)
	if head is None:
		return redirect(url_for('not_found'))

	return dict( \
		repo = repository,
		treeid = tree,
		commit = head,
		tree = head.tree.values(),
	)

@get("/<repository>/commit/<tree>/", endpoint='commit')
@templated("pyggi/commit-info.xhtml")
def commit(repository, tree):
	# check if the repository exists
	repo_folder = GitRepository.getRepositoryFolder(repository)
	if repo_folder is None:
		return redirect(url_for('not_found'))
	repo = GitRepository(repo=repo_folder)

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
	# check if the repository exists
	repo_folder = GitRepository.getRepositoryFolder(repository)
	if repo_folder is None:
		return redirect(url_for('not_found'))
	repo = GitRepository(repo=repo_folder)

	# the complete path, including the treeish
	path = "/".join([tree,path])

	# check for tree
	head = repo.getBranchHead(tree)
	if head is None:
		return redirect(url_for('not_found'))

	# save the tree-id
	treeid = tree

	# get tree by path and check for error
	tree = repo.getTreeByPath(path)
	if tree is None:
		return redirect(url_for('not_found'))

	return dict( \
		repo = repository,
		treeid = treeid,
		commit = head,
		tree = tree.values(),
		breadcrumbs = path.split("/")[1:]
	)

@get("/<repository>/history/<tree>/<path:path>", endpoint='history')
@templated("pyggi/history.xhtml")
def history(repository, tree, path):
	# check if the repository exists
	repo_folder = GitRepository.getRepositoryFolder(repository)
	if repo_folder is None:
		return redirect(url_for('not_found'))
	repo = GitRepository(repo=repo_folder)

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
	repo_folder = GitRepository.getRepositoryFolder(repository)
	if repo_folder is None:
		return redirect(url_for('not_found'))
	repo = GitRepository(repo=repo_folder)

	# the complete path, including the treeish
	path = "/".join([tree,path])

	# check for head
	head = repo.getBranchHead(tree)
	if head is None:
		return redirect(url_for('not_found'))

	# check for blob
	blob = repo.getBlobBypath(path)
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
	repo_folder = GitRepository.getRepositoryFolder(repository)
	if repo_folder is None:
		return redirect(url_for('not_found'))

	# the complete path, including the treeish
	path = "/".join([tree,path])

	# check for head
	head = repo.getBranchHead(tree)
	if head is None:
		return redirect(url_for('not_found'))

	# check for blob
	blob = repo.getBlobBypath(path)
	if blob is None:
		return redirect(url_for('not_found'))

	# check for blame
	blame = repo.getBlame(path)
	if blame is None:
		return redirect(url_for('not_found'))

	repo = GitRepository(repo=repo_folder)
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
	repo_folder = GitRepository.getRepositoryFolder(repository)
	if repo_folder is None:
		return redirect(url_for('not_found'))
	repo = GitRepository(repo=repo_folder)

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

