# -*- coding: utf-8 -*-

import os

from lib.decorators import templated, response_mimetype
from lib.repository import GitRepository
from flask import Module, current_app#, redirect_url, url_for

frontend = Module(__name__, 'frontend')

@frontend.route("/")
@templated("frontend/repositories.xhtml")
def index():
	# compute the names of repositories
	repnames = [GitRepository.getRepositoryFolder(name) \
		for name in os.walk(current_app.config['GIT_REPOSITORIES']).next()[1] \
		if GitRepository.isGitRepository(name)
	]
	print repnames

	return dict( \
		repositories = [ \
			GitRepository(repo=name) for name in repnames
		]
	)


@frontend.route("/<repository>/tree/<tree>/")
@templated("frontend/browse.xhtml")
def browse(repository, tree):
	# check if the repository exists
	repo_folder = GitRepository.getRepositoryFolder(repository)
	if repo_folder is None:
		pass

	repo = GitRepository(repo=repo_folder)
	return dict( \
		repo = repository,
		treeid = tree,
		commit = repo.getBranchHead(tree),
		tree = repo.getBranchHead(tree).tree.values(),
	)

@frontend.route("/<repository>/commit/<tree>/")
@templated("frontend/commit-info.xhtml")
def commit(repository, tree):
	# check if the repository exists
	repo_folder = GitRepository.getRepositoryFolder(repository)
	if repo_folder is None:
		pass

	repo = GitRepository(repo=repo_folder)
	return dict( \
		repo = repository,
		treeid = tree,
		commit = repo.getBranchHead(tree),
		diffs = repo.getBranchHead(tree).diffs
	)

@frontend.route("/<repository>/tree/<tree>/<path:path>/")
@templated("frontend/browse.xhtml")
def browse_sub(repository, tree, path):
	# check if the repository exists
	repo_folder = GitRepository.getRepositoryFolder(repository)
	if repo_folder is None:
		pass

	# the complete path, including the treeish
	path = "/".join([tree,path])

	repo = GitRepository(repo=repo_folder)
	return dict( \
		repo = repository,
		treeid = tree,
		commit = repo.getBranchHead(tree),
		tree = repo.getTreeByPath(path).values(),
		breadcrumbs = path.split("/")[1:]
	)

@frontend.route("/<repository>/history/<tree>/<path:path>")
@templated("frontend/history.xhtml")
def history(repository, tree, path):
	# check if the repository exists
	repo_folder = GitRepository.getRepositoryFolder(repository)
	if repo_folder is None:
		pass

	# the complete path, including the treeish
	path = "/".join([tree, path])

	repo = GitRepository(repo=repo_folder)
	return dict( \
		repo = repository,
		treeid = tree,
		history = repo.getHistory(path),
		breadcrumbs = path.split("/")[1:]
	)

@frontend.route("/<repository>/blob/<tree>/<path:path>")
@templated("frontend/blob.xhtml")
def blob(repository, tree, path):
	# check if the repository exists
	repo_folder = GitRepository.getRepositoryFolder(repository)
	if repo_folder is None:
		pass

	# the complete path, including the treeish
	path = "/".join([tree,path])

	repo = GitRepository(repo=repo_folder)
	return dict( \
		repo = repository,
		treeid = tree,
		commit = repo.getBranchHead(tree),
		blob = repo.getBlobByPath(path),
		breadcrumbs = path.split("/")[1:]
	)

@frontend.route("/<repository>/blame/<tree>/<path:path>")
@templated("frontend/blame.xhtml")
def blame(repository, tree, path):
	# check if the repository exists
	repo_folder = GitRepository.getRepositoryFolder(repository)
	if repo_folder is None:
		pass

	# the complete path, including the treeish
	path = "/".join([tree,path])

	repo = GitRepository(repo=repo_folder)
	return dict( \
		repo = repository,
		treeid = tree,
		commit = repo.getBranchHead(tree),
		blame = repo.getBlame(path),
		blob = repo.getBlobByPath(path),
		breadcrumbs = path.split("/")[1:]
	)

@frontend.route("/<repository>/raw/<tree>/<path:path>")
@response_mimetype("text/plain")
def raw(repository, tree, path):
	# check if the repository exists
	repo_folder = GitRepository.getRepositoryFolder(repository)
	if repo_folder is None:
		pass

	# the complete path, including the treeish
	path = "/".join([tree,path])

	repo = GitRepository(repo=repo_folder)
	return repo.getBlobByPath(path).data

