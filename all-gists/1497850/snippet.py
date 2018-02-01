"""==============================
Branded IPython Notebook Launcher
=================================

Executing this module will create an overlay over ipython notebooks own static
files and templates and overrides static files and templates and copies over all
example notebooks into a temporary folder and launches the ipython notebook server.

You can use this to offer an interactive tutorial for your library/framework/...


To use this script properly, create three folders in the same folder this script
resides in:

    parent
    |
    +- this_script.py
    |
    +- templates/
    |  |
    |  ...
    |
    +- static/
    |  |
    |  ...
    |
    |+ notebooks/
    |  |
    |  ...


The folders templates and static may be empty, but must exist. Read the
docstring of merge_dirs to find out how these folders are treated.

If you put those folders anywhere else, change the variables in the
Configuration section below.

In your setup.py you can add the following to your entry_points:

      [console_scripts]
      my_framework_tutorial = framework.examples.notebooks.this_script:launch_notebook_server

and a binary will be created for the user's system that launches this script.

Additionally, add these package_data entries, so that the static files
get installed, too:

      package_data = {
          'framework.examples.notebooks':
              ['notebooks/*', 'static/**/*', 'templates/*'],
          }


License
-------

Copyright (c) 2011, Timo Paulssen
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * The name of the author may not be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL TIMO PAULSSEN BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


Revision History
----------------

   1.0 2011-12-19
        First release.

   1.1 2011-12-20
        Don't use os.system for starting the notebook.
        Cleaner clean-up.
"""

import os
import shutil
import tempfile
from itertools import izip

try:
    from IPython.frontend.html.notebook import notebookapp
except ImportError:
    print "You don't seem to have IPython installed, or the dependencies of "
    print "ipython notebook are not met."

    raise

"""==================
Configuration section
=====================
"""

"""This is the base path in which the modified templates/, static/ and the
example notebooks can be found:"""
BASE_PATH = os.path.dirname(__file__)


"""By default, the template, static and notebooks folder will be assumed inside
BASE_PATH:"""
TEMPLATE_PATH = os.path.join(BASE_PATH, "templates")
STATIC_PATH = os.path.join(BASE_PATH, "static")
EXAMPLES_PATH = os.path.join(BASE_PATH, "notebooks")


"""These are the folders from which the original templates and static files are
taken. You should not have to change this. It will usually be correct."""
NOTEBOOK_BASE_PATH = os.path.dirname(notebookapp.__file__)
NOTEBOOK_TEMPLATE_PATH = os.path.join(NOTEBOOK_BASE_PATH, "templates")
NOTEBOOK_STATIC_PATH = os.path.join(NOTEBOOK_BASE_PATH, "static")

"""This name will be the prefix for the temporary folder"""
PROJECT_NAME = "my_pretty_framework"



"""These extra arguments go directly between the tornado arguments and the
arguments passed to this script on the commandline:"""
#notebook_extra_args = ["--gui=qt"] # for example
notebook_extra_args = [""]


"""=========
Code section
============
"""

