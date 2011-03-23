# -*- coding: utf-8 -*-

import os

from lib.decorators import templated
from lib.repository import GitRepository
from flask import Module #, current_app#, redirect_url, url_for

frontend = Module(__name__, 'frontend')

@frontend.route("/")
@templated("frontend/base.xhtml")
def index():
	return dict()


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

