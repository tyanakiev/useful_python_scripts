"""
Git clone generic module.
"""

import os
import httplib
from urlparse import urlparse
from subprocess32 import Popen


class GitClone(object):
    """Class that clones git repo"""

    def __init__(self, git_url, repo_path, username, p_ss):
        self._git_url = git_url
        self._repo_path = repo_path
        self._username = username
        self._p_ss = p_ss

    @staticmethod
    def check_url(url):
        """Checks if url is valid"""
        print('Checking if url: %r is valid', url)
        p = urlparse(url)
        conn = httplib.HTTPConnection(p.netloc)
        conn.request('HEAD', p.path)
        resp = conn.getresponse()
        return resp.status < 400

    def _prepare_url(self):
        """Adding username and password in url. """
        url = self._git_url
        user = self._username
        p_ss = self._p_ss
        parsed = urlparse(url)
        assert '@' not in (parsed.netloc, user, p_ss)
        assert ':' not in (user, p_ss)
        replaced = parsed._replace(netloc="{}:{}@{}".format(user, p_ss, parsed.netloc))
        return replaced.geturl()

    def _clone_repo(self):
        """Execute clone_from method."""
        cmd = ['git', 'clone', '--depth', '1', self._git_url, self._repo_path]
        print('Executing command: %r', ' '.join(cmd))
        proc = Popen(cmd)
        # collection stdout and stderr if needed.
        stdout, stderr = proc.communicate()

    def _assert_attr(self):
        """Checks class attributes."""
        if not os.path.isdir(self._repo_path):
            os.mkdir(self._repo_path)
        assert self.check_url(self._git_url)

    def clone(self):
        """Clones repo to given dir"""
        print('Starting git repo cloning...')
        self._assert_attr()
        self._git_url = self._prepare_url()
        self._clone_repo()