def merge_dirs(base, overlay, target, preserve_originals=False):
    """This function merges a base and an overlay folder into a target folder.

    If a folder exists in base or overlay only, it will be symlinked
    into the target.

    If a folder exists in both, the folder is created in the target and
    merging continues with the contents of both folders.

    If a file exists in base or overlay only, it will be symlinked from base.

    If a file exists in both and preserve_originals is True, the file from
    base will be symlinked here with a original_ prefix. The file from the
    overlay will be symlinked into the target.
    """

    def replace_prefix(prefix, path, new_prefix):
        assert path.startswith(prefix)
        if path.startswith("/"):
            path = path[1:]
        return os.path.join(new_prefix, path[len(prefix):])

    base_w = os.walk(base, followlinks=True)
    overlay_w = os.walk(overlay, followlinks=True)

    from_base_dirs = []
    from_over_dirs = []
    from_base_files = []
    from_over_files = []
    preserved_originals = []

    # walk the base and overlay trees in parallel
    for (base_t, over_t) in izip(base_w, overlay_w):
        (base_path, base_dirs, base_files) = base_t
        (over_path, over_dirs, over_files) = over_t

        # don't recurse into dirs that are only in base or only in overlay.
        # instead, just symlink them.
        # this keeps both walkers in sync.
        for subdir in set(base_dirs[:] + over_dirs[:]):
            if subdir not in over_dirs:
                base_dirs.remove(subdir)
                from_base_dirs.append(os.path.join(base_path, subdir))
            elif subdir not in base_dirs:
                over_dirs.remove(subdir)
                from_over_dirs.append(os.path.join(base_path, subdir))

        for fn in set(base_files[:] + over_files[:]):
            if fn in over_files and fn in base_files and preserve_originals:
                preserved_originals.append(os.path.join(base_path, fn))
            if fn not in over_files:
                from_base_files.append(os.path.join(base_path, fn))
            else:
                from_over_files.append(os.path.join(over_path, fn))

    # link full directories over
    for source, dirlist in ((base, from_base_dirs), (overlay, from_over_dirs)):
        for dir_link in dirlist:
            os.symlink(dir_link, replace_prefix(source, dir_link, target))

    # link files over.
    for source, filelist in ((base, from_base_files),
                             (overlay, from_over_files),
                             (base, preserved_originals)):
        for file_link in filelist:
            target_file = replace_prefix(source, file_link, target)

            # preserved originals get an original_ prefix
            if filelist is preserved_originals:
                tfp, tfn = os.path.dirname(target_file), os.path.basename(target_file)
                target_file = os.path.join(tfp, "original_" + tfn)

            parent_dir = os.path.dirname(target_file)
            if not os.path.exists(parent_dir):
                os.makedirs(parent_dir)
            os.symlink(file_link, target_file)


def create_overlay():
    """This function copies all files from the source to the target and then
    links all missing files from IPython itself to the target.

    Templates that are overridden will be linked to orig_{filename}, so that
    changes to templates can just use tornadowebs own template extension scheme.

    It returns a tuple with the temporary path as well as a dictionary with keys
    'template_path' and 'static_path', which are absolute paths to the merged
    templates and static files."""

    # create the temporary folder where overlay and base are merged
    path = tempfile.mkdtemp(prefix=PROJECT_NAME + "_tutorial")

    template_path = os.path.join(path, "templates")
    static_path = os.path.join(path, "static")
    os.mkdir(template_path)
    os.mkdir(static_path)

    merge_dirs(NOTEBOOK_TEMPLATE_PATH, TEMPLATE_PATH, template_path, True)
    merge_dirs(NOTEBOOK_STATIC_PATH, STATIC_PATH, static_path)

    return path, {'template_path': template_path, 'static_path': static_path}

def copy_example_notebooks(target_path):
    shutil.copytree(EXAMPLES_PATH, os.path.join(target_path, "notebooks"))

def launch_notebook_server():
    import sys
    import signal
    base_path, settings = create_overlay()
    copy_example_notebooks(base_path)

    print
    print "running notebook overlay from", base_path
    print
    print "hit ctrl-c to exit the tutorial"
    print

    app = notebookapp.NotebookApp()
    app.initialize(argv=[
              '''--NotebookApp.webapp_settings=%s''' % (settings),
              '''--NotebookManager.notebook_dir="%s"''' % (os.path.join(base_path, "notebooks"))] +
              notebook_extra_args +
              sys.argv[1:])

    # somewhere in initialize, the SIGINT handler gets set to be ignored.
    # we have to undo that
    signal.signal(signal.SIGINT, signal.default_int_handler)

    try:
        app.start()
    except KeyboardInterrupt:
        pass
    finally:
        print
        print "deleting", base_path
        shutil.rmtree(base_path)

    print "goodbye"

if __name__ == "__main__":
    launch_notebook_server()
