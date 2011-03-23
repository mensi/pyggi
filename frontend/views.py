from lib.decorators import templated
from flask import Module

frontend = Module(__name__, 'frontend')

@frontend.route("/")
@templated("frontend/base.xhtml")
def index():
	return dict()

@frontend.route("/browse")
@templated("frontend/browse.xhtml")
def browser():
	from lib.repository import GitRepository
	repo = GitRepository(repo="/home/tobias/git-frontend")
	return dict(commit=repo.getHead())
