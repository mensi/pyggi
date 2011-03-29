# -*- coding: utf-8 -*-

from git import Repo, Blob
from flask import current_app
from git import GitCommandError

class Readme(object):
	def __init__(self, name, data, type):
		self.name = name
		self.data = data
		self.type = type

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

	def getBranchHead(self, name):
		try:
			return self.repo.commits(name)[0]
		except GitCommandError as error:
			return None

	def getTarGz(self, tree):
		try:
			return self.repo.archive_tar_gz(tree, self.name+"/")
		except:
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
		try:
			breadcrumbs = path.split("/")
			return Blob.blame(self.repo, breadcrumbs[0], '/'.join(breadcrumbs[1:]))
		except GitCommandError as error:
			return None

	def getHistory(self, path):
		try:
			breadcrumbs = path.split("/")
			return self.repo.commits(breadcrumbs[0], '/'.join(breadcrumbs[1:]))
		except GitCommandError as error:
			return None

	def getReadme(self):
		try:
			# test markdown
			file = self.repo.active_branch+"/README.md"
			blob = self.getBlobByPath(file)
			if not blob is None:
				import markdown
				return Readme("README.md", markdown.markdown(blob.data, safe_mode="replace"), "markdown")

			# test RST
			file = self.repo.active_branch+"/README.rst"
			blob = self.getBlobByPath(file)
			if not blob is None:
				import docutils.core
				parts = docutils.core.publish_parts(blob.data, writer_name="html")
				return Readme("README.rst", parts['body'], "RST")

			# test plain
			file = self.repo.active_branch+"/README"
			blob = self.getBlobByPath(file)
			if not blob is None:
				from filters import html_escape_table
				return Readme("README", "".join(html_escape_table.get(c,c) for c in blob.data), "plain")
		except:
			pass

		return None

