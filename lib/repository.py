# -*- coding: utf-8 -*-

from git import Repo, Blob
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

		# next up, write some information down, for easy acces
		self.description = self.repo.description
		self.name = kwargs['repo'].split("/")[-1]
		self.head = self.repo.heads[0]

	@staticmethod
	def getRepositoryFolder(repository):
		import os
		repo_folder = os.path.join(current_app.config['GIT_REPOSITORIES'], repository)
		if not os.path.exists(repo_folder):
			return None
		return repo_folder

	@staticmethod
	def isGitRepository(repository):
		try:
			repo = Repo(GitRepository.getRepositoryFolder(repository))
			return True
		except:
			return False

	def getHead(self):
		return self.repo.commits()[0]

	def getBranchHead(self, name):
		from git import GitCommandError
		try:
			return self.repo.commits(name)[0]
		except GitCommandError as error:
			return None

	def getTreeByPath(self, path):
		"""
			traverse tree defined by path
		"""
		breadcrumbs = path.split("/")
		tree = self.getBranchHead(breadcrumbs[0]).tree
		for crumb in breadcrumbs[1:]:
			try:
				tree = tree[crumb]
			except KeyError as error:
				return None
		return tree

	def getBlobByPath(self, path):
		return self.getTreeByPath(path)

	def getBlame(self, path):
		breadcrumbs = path.split("/")
		return Blob.blame(self.repo, breadcrumbs[0], '/'.join(breadcrumbs[1:]))

	def getHistory(self, path):
		breadcrumbs = path.split("/")
		return self.repo.commits(breadcrumbs[0], '/'.join(breadcrumbs[1:]))
