# -*- coding: utf-8 -*-
"""
github3.repos.commit
====================

This module contains the RepoCommit class alone

"""
from __future__ import unicode_literals

from . import status
from .. import git, models, users
from .comment import RepoComment


class RepoCommit(models.BaseCommit):
    """The :class:`RepoCommit <RepoCommit>` object. This represents a commit as
    viewed by a :class:`Repository`. This is different from a Commit object
    returned from the git data section.

    Two commit instances can be checked like so::

        c1 == c2
        c1 != c2

    And is equivalent to::

        c1.sha == c2.sha
        c1.sha != c2.sha

    """

    def _update_attributes(self, commit):
        super(RepoCommit, self)._update_attributes(commit)

        self.author = self._class_attribute(
            commit, 'author', users.ShortUser, self
        )
        self.committer = self._class_attribute(
            commit, 'committer', users.ShortUser, self
        )

        #: :class:`Commit <github3.git.Commit>`.
        self.commit = self._class_attribute(commit, 'commit', git.ShortCommit, self)

        self.sha = self._get_attribute(commit, 'sha')

        #: The number of additions made in the commit.
        self.additions = 0

        #: The number of deletions made in the commit.
        self.deletions = 0

        #: Total number of changes in the files.
        self.total = 0
        stats = self._get_attribute(commit, 'stats')
        if stats:
            self.additions = commit['stats'].get('additions')
            self.deletions = commit['stats'].get('deletions')
            self.total = commit['stats'].get('total')

        #: The files that were modified by this commit.
        self.files = self._get_attribute(commit, 'files', [])

        self._uniq = self.sha

        #: The commit message
        self.message = getattr(self.commit, 'message', None)

    def _repr(self):
        return '<Repository Commit [{0}]>'.format(self.sha[:7])

    def diff(self):
        """Retrieve the diff for this commit.

        :returns: the diff as a bytes object
        :rtype: bytes
        """
        resp = self._get(self._api,
                         headers={'Accept': 'application/vnd.github.diff'})
        return resp.content if self._boolean(resp, 200, 404) else b''

    def patch(self):
        """Retrieve the patch formatted diff for this commit.

        :returns: the patch as a bytes object
        :rtype: bytes
        """
        resp = self._get(self._api,
                         headers={'Accept': 'application/vnd.github.patch'})
        return resp.content if self._boolean(resp, 200, 404) else b''

    def status(self):
        """Retrieve the combined status for this commit.

        :returns: the combined status for this commit
        :rtype: :class:`~github3.repos.status.CombinedStatus`
        """
        url = self._build_url('status', base_url=self._api)
        json = self._json(self._get(url), 200)
        return self._instance_or_null(status.CombinedStatus, json)

    def statuses(self):
        """Retrieve the statuses for this commit.

        :returns: the statuses for this commit
        :rtype: :class:`~github3.repos.status.Status`
        """
        url = self._build_url('statuses', base_url=self._api)
        return self._iter(-1, url, status.Status)

    def comments(self, number=-1, etag=None):
        """Iterate over comments for this commit.

        :param int number: (optional), number of comments to return. Default:
            -1 returns all comments
        :param str etag: (optional), ETag from a previous request to the same
            endpoint
        :returns: generator of
            :class:`RepoComment <github3.repos.comment.RepoComment>`\ s
        """
        url = self._build_url('comments', base_url=self._api)
        return self._iter(int(number), url, RepoComment, etag=etag)
