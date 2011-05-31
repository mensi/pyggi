# -*- coding: utf-8 -*-

"""
    :copyright: (c) 2011 by Tobias Heinzen
    :license: BSD, see LICENSE for more details
"""

from git import Repo, GitCommandError
from lib.repository import RepositoryError, Repository
from lib.config import config

class GitRepository(Repository):
    class Submodule(object):
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
            self.url  = url[0]

    def __init__(self, **options):
        self.options = options

        # check if it's really a repository
        if not GitRepository.isRepository(self.options['repository'].split("/")[-1]):
            raise RepositoryError("Repository '%s' is not a Git Repository" % self.options['repository'])

        self.repo = Repo(self.options['repository'])

        # next up prepare some fields
        self.description = self.repo.description
        self.name = self.options['repository'].split("/")[-1]
        self.is_empty = len(self.repo.heads) == 0

    @property
    def clone_urls(self):
        urls = dict(config.items('clone'))
        return dict([(proto, urls[proto].replace("%repo%", self.name)) for proto in urls.keys()])

    @property
    def head(self):
        if self.is_empty:
            raise RepositoryError("Repository '%s' is empty" % self.name)

        return self.repo.heads[0]

    @staticmethod
    def resolve_ref(repository, ref):
        import re
        sha_regex = re.compile('[0-9a-f]{40}')

        if sha_regex.match(ref) is not None:
            return ref

        try:
            from git import Git
            g = Git(repository)
            return g.show_ref('--heads','--tags','-s', ref).split("\n", 1)[0]
        except:
            return None

    @property
    def license(self):
        try:
            path = self.active_branch+"/LICENSE"
            if not self.blob(path) is None:
                return path
        except RepositoryError:
            pass

        return None

    def submodules(self, base, tree):
        try:
            result = []
            path = tree+"/.gitmodules"
            data = self.blob(path).data.split("\n")

            previous = -1
            for n in xrange(0,len(data)):
                line = data[n]
                if line.startswith("[submodule"):
                    if not previous == -1:
                        result.append(GitRepository.Submodule(data[previous:n]))
                    previous = n

            if not previous == -1:
                result.append(GitRepository.Submodule(data[previous:len(data)]))

            return sorted([x for x in result if x.path_base == base], key=lambda x: x.path_name)
        except RepositoryError:
            pass

        return []

    def tree(self, path):
        breadcrumbs = path.split("/")
        tree = self.commit(breadcrumbs[0]).tree
        for crumb in breadcrumbs[1:]:
            try:
                tree = tree[crumb]
            except KeyError:
                raise RepositoryError("Repository '%s' has no tree '%s'" % (self.name, path))

        from git import Blob, Tree
        if isinstance(tree, Tree):
            items = tree.values()
            trees = sorted([x for x in items if isinstance(x, Tree)], key=lambda x: x.name)
            for t in trees:
                t.is_tree = True
            blobs = sorted([x for x in items if isinstance(x, Blob)], key=lambda x: x.name)
            tree.values = trees+blobs
            for t in tree.values:
                t.last_commit = self.last_commit(breadcrumbs[0], "/".join(breadcrumbs[1:]+[t.name]))

        tree.is_tree = True
        return tree

    def blob(self, path):
        blob = self.tree(path)
        blob.is_tree = False
        return blob

    def last_commit(self, tree, path):
        result = self.repo.log(tree, path, max_count=1)
        return result[0]

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
        except:
            pass

        return None

    def archive(self, treeish):
        try:
            return self.repo.archive_tar_gz(treeish, self.name+"/")
        except GitCommandError:
            return RepositoryError("Repository '%s' has no tree '%s'" % (self.name, treeish))

    def history(self, path):
        try:
            breadcrumbs = path.split("/")
            return self.repo.commits(breadcrumbs[0], '/'.join(breadcrumbs[1:]))
        except GitCommandError:
            return RepositoryError("Repository '%s' has no path '%s'" % (self.name, path))

    def blame(self, path):
        try:
            from git import Blob
            breadcrumbs = path.split("/")
            return Blob.blame(self.repo, breadcrumbs[0], '/'.join(breadcrumbs[1:]))
        except GitCommandError:
            return RepositoryError("Repository '%s' has no blame '%s'" % (self.name, path))

    @staticmethod
    def isRepository(name):
        try:
            repo = Repo(GitRepository.path(name))
            return True if not config.getboolean('general','PRESERVE_DAEMON_EXPORT') else repo.daemon_export
        except:
            return False

    @staticmethod
    def path(name):
        import os
        folder = os.path.join(config.get('general','GIT_REPOSITORIES'), name)
        if not os.path.exists(folder):
            raise RepositoryError("Repository '%s' does not exist" % name)

        return folder

    def commit(self, treeish):
        try:
            commit =  self.repo.commits(treeish)[0]
            commit.is_branch = commit.id in [x.commit.id for x in self.repo.branches]
            commit.is_tag = treeish in [x.name for x in self.repo.tags]

            return commit
        except GitCommandError:
            return RepositoryError("Repository '%s' has no tree '%s'" % (self.name, treeish))
