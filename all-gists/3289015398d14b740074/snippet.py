#!/usr/bin/env python
"""
Provide useful alembic information after switching branches.
"""

import argparse
import subprocess
import os
import os.path
import py.path
import logging

from alembic.config import Config
from alembic.script import ScriptDirectory
from alembic.environment import EnvironmentContext
from alembic.util import CommandError


def intbool(val):
    return val == '1'

parser = argparse.ArgumentParser(prog="post-checkout", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument('prev_sha1')
parser.add_argument('new_sha1')
parser.add_argument('is_branch_checkout', type=intbool)


def get_heads():
    # git show-ref --heads
    raw_heads = subprocess.check_output(['git', 'show-ref', '--heads']).splitlines()
    split_heads = [raw.split(" ", 1) for raw in raw_heads]
    heads = {split[0]: split[1].split("/")[-1] for split in split_heads}
    return heads


def get_toplevel():
    return subprocess.check_output(['git', 'rev-parse', '--show-toplevel']).strip()


class CaptureCurrentContext(EnvironmentContext):
    # This is a sham EnvironmentContext which only captures the current revision
    def __init__(self, cfg, script, **kw):
        super(CaptureCurrentContext, self).__init__(cfg, script, **kw)
        self.current_revisions = set()

    def run_migrations(self, **kw):
        self.current_revisions.add(self.get_context().get_current_revision())


def get_alembic_data():
    # This function must be run with the alembic root as the cwd
    fake_cmd_opts = type('args', (object,), {'x': []})()
    cfg = Config(file_="alembic.ini", cmd_opts=fake_cmd_opts)
    script = ScriptDirectory.from_config(cfg)

    sham = CaptureCurrentContext(cfg, script)
    with sham:
        try:
            # disable INFO level and below logging
            logging.disable(logging.INFO)
            script.run_env()
        finally:
            # undo the disable
            logging.disable(logging.NOTSET)

    if len(sham.current_revisions) > 1:
        return {
            'msg': u"""Your databases are at different revisions: {revisions}. Unable to offer more advice.""",
            'revisions': sham.current_revisions
        }
    current_revision = sham.current_revisions.pop()

    have_current = True
    try:
        script.get_revision(current_revision)
    except CommandError:
        have_current = False

    heads = script.get_heads()
    if len(heads) > 1:
        # branch exists, can't do much else
        branchpoint = [rev for rev in script.walk_revisions() if rev.is_branch_point][0]

        if not have_current:
            msg = u"""There is an Alembic branch in the tree. In addition, your current revision is not in the tree. You should switch back and downgrade. The branchpoint is {branchpoint.revision}: {branchpoint.doc}.

git checkout {previous_ref}
cd {alembic_root}
alembic downgrade {branchpoint.revision}
cd ../..
git checkout {new_ref}
"""
            return {
                'msg': msg,
                'branchpoint': branchpoint
            }

        # are we upstream or downstream of the branchpoint?
        upstream = True
        try:
            list(script.walk_revisions(base=branchpoint.revision, head=current_revision))
        except CommandError:
            upstream = False

        if upstream:
            msg = u"""There is an Alembic branch in the tree, downstream of your current revision. You should downgrade before resolving the branch. The branchpoint is {branchpoint.revision}: {branchpoint.doc}.

cd {alembic_root}
alembic downgrade {branchpoint.revision}
cd ../..
"""
        else:
            msg = u"""There is an Alembic branch in the tree, upstream of your current revision. You should resolve the branch before upgrading. The branchpoint is {branchpoint.revision}: {branchpoint.doc}."""
        return {
            'msg': msg,
            'branchpoint': branchpoint
        }

    # If we're here, there's no branch.
    head = script.get_revision(heads[0])
    if head.revision == current_revision:
        # Nothing to do
        return None

    if have_current:
        # most recent comes first
        ahead = list(script.walk_revisions(base=current_revision))
        # we want most recent to be last
        ahead.reverse()
        msg = u"""There are {count} revisions upstream of your current revision. You should upgrade before continuing.

cd {alembic_root}
alembic upgrade head
cd ../..
"""
        return {
            'msg': msg,
            'count': len(ahead),
            'ahead': ahead
        }
    else:
        msg = u"""The Alembic history does not contain your current revision. The latest revision is {head.revision}: {head.doc}. You should switch back and downgrade.

git checkout {previous_ref}
cd {alembic_root}
alembic downgrade {head.revision}
cd ../..
git checkout {new_ref}
"""
        return {
            'msg': msg,
            'head': head
        }


def main():
    args = parser.parse_args()
    if not args.is_branch_checkout:
        parser.exit(0)
    heads = get_heads()
    alembic_root = os.path.join(get_toplevel(), 'share/migrations')
    with py.path.local(alembic_root).as_cwd():
        alembic_data = get_alembic_data()
    if alembic_data is not None:
        alembic_data['alembic_root'] = alembic_root
        alembic_data['previous_ref'] = heads.get(args.prev_sha1, args.prev_sha1)
        alembic_data['new_ref'] = heads.get(args.new_sha1, args.new_sha1)
        print alembic_data['msg'].format(**alembic_data)
        if 'ahead' in alembic_data:
            for rev in alembic_data['ahead']:
                print "  {0}: {1}".format(rev.revision, rev.doc)

    parser.exit(0)

if __name__ == '__main__':
    main()