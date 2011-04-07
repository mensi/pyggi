# -*- coding: utf-8 -*-

class RepositoryError(Exception):
	def __init__(self, reason):
		self.reason = reason

	def __str__(self):
		return repr(self.reason)

class Repository(object):
	def __init__(self, **options):
		name = "Dummy repository"
		description = "No description"
		is_empty = True

	class Readme(object):
		def __init__(self, **kwargs):
			self.name = kwargs['name']
			self.data = kwargs['data']
			self.type = kwargs['type']

	class Tree(object):
		"""
			A Tree object should have at least the following fields

			id					the unique id of that tree
			values()			a method returning a list of Blob and Tree objects
			name				the name of this tree
		"""
		pass

	class Blob(object):
		"""
			A Blob object should have at least the following fields

			name				the name of this blob
			id					the unique id of that blob
			data				the data that this blob contains
		"""
		pass

	class Commit(object):
		"""
			A Commit object should have at least the following fields

			committed_date		a time_struct with the date and time of
								the commit
			repo				a Repository like object (backlink)
			message				the message for the commit
			author				an object that has at least the fields
									name
			id					the unique id of that commit
			tree				a Repository.Tree like object
			parents				a list of Repository.Commit objects that
								are parents of this commit
		"""
		pass

	class Head(object):
		"""
			A Head object should have at least the following fields

			commit		a Repository.Commit like object
		"""
		pass

	@property
	def branches(self):
		"""
			return a list of branches of the repository or raise
					a RepositoryError
		"""
		raise RepositoryError("Abstract Repository")

	@property
	def active_branch(self):
		"""
			return the current active branch name or raise
					a RepositoryError
		"""
		raise RepositoryError("Abstract Repository")

	@property
	def tags(self):
		"""
			return a list of tags of the repository or raise
					a RepositoryError
		"""
		raise RepositoryError("Abstract Repository")

	@property
	def head(self):
		"""
			return the current HEAD of the repository. should
			raise a RepositoryError if the repository is empty.

			the returned object should comply to Repository.Head
			specificications
		"""
		raise RepositoryError("Abstract Repository")

	@property
	def readme(self):
		"""
			return a Repository.Readme like object if there is a readme
					file in the repository or None otherwise
		"""
		raise RepositoryError("Abstract Repository")

	def commit(self, treeish):
		"""
			@param treeish the id of a specific commit

			return a Repository.Commit like object for the commit
					with the id treeish or raise a RepositoryError
					exception.
		"""
		raise RepositoryError("Abstract Repository")

	def tree(self, path):
		"""
			@param path a path in thre repository for which a tree
						should be acquired.

			return a Repository.Tree like object or raise a RepositoryError
						if tree does not exist
		"""
		raise RepositoryError("Abstract Repository")


	def blob(self, path):
		"""
			@param path a path in the repository for which a blob
						should be acquired.
						
			return a Repository.Blob like object or raise a RepositoryError
						if blob does not exist
		"""
		raise RepositoryError("Abstract Repository")

	@staticmethod
	def isRepository(name):
		"""
			@param name the name of the repository

			return True if the repository identified by name is really
					a valid repository, False otherwise. The name is
					added to the path of the repositories.
		"""
		return False

	@staticmethod
	def path(name):
		"""
			@param name the name of the repository
			return the absolute path of the repository on the file system
		"""
		return None
