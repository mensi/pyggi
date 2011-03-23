# -*- coding: utf-8 -*-

import os

from lib.decorators import templated
from flask import Module, current_app#, redirect_url, url_for

frontend = Module(__name__, 'frontend')

@frontend.route("/")
@templated("frontend/base.xhtml")
def index():
	return dict()

@frontend.route("/<repository>/tree/<tree>")
@templated("frontend/browse.xhtml")
def browser(repository, tree):
	# check if the repository exists
	repo_folder = os.path.join(current_app.config['GIT_REPOSITORIES'], repository)
	if not os.path.exists(repo_folder):
		#return redirect_url(url_for('frontend.index'))
		pass

	from lib.repository import GitRepository
	repo = GitRepository(repo=repo_folder)
	return dict( \
		repo = repository,
		treeid = tree,
		commit=repo.getBranchHead(tree)
	)
