# -*- coding: utf-8 -*-

from git import Repo
from flask import current_app

class GitRepository(object):
	def __init__(self, **kwargs):
		"""
			creates a git repository object, that wraps around GitPython to
			provide a more relaxed acces to features.

			@param kwargs
				repo=<dir> the directory of the repository to parse
		"""

		# load up repo
		self.repo = Repo(kwargs['repo'])

	@staticmethod
	def getRepositoryFolder(repository):
		import os
		repo_folder = os.path.join(current_app.config['GIT_REPOSITORIES'], repository)
		if not os.path.exists(repo_folder):
			return None
		return repo_folder

	def getHead(self):
		return self.repo.commits()[0]

	def getBranchHead(self, name):
		return self.repo.commits(name)[0]

	def getTreeByPath(self, path):
		"""
			traverse tree defined by path
		"""
		breadcrumbs = path.split("/")
		tree = self.getBranchHead(breadcrumbs[0]).tree
		for crumb in breadcrumbs[1:]:
			tree = tree[crumb]
		return tree

	def getBlobByPath(self, path):
		return self.getTreeByPath(path)
