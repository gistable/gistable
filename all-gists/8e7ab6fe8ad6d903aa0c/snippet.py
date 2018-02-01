import os
import shutil
import synapseclient
from synapseclient import Project, Folder, Entity, File

syn = synapseclient.login()


def download(entity, directory=None, verbose=False, indent=0):
    """
    Recusively download a Project or Folder from Synapse.

    :param entity: A Synapse Entity or Synapse ID.
    :param directory: The destination directory for the downloaded files.
    :param verbose: Print a directory tree of the downloaded project or folder.
    :param indent: keeps track of indent level for printing during recursive calls.
    """
    if not directory:
        directory = os.getcwd()
    entity = syn.get(entity, downloadLocation=directory, downloadFile=True)
    if isinstance(entity, Project) or isinstance(entity, Folder):
        if verbose:
            print("%s%s/" % (" "*indent, entity.name))
        subdir = os.path.join(directory, entity.name)
        if not os.path.exists(subdir):
            os.makedirs(subdir)
        results = syn.chunkedQuery('select id, name from entity where parentId=="%s"' % entity.id)
        for result in results:
            download(result['entity.id'], directory=subdir, verbose=verbose, indent=indent+2)
    else:
        if verbose:
            print("%s%s" % (" "*indent, entity.name))
