# -*- coding: utf-8 -*-

"""
    :copyright: (c) 2011 by Tobias Heinzen
    :license: BSD, see LICENSE for more details
"""

import os, os.path
from git import Repo, GitCommandError
from pyggi.lib.repository import RepositoryError, Repository, EmptyRepositoryError
from pyggi.lib.config import config

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
            self.url = url[0]

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
    def clone_urls(self):
        urls = dict(config.items('clone'))
        return dict([(proto, urls[proto] % self.name) for proto in urls.keys()])

    @property
    def head(self):
        if self.is_empty:
            raise RepositoryError("Repository '%s' is empty" % self.path)

        return self.repo.heads[0]

    @staticmethod
    def resolve_ref(repository, ref):
        if not os.path.exists(repository):
            raise RepositoryError("Repository '%s' does not exist" % repository)

        import re
        sha_regex = re.compile('[0-9a-f]{40}')

        if sha_regex.match(ref) is not None:
            return ref

        try:
            from git import Git
            g = Git(repository)
            return g.show_ref('--heads', '--tags', '-s', ref).split("\n", 1)[0]
        except:
            return None

    @property
    def license(self):
        try:
            path = self.active_branch + "/LICENSE"
            if not self.blob(path) is None:
                return path
        except RepositoryError:
            pass

        return None

    def submodules(self, base, tree):
        try:
            result = []
            path = tree + "/.gitmodules"
            data = self.blob(path).data.split("\n")

            previous = -1
            for n in xrange(0, len(data)):
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
                raise RepositoryError("Repository '%s' has no tree '%s'" % (self.path, path))

        from git import Blob, Tree
        if isinstance(tree, Tree):
            items = tree.values()
            trees = sorted([x for x in items if isinstance(x, Tree)], key=lambda x: x.name)
            for t in trees:
                t.is_tree = True
            blobs = sorted([x for x in items if isinstance(x, Blob)], key=lambda x: x.name)
            tree.values = trees + blobs
            for t in tree.values:
                t.last_commit = self.last_commit(breadcrumbs[0], "/".join(breadcrumbs[1:] + [t.name]))

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

    def last_activities(self, treeish, count=4, skip=0):
        return self.repo.commits(treeish, max_count=count, skip=0)

    def archive(self, treeish):
        try:
            return self.repo.archive_tar_gz(treeish, self.name + "/")
        except GitCommandError:
            return RepositoryError("Repository '%s' has no tree '%s'" % (self.path, treeish))

    def history(self, path):
        try:
            breadcrumbs = path.split("/")
            return self.repo.commits(breadcrumbs[0], '/'.join(breadcrumbs[1:]))
        except GitCommandError:
            return RepositoryError("Repository '%s' has no path '%s'" % (self.path, path))

    def blame(self, path):
        try:
            from git import Blob
            breadcrumbs = path.split("/")
            return Blob.blame(self.repo, breadcrumbs[0], '/'.join(breadcrumbs[1:]))
        except GitCommandError:
            return RepositoryError("Repository '%s' has no blame '%s'" % (self.path, path))

    @property
    def branches(self):
        return self.repo.heads

    @property
    def tags(self):
        return self.repo.tags

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

    def commit(self, treeish):
        try:
            commit = self.repo.commits(treeish)[0]
            commit.is_branch = commit.id in [x.commit.id for x in self.repo.branches]
            commit.is_tag = treeish in [x.name for x in self.repo.tags]

            return commit
        except GitCommandError:
            return RepositoryError("Repository '%s' has no tree '%s'" % (self.path, treeish))
