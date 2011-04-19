# -*- coding: utf-8 -*-

"""
	:copyright: (c) 2011 by Tobias Heinzen 
	:license: BSD, see LICENSE for more details
"""

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

		from git import Blob, Tree
		if isinstance(tree, Tree):
			items = tree.values()
			trees = sorted([x for x in items if isinstance(x, Tree)], key=lambda x: x.id, reverse=True)
			for t in trees:
				t.is_tree = True
			blobs = sorted([x for x in items if isinstance(x, Blob)], key=lambda x: x.id, reverse=True)
			tree.values = trees+blobs

		tree.is_tree = True
		return tree

	def blob(self, path):
		blob = self.tree(path)
		blob.is_tree = False
		return blob

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

	def archive(self, treeish):
		try:
			return self.repo.archive_tar_gz(treeish, self.name+"/")
		except GitCommandError as error:
			return RepositoryError("Repository '%s' has no tree '%s'" % (self.name, treeish))

	def history(self, path):
		try:
			breadcrumbs = path.split("/")
			return self.repo.commits(breadcrumbs[0], '/'.join(breadcrumbs[1:]))
		except GitCommandError as error:
			return RepositoryError("Repository '%s' has no path '%s'" % (self.name, path))

	def blame(self, path):
		try:
			from git import Blob
			breadcrumbs = path.split("/")
			return Blob.blame(self.repo, breadcrumbs[0], '/'.join(breadcrumbs[1:]))
		except GitCommandError as error:
			return RepositoryError("Repository '%s' has no blame '%s'" % (self.name, path))

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
			return None

		return folder

	def commit(self, treeish):
		try:
			commit =  self.repo.commits(treeish)[0]
			commit.is_branch = commit.id in [x.commit.id for x in self.repo.branches]
			commit.is_tag = commit in [x.name for x in self.repo.tags]

			return commit
		except GitCommandError as error:
			return RepositoryError("Repository '%s' has no tree '%s'" % (self.name, treeish))
