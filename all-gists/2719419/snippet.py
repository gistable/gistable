#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  gitprompt.py
#
#  Copyright 2012 Manuel Vázquez Acosta <mva DOT led AT google-mail-address-here.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#
#

from IPython.core.prompts import LazyEvaluate as promptify

try:
    import git

    class Repo(git.Repo):
        @property
        def active_branch(self):
            try:
                return super(Repo, self).active_branch
            except:
                return '(no branch)'

        @property
        def has_untracked(self):
            return '??' in self.git.status(porcelain=True)


    def _br_and_st():
        try:
            repo = Repo()
            return repo.active_branch, repo.is_dirty, repo.has_untracked
        except git.InvalidGitRepositoryError:
            return '', False, False
        except Exception as error:
            return str(error), False, False

except ImportError:
    # Fall back to execute git subprocess if python-git is not installed.

    from subprocess import Popen, PIPE

    def _git_current_branch():
        # The following is the same as `git branch |grep ^\* |cut -b3-` which gets the current branch name
        git_br = Popen(["git", "branch"], stdout=PIPE, stderr=PIPE)
        grep = Popen(['grep', r'^\*'], stdin=git_br.stdout, stdout=PIPE)
        cut = Popen(['cut', '-b3-'], stdin=grep.stdout, stdout=PIPE)
        return cut.communicate()[0].strip()

    def _git_isdirty():
        # git st --porcelain | grep -v ^? | wc -l
        git_st = Popen(["git", "status", "--porcelain"], stdout=PIPE, stderr=PIPE)
        grep = Popen(["grep", "-v", "^?"], stdin=git_st.stdout, stdout=PIPE)
        wc = Popen(['wc', '-l'], stdin=grep.stdout, stdout=PIPE)
        count = wc.communicate()[0].strip()
        count = int(count)
        return False if count == 0 else True

    def _git_has_untracked():
        # git st --porcelain | grep ^? | wc -l
        git_st = Popen(["git", "status", "--porcelain"], stdout=PIPE, stderr=PIPE)
        grep = Popen(["grep", "^?"], stdin=git_st.stdout, stdout=PIPE)
        wc = Popen(['wc', '-l'], stdin=grep.stdout, stdout=PIPE)
        count = wc.communicate()[0].strip()
        count = int(count)
        return False if count == 0 else True

    def _br_and_st():
        try:
            return _git_current_branch(), _git_isdirty(), _git_has_untracked()
        except:
            return '', False, False


@promptify
def git_branch_and_st():
    branch, dirty, untracked = _br_and_st()
    if branch:
        if dirty or untracked:
            suffix = ', '
            if dirty:
                suffix += '*'
            if untracked:
                suffix += '+'
        else:
            suffix = ''
        return '[{branch}{suffix}]'.format(branch=branch, suffix=suffix)
    else:
        return ''
