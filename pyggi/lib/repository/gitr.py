# -*- coding: utf-8 -*-

"""
    :copyright: (c) 2011 by Tobias Heinzen
    :license: BSD, see LICENSE for more details
"""

import os, os.path
from git import Repo, GitCommandError
from gitdb.exc import BadObject
from pyggi.lib.repository import Repository, RepositoryError, EmptyRepositoryError
from pyggi.lib.config import config

class GitRepository(Repository):
    class GitSubmodule(object):
        def __init__(self, configuration):
            """
                @param configuration a list of strings, that correspond
                                        to the configuration block for this
                                        submodule
            """

            import re
            modulere = re.compile('\[submodule\s*"(.*?)"\]')
            pathre = re.compile("\s*path\s*=\s*(.*)")
            urlre = re.compile("\s*url\s*=\s*(.*)")

            name = [
                        match[0]
                        for match in [modulere.findall(line) for line in configuration]
                        if len(match) == 1
                    ]
            path = [
                        match[0]
                        for match in [pathre.findall(line) for line in configuration]
                        if len(match) == 1
                    ]
            url = [
                        match[0]
                        for match in [urlre.findall(line) for line in configuration]
                        if len(match) == 1
                    ]

            if len(name) == 0 or len(path) == 0 or len(url) == 0:
                raise RepositoryError("Corrupt submodule")

            self.name = name[0]
            path = path[0].rsplit("/", 1)
            if len(path) == 1:
                self.path_base = ""
                self.path_name = path[0]
            else:
                self.path_base = path[0]
                self.path_name = path[1]
            self.url = url[0]

    class GitBranch:
        """emulating Repository.Branch fields"""
        def __init__(self, branch):
            self.branch = branch
            self.name = branch.name
            self.commit = GitRepository.GitCommit(branch.commit)

    class GitTree:
        """emulating Repository.Tree fields"""
        def __init__(self, tree):
            # emulate id field (has been renamed)
            self.id = tree.hexsha

            # one-to-one copy of fields
            self.name = tree.name

            # additional fields
            self._values = None
            self.is_tree = True
            self.tree = tree
            """
            last_commit         a Repository.Commit like object that points to the last
                                commit to this object (see Repository.last_commit)"""

        @property
        def values(self):
            if self._values is None:
                trees = [GitRepository.GitTree(tree) for tree in self.tree.trees]
                blobs = [GitRepository.GitBlob(blob) for blob in self.tree.blobs]
                self._values = trees + blobs
            return self._values

    class GitBlob:
        """emulating Repository.Blob fields"""
        def __init__(self, blob):
            # emulate id field (has been renamed)
            self.id = blob.hexsha

            # one-to-one copy of fields
            self.name = blob.name
            self.size = blob.size
            self.mode = blob.mode
            self.mime_type = blob.mime_type

            # additional fields
            self._data = None
            self.is_tree = False
            self.blob = blob
            """
            last_commit         a Repository.Commit like object that points to the last
                                commit to this object (see Repository.last_commit)"""

        @property
        def data(self):
            # only load data once
            if self._data is None:
                self._data = self.blob.data_stream.read()
            return self._data

    class GitCommit:
        """emulating Repository.Commit fields"""
        def __init__(self, commit):
            # id has been renamed
            self.id = commit.hexsha

            # identify commit as branch and tag
            self.is_branch = commit.hexsha in (head.commit.hexsha for head in commit.repo.branches)
            self.is_tag = commit.hexsha in (tag.commit.hexsha for tag in commit.repo.tags)

            # some computed stuff
            self.tree = GitRepository.GitTree(commit.tree)
            self.parents = (GitRepository.GitCommit(c) for c in commit.parents)

            # one-to-one copy of Commit object fields
            self.committed_date = commit.committed_date
            self.repo = commit.repo
            self.message = commit.message
            self.summary = commit.summary
            self.author = commit.author
            self.stats = commit.stats

            # the commit object
            self.commit = commit

        @property
        def tree(self):
            return self.commit.tree

        @property
        def parents(self):
            return self.commit.parents

        @property
        def diffs(self):
            if len(self.commit.parents) > 0:
                return self.commit.parents[0].diff(self.commit.hexsha, create_patch=True)
            return []

    def __init__(self, **options):
        self.options = options

        # check if it's really a repository
        if not GitRepository.isRepository(self.options['repository']):
            raise RepositoryError("Repository '%s' is not a Git Repository" % self.options['repository'])
        self.path = self.options['repository']

        if not os.path.exists(self.path):
            raise RepositoryError("Repository '%s' does not exist" % self.path)
        self.repo = Repo(self.path)

        # next up prepare some fields
        self.description = self.repo.description
        self.name = self.options['repository'].rsplit("/", 1)[-1]

        # if we have an empty repository we shall raise an error
        # so that we get redirected to a special page (except if
        # we force the loading of the repository)
        if len(self.repo.heads) == 0 and (not 'force' in self.options.keys() or not self.options['force']):
            raise EmptyRepositoryError(self.name)

    @property
    def is_bare(self):
        return self.repo.bare

    @property
    def is_empty(self):
        return len(self.repo.heads) == 0

    @property
    def active_branch(self):
        return self.repo.active_branch.name

    @property
    def branches(self):
        return sorted((GitRepository.GitBranch(b) for b in self.repo.heads), key=lambda x: x.commit.committed_date, reverse=True)

    @property
    def tags(self):
        return [GitRepository.GitBranch(b) for b in self.repo.tags]

    @property
    def clone_urls(self):
        urls = dict(config.items('clone'))
        return dict([(proto, urls[proto] % self.name) for proto in urls.keys()])

    @property
    def readme(self):
        try:
            # markdown
            file = self.active_branch + "/README.md"
            blob = self.blob(file)

            import markdown
            return Repository.Readme(\
                name="README.md",
                data=markdown.markdown(blob.data, safe_mode="replace"),
                type="markdown"
            )
        except:
            pass

        try:
            # RST
            file = self.active_branch + "/README.rst"
            blob = self.blob(file)

            import docutils.core
            parts = docutils.core.publish_parts(blob.data, writer_name="html")
            return Repository.Readme(\
                name="README.rst",
                data=parts['body'],
                type="RST"
            )
        except:
            pass

        try:
            # plain
            file = self.active_branch + "/README"
            blob = self.blob(file)

            from pyggi.lib.filters import html_escape_table

            data = unicode(blob.data, 'utf-8')
            data = "".join(html_escape_table.eet(c, c) if c != "\n" else "<br/>" for c in data)

            return Repository.Readme(\
                name="README",
                data=data,
                type="plain"
            )
        except:
            pass

        return None

    @staticmethod
    def isRepository(path):
        try:
            repo = Repo(path)
        except:
            return False

        try:
            preserve_daemon_export = config.getboolean('general', 'preserve_daemon_export')
        except:
            preserve_daemon_export = True

        if preserve_daemon_export:
            return repo.daemon_export

        return True

    @staticmethod
    def resolve_ref(repository, ref):
        if not os.path.exists(repository):
            raise RepositoryError("Repository '%s' does not exist" % repository)

        import re
        sha_regex = re.compile('[0-9a-f]{40}')

        if sha_regex.match(ref) is not None:
            return ref

        try:
            return GitRepository(repository).commit(ref).hexsha
        except:
            return None

    def _traverse_tree(self, path):
        rev, path = (path+"/").split("/", 1)
        tree = self.repo.tree(rev)
        if path == "":
            return (x for x in [tree])
        return tree.traverse(predicate=lambda i,d: i.path == path[:-1])

    def blob(self, path):
        try:
            gen = self._traverse_tree(path)
            return GitRepository.GitBlob(gen.next())
        except BadObject:
            raise RepositoryError("Repository '%s' has no tree '%s'" % (self.path, path))
        except StopIteration:
            raise RepositoryError("Repository '%s' has no tree '%s'" % (self.path, path))

    def tree(self, path):
        try:
            gen = self._traverse_tree(path)
            return GitRepository.GitTree(gen.next())
        except BadObject:
            raise RepositoryError("Repository '%s' has no tree '%s'" % (self.path, path))
        except StopIteration:
            raise RepositoryError("Repository '%s' has no tree '%s'" % (self.path, path))

    def last_activities(self, treeish, count=4, skip=0):
        return (GitRepository.GitCommit(c) for c in self.repo.iter_commits(treeish, max_count=count, skip=skip))

    def commit(self, rev):
        try:
            return GitRepository.GitCommit(self.repo.commit(rev))
        except BadObject:
            raise RepositoryError("Repository '%s' has no branch '%s'" % (self.path, rev))

    def submodules(self, base, tree):
        # let us parse .gitmodules ourselves. the implementation
        # of GitPython does not allow to iterate submodules of
        # a specific path nor of a specific revision!!

        try:
            result = []
            path = tree + "/.gitmodules"
            data = self.blob(path).data.split("\n")

            previous = -1
            for n in xrange(0, len(data)):
                line = data[n]
                if line.startswith("[submodule"):
                    if not previous == -1:
                        result.append(GitRepository.GitSubmodule(data[previous:n]))
                    previous = n

            if not previous == -1:
                result.append(GitRepository.GitSubmodule(data[previous:len(data)]))

            return sorted([x for x in result if x.path_base == base], key=lambda x: x.path_name)
        except RepositoryError:
            pass

        return []

    def history(self, path):
        breadcrumbs = path.split("/")
        return (
            GitRepository.GitCommit(c) for c in
                self.repo.iter_commits(breadcrumbs[0], "/".join(breadcrumbs[1:]))
        )

    def blame(self, path):
        breadcrumbs = path.split("/")
        return ((GitRepository.GitCommit(c), b) for c,b in
            self.repo.blame(breadcrumbs[0], "/".join(breadcrumbs[1:]))
        )

    def commit_count(self, start):
        commit = self.repo.commit(start)
        return commit.count()

    def archive(self, treeish):
       try:
            from tempfile import TemporaryFile
            with TemporaryFile(mode='w+b') as fp:
                self.repo.archive(fp, treeish)
                fp.flush()
                fp.seek(0)
                data = fp.read()

            return data
       except GitCommandError:
            return RepositoryError("Repository '%s' has no tree '%s'" % (self.path, treeish))

