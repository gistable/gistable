#!/usr/bin/env python2

r'''
sos-branch.py -- create an SOS branch on remote git repository

Oct 19th 2012, my colleagues found the wiki of a repository on GitHub is
corrupted, but they had not cloned the wiki since it was created. To make bad
worse, GitHub does not provide for wiki the same content accessing API as for
normal repository.

Yes, there is still a chance to recover all the commits before the corrupted
one, if you know how git works. When git pushes, it only sends commits which the
remote side does not have. Since the branch being created on remote side is
pointing to an existing commit there, git only sends an empty pack. So, all just
pretend that I have all these commits locally, send an empty pack, and then
fetch the created branch.

.. admonition:: WARNING

    Running this script might lead to data loss on remote git repository, use
    at your own risk.


    >>> from dulwich.client import get_transport_and_path
    >>> from dulwich.objects import Blob, Tree, Commit
    >>> from dulwich.repo import Repo
    >>> import os, time
    >>>
    >>> REPONAME = "corrupted-repo"
    >>> AUTHOR = "AUTHOR <author@example.com>"
    >>> TIMESTAMP = int(time.time())
    >>> TIMEZONE = time.timezone
    >>>
    >>> repo = Repo.init(REPONAME, mkdir=True)
    >>>
    >>> first_blob = Blob.from_string("FIRST BLOB\n")
    >>> first_tree = Tree()
    >>> first_tree.add("README", 0100644, first_blob.id)
    >>> first_commit = Commit()
    >>> first_commit.tree = first_tree.id
    >>> first_commit.author = first_commit.committer = AUTHOR
    >>> first_commit.author_time = first_commit.commit_time = TIMESTAMP
    >>> first_commit.author_timezone = first_commit.commit_timezone = TIMEZONE
    >>> first_commit.encoding = "UTF-8"
    >>> first_commit.message = "First commit"
    >>> repo.object_store.add_object(first_blob)
    >>> repo.object_store.add_object(first_tree)
    >>> repo.object_store.add_object(first_commit)
    >>>
    >>> second_blob = Blob.from_string("SECOND BLOB\n")
    >>> second_tree = Tree()
    >>> second_tree.add("README", 0100644, second_blob.id)
    >>> second_commit = Commit()
    >>> second_commit.parents = [first_commit.id]
    >>> second_commit.tree = second_tree.id
    >>> second_commit.author = second_commit.committer = AUTHOR
    >>> second_commit.author_time = second_commit.commit_time = TIMESTAMP
    >>> second_commit.author_timezone = second_commit.commit_timezone = TIMEZONE
    >>> second_commit.encoding = "UTF-8"
    >>> second_commit.message = "Second commit"
    >>> repo.object_store.add_object(second_blob)
    >>> repo.object_store.add_object(second_tree)
    >>> repo.object_store.add_object(second_commit)
    >>>
    >>> repo.refs['refs/heads/master'] = second_commit.id
    >>>
    >>> os.remove(repo.object_store._get_shafile_path(second_tree.id))
    >>>
    >>> client, path = get_transport_and_path(REPONAME)
    >>> sos_branch(client, path, 'backup', first_commit.id)
    >>>
    >>> repo.refs['refs/heads/backup'] == first_commit.id
    True
'''

__docformat__ = "restructuredtext"


from dulwich.pack import write_pack_objects

# copied from dulwich/client.py
# https://github.com/jelmer/dulwich/blob/dulwich-0.8.5/dulwich/client.py#L426-L459
def _send_pack(self, path, determine_wants, generate_pack_contents,
              progress=None):
    """Upload a pack to a remote repository.

    :param path: Repository path
    :param generate_pack_contents: Function that can return a sequence of the
        shas of the objects to upload.
    :param progress: Optional callback called with progress updates

    :raises SendPackError: if server rejects the pack data
    :raises UpdateRefsError: if the server supports report-status
                             and rejects ref updates
    """
    proto, unused_can_read = self._connect('receive-pack', path)
    old_refs, server_capabilities = self._read_refs(proto)
    negotiated_capabilities = self._send_capabilities & server_capabilities
    try:
        new_refs = determine_wants(old_refs)
    except:
        proto.write_pkt_line(None)
        raise
    if new_refs is None:
        proto.write_pkt_line(None)
        return old_refs
    (have, want) = self._handle_receive_pack_head(proto,
        negotiated_capabilities, old_refs, new_refs)
    if not want and old_refs == new_refs:
        return new_refs
    objects = generate_pack_contents(have, want)

    # see https://bugs.launchpad.net/dulwich/+bug/960169 for detail
    # simply remove `if len(objects) > 0:` is OK, since we don't delete any
    # branch

    # if len(objects) > 0:
    #     entries, sha = write_pack_objects(proto.write_file(), objects)

    entries, sha = write_pack_objects(proto.write_file(), objects)

    self._handle_receive_pack_tail(proto, negotiated_capabilities,
        progress)
    return new_refs


def sos_branch(client, path, branch, sha):
    def determine_wants(refs):
        new_refs = refs.copy()
        new_refs['refs/heads/'+branch] = sha
        return new_refs

    def generate_pack_contents(have, want):
        return []

    _send_pack(client, path, determine_wants, generate_pack_contents)


if __name__ == '__main__':
    import sys
    from dulwich.client import get_transport_and_path

    try:
        uri, branch, sha = sys.argv[1:]
    except ValueError:
        print >>sys.stderr, "sos-branch.py repo branch sha"
        quit(1)

    client, path = get_transport_and_path(uri)
    sos_branch(client, path, branch, sha)
