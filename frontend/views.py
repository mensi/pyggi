# -*- coding: utf-8 -*-

import os

from lib.decorators import templated, response_mimetype
from lib.repository import GitRepository
from flask import Module, current_app, redirect

frontend = Module(__name__, 'frontend')

@frontend.route("/")
@templated("frontend/repositories.xhtml")
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

@frontend.route("/<repository>/")
def repository(repository):
	return redirect("/%s/tree/master/" % repository)

@frontend.route("/<repository>/error/repo")
@templated("frontend/errors/unknown_repo.xhtml")
def error_unknown_repo(repository):
	return dict( \
		repo = repository
	)

@frontend.route("/<repository>/error/tree")
@templated("frontend/errors/unknown_tree.xhtml")
def error_unknown_tree(repository):
	# check repo
	repo_folder = GitRepository.getRepositoryFolder(repository)
	if repo_folder is None:
		return redirect('/%s/error/repo' % repository)
	repo = GitRepository(repo=repo_folder)

	# the special tree 'master' will always exist, and thus
	# we can get a commit object
	head = repo.getBranchHead("master")

	# try to get the tree name
	try:
		from flask import request
		tree = request.values['t']
	except:
		tree = ""

	return dict( \
		repo = repository,
		commit = head,
		tree = tree
	)

@frontend.route("/<repository>/error/path")
@templated("frontend/errors/unknown_path.xhtml")
def error_unknown_path(repository):
	# check repo
	repo_folder = GitRepository.getRepositoryFolder(repository)
	if repo_folder is None:
		return redirect('/%s/error/repo' % repository)
	repo = GitRepository(repo=repo_folder)

	# we will now check if we can get the tree
	# by checking the contents of the transmitted variable.
	# if nothing was transmitted, then we obviously got
	# another error, and we have to handle that
	try:
		from flask import request
		path = request.values['p']

		# if the path is empty, or has not at least
		# two entries, then we're done also
		path = path.split("/", 1)
		if not len(path) == 2:
			raise KeyError("")
	except KeyError as error:
		return redirect('/%s/error/tree?t=' % repository)

	# the first entry in the path will give us the tree
	# we want to reference
	head = repo.getBranchHead(path[0])
	if head is None:
		return redirect('/%s/error/tree?t=%s' % (repository, path[0]))

	return dict( \
		repo = repository,
		commit = head,
		path = path[1]
	)

@frontend.route("/<repository>/tree/<tree>/")
@templated("frontend/browse.xhtml")
def browse(repository, tree):
	# check if the repository exists
	repo_folder = GitRepository.getRepositoryFolder(repository)
	if repo_folder is None:
		return redirect('/%s/error/repo' % repository)
	repo = GitRepository(repo=repo_folder)

	# check if we can get the branch head
	head = repo.getBranchHead(tree)
	if head is None:
		return redirect('/%s/error/tree?t=%s' % (repository, tree))

	return dict( \
		repo = repository,
		treeid = tree,
		commit = head,
		tree = head.tree.values(),
	)

@frontend.route("/<repository>/commit/<tree>/")
@templated("frontend/commit-info.xhtml")
def commit(repository, tree):
	# check if the repository exists
	repo_folder = GitRepository.getRepositoryFolder(repository)
	if repo_folder is None:
		return redirect('/%s/error/repo' % repository)
	repo = GitRepository(repo=repo_folder)

	# check for tree
	head = repo.getBranchHead(tree)
	if head is None:
		return redirect('/%s/error/tree?t=%s' % (repository, tree))

	return dict( \
		repo = repository,
		treeid = tree,
		commit = head,
		diffs = head.diffs
	)

@frontend.route("/<repository>/tree/<tree>/<path:path>/")
@templated("frontend/browse.xhtml")
def browse_sub(repository, tree, path):
	# check if the repository exists
	repo_folder = GitRepository.getRepositoryFolder(repository)
	if repo_folder is None:
		return redirect('/%s/error/repo' % repository)
	repo = GitRepository(repo=repo_folder)

	# the complete path, including the treeish
	path = "/".join([tree,path])

	# check for tree
	head = repo.getBranchHead(tree)
	if head is None:
		return redirect('/%s/error/tree?t=%s' % (repository, tree))

	# get tree by path and check for error
	tree = repo.getTreeByPath(path)
	if tree is None:
		return redirect('/%s/error/path?p=%s' % (repository, path))

	return dict( \
		repo = repository,
		treeid = tree,
		commit = head,
		tree = tree.values(),
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
		commit = repo.getBranchHead(tree),
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

