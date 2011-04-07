# -*- coding: utf-8 -*-

from flask import current_app
from git import Repo, GitCommandError, NoSuchPathError
from lib.repository import RepositoryError, Repository

class GitRepository(Repository):
	def __init__(self, **options):
		self.options = options

		# try to load the git repository
		try:
			self.repo = Repo(self.options['repository'])
		except NoSuchPathError as error:
			raise RepositoryError("Repository '%s' is not a Git Repository" % self.options['repository'])

		# next up prepare some fields
		self.description = self.repo.description
		self.name = self.options['repository'].split("/")[-1]
		self.is_empty = len(self.repo.heads) == 0

	@property
	def head(self):
		if self.is_empty:
			raise RepositoryError("Repository '%s' is empty" % self.name)

		return self.repo.heads[0]

	def tree(self, path):
		breadcrumbs = path.split("/")
		tree = self.commit(breadcrumbs[0]).tree
		for crumb in breadcrumbs[1:]:
			try:
				tree = tree[crumb]
			except KeyError as error:
				raise RepositoryError("Repository '%s' has no tree '%s'" % (self.name, path))
		return tree

	def blob(self, path):
		return self.tree(path)

	@property
	def active_branch(self):
		return self.repo.active_branch

	@property
	def readme(self):
		try:
			# markdown
			file = self.active_branch+"/README.md"
			blob = self.blob(file)
			
			import markdown
			return Repository.Readme( \
				name = "README.md",
				data = markdown.markdown(blob.data, safe_mode="replace"),
				type = "markdown"
			)
		except Exception as errr:
			print errr

		return None

	@staticmethod
	def isRepository(name):
		try:
			repo = Repo(GitRepository.path(name))
			return True if not current_app.config['PRESERVE_DAEMON_EXPORT'] else repo.daemon_export
		except:
			return False

	@staticmethod
	def path(name):
		import os
		folder = os.path.join(current_app.config['GIT_REPOSITORIES'], name)
		if not os.path.exists(folder):
			return none

		return folder

	def commit(self, treeish):
		try:
			return self.repo.commits(treeish)[0]
		except GitCommandError as error:
			return RepositoryError("Repository '%s' has no tree '%s'" % (name, treeish))
