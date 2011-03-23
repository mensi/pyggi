# -*- coding: utf-8 -*-

from git import Repo

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

	def getHead(self):
		return self.repo.commits()[0]

	def getBranchHead(self, name):
		return self.repo.commits(name)[0]
