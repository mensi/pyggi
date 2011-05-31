# -*- coding: utf-8 -*-

"""
    :copyright: (c) 2011 by Tobias Heinzen
    :license: BSD, see LICENSE for more details
"""

class RepositoryError(Exception):
    def __init__(self, reason):
        self.reason = reason

    def __str__(self):
        return repr(self.reason)

    def __getattr__(self, name):
        if not name in ["reason", "__str__"]:
            raise self
        return super(RepositoryError, self).__getattr__(name)

class Repository(object):
    def __init__(self, **options):
        self.name = "Dummy repository"
        self.description = "No description"
        self.is_empty = True

    class Readme(object):
        def __init__(self, **kwargs):
            self.name = kwargs['name']
            self.data = kwargs['data']
            self.type = kwargs['type']

    class Submodule(object):
        """
            A Submodule object should have at least the following fields

            name        the name of the submodule
            path_base   the base path were this submodule is located in
            path_name   the name of the path that links to the submodule
            url         the url from which this submodule is cloned
        """
        pass

    class Stats(object):
        """
            A Stats object should have at least the following fields

            files       a dictionary with the files in the commit as keys
                        and a dictionary with 'insertions','deletions' as keys
                        and integer as values that describe the number of changes

                            example: files = {'a': {'insertions': 3, 'deletions': 25}}

            total       a dictionary with keys 'files', 'insertions' and 'deletions' as keys
                        and integer as values that describe the number of changes

                            example: total = {'files': 1, 'insertions': 3, 'deletions': 25}
        """
        pass

    class Diff(object):
        """
            A Diff object should have at least the following fields

            new_file        the filename of a newly created file or None if the
                            file existed before
            deleted_file    the filename of the deleted file or None if the
                            file still exists

            rename_to
            rename_from     describes a rename of a file, or None if the
                            filename does not change

            b_path          the path inside the git repository of this file

            diff            a blob field that contains the text of a 'git diff' like
                            format

            stats           a Repository.Stats object
        """
        pass

    class Tree(object):
        """
            A Tree object should have at least the following fields

            id                  the unique id of that tree
            values              a list of Blob and Tree objects, sorted by name
                                and Tree objects are grouped together before the Blob objects
            name                the name of this tree
            last_commit         a Repository.Commit like object that points to the last
                                commit to this object (see Repository.last_commit)
            is_tree = True
        """
        pass

    class Blob(object):
        """
            A Blob object should have at least the following fields

            name                the name of this blob
            id                  the unique id of that blob
            data                the data that this blob contains
            size                the size in bytes of the file
            mode                the mode of the file
            mime_type           the mime_type of that file or 'text/plain' if
                                unknown
            last_commit         a Repository.Commit like object that points to the last
                                commit to this object (see Repository.last_commit)
            is_tree = False
        """
        pass

    class Branch(object):
        """
            A Branch object should have at least the following fields

            name                the name of this branch
            commit              a link to the commit that this branch
                                refers to (Repository.Commit)
        """
        pass

    class Commit(object):
        """
            A Commit object should have at least the following fields

            committed_date      a time_struct with the date and time of
                                the commit
            repo                a Repository like object (backlink)
            message             the message for the commit
            author              an object that has at least the fields
                                    name
            id                  the unique id of that commit
            tree                a Repository.Tree like object
            parents             a list of Repository.Commit objects that
                                are parents of this commit
            diffs               a list of Repository.Diff objects that describe
                                the changes in this commit

            is_branch           True if the commit is current head of the active branch
            is_tag              True if the commit has a tag
        """
        pass

    class Head(object):
        """
            A Head object should have at least the following fields

            commit      a Repository.Commit like object
        """
        pass

    @staticmethod
    def resolve_ref(repository, reference):
        """
            resolve a reference name in a repository to the respective
            unique id of a commit, or None if the reference could not
            be resolved
        """
        raise RepositoryError("Abstract Repository")

    @property
    def branches(self):
        """
            return a list of branches of the repository or raise
                    a RepositoryError. An entry in the list
                    is a Repository.Branch like object
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
                    a RepositoryError. An entry in the list
                    is a Repository.Branch like object
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

    def last_commit(self, tree, path):
        """
            return a Repository.Commit like object, that provides
            the last commit to this path in reference to a given
            tree (meaning: return the newest commit that is not newer
            than the given treeish)

            @param tree the reference tree
            @param path the path in the repository
        """
        raise RepositoryError("Abstract Repository")

    def archive(self, treeish):
        """
            @param  treeish the id of a specific commit

            return the data of a 'tar.gz' archive of the specified commit
        """
        raise RepositoryError("Abstract Repository")

    @property
    def license(self):
        """
            return the path to the LICENSE file in the active branch or None
                    if no LICENSE file is available.
        """
        raise RepositoryError("Abstract Repository")

    @property
    def readme(self):
        """
            return a Repository.Readme like object if there is a readme
                    file in the repository or None otherwise
        """
        raise RepositoryError("Abstract Repository")

    @property
    def clone_urls(self):
        """
            return a dictionary that contains as keys a protocol
                    and as value an url, from where the repository
                    can be clone.
        """
        raise RepositoryError("Abstract Repository")

    def submodules(self, base, treeish):
        """
            @param  base the base path from which the submodules should
                            be listed
            @param  treeish from which tree shall the submodules be listed

            return a list of Repository.Submodule that are in the base path, sorted
                    by their path name or an empty list.
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

    def history(self, path):
        """
            @param path a path in the repository for which the history
                        should be acquired

            return a list of Repository.Commit objects that compose of the
                    history for that path. The list should be sorted such that
                    the newest commit is the first element in the list.
        """
        raise RepositoryError("Abstract Repository")

    def blame(self, path):
        """
            @param path a path in the repository for which the blame
                        information should be acquired

            return a list of tuples that contain the blame information. the tuple
                    is composed of the following entries:
                        [0] ->  a Repository.Commit object
                        [1] ->  a list of strings that are the lines of
                                the file that were changed in the commit
                                (referenced by [0])
        """
        raise RepositoryError("Abstract Repository")

    def tree(self, path):
        """
            @param path a path in the repository for which a tree
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
            return the absolute path of the repository on the file system or raise
                    RepositoryError if not found
        """
        raise RepositoryError('Abstract Repository')
