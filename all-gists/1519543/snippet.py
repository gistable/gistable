# This script allows you to do multiple find/replace operations in one pass. The find/replace
# pairs are defined in a file (defaults to ~/.st2_multiple_find_replace) using the format
#
# find <separator> replace

# By default, the separator is the hash-pointer (=>), but it can be changed if
# necessary (see below). To use multiple find and replace, save this code to a file in
# your Packages/User folder using whatever name you like. I use multiple_find_replace.py.
# Edit your user key bindings and pick whatever key combinations you want to trigger 
# these operations. On Mac OS X, I chose COMMAND+OPTION+M E to edit and COMMAND+OPTION+M R
# to replace. The actual key bindings are:
#
# { "keys": ["super+alt+m", "f"], "command": "multiple_find_replace", "args": {"operation": "find"} },
# { "keys": ["super+alt+m", "r"], "command": "multiple_find_replace", "args": {"operation": "replace"} }
#
# When you issue the multiple_find_replace command, if the file does not exist, it will
# be created and opened for editing. If the file does exist, it will be parsed for 
# find/replace pairs and the current file will be the operation's subject. In order to
# edit your find/replace pairs, issue the edit_multiple_find_replace command, which
# will either open or activate the search term file.
#
# To change the separator used in the search term file, include a comment at the top of
# the file like this:
#
# separator: ==
#
# changing the double equal to whatever ever separator you want to use. The script will
# then use that separator to split the line when parsing the find/replace pairs.
#
# All find/replace operations are done in a single edit, so a single undo returns the
# subject text to its original state. Also of importance is the pairs are processed
# in the order they appear in the file.
#
# At present, the find/replace operations work against the entire buffer. A future
# enhancement would be to operate against a selection only.

import sublime, sublime_plugin
import os

class MultipleFindReplaceCommand(sublime_plugin.WindowCommand):
    def run(self, operation):
        self.file_name = os.path.expanduser('~/.st2_multiple_find_replace')
        self.separator_key = 'separator:'
        self.separator = '=>'
        self.lines = None

        self.ensure_multiple_find_replace_file()

        if operation == 'find':
            self.find()
        else:
            self.replace()


    def ensure_multiple_find_replace_file(self):
        if not os.path.exists(self.file_name):
            contents = "# Put one find/replace pair on each line, separated by a separator. For example:\n"
            contents += "\n"
            contents += "ReplaceThis => WithThis\n"
            contents += "\n"
            contents += "# The default separator is =>. To change it, put the following line at the top\n"
            contents += "# of this file, replacing the double equal with whatever you want the separator\n"
            contents += "# to be:\n"
            contents += "\n"
            contents += "# separator: ==\n"

            with open(self.file_name, 'a') as the_file:
                the_file.write(contents)


    def find(self):
        self.window.open_file(self.file_name)


    def replace(self):
        self.load_file()

        view = self.window.active_view()
        edit = view.begin_edit()

        for line in self.lines:
            if line.startswith('#'):
                continue

            try:
                find, replace = line.split(self.separator)
            except:
                continue
            
            find = find.strip()
            replace = replace.strip()

            matches = view.find_all(find)
            matches.reverse()

            for region in matches:
                view.replace(edit, region, replace)

        view.end_edit(edit)


    def load_file(self):
        input_file = open(self.file_name, 'r')
        self.lines = input_file.readlines()
        input_file.close()

        for line in self.lines:
            if line.startswith('#'):
                pos = line.find(self.separator_key)
                if pos > 0:
                    junk, separator = line.split(self.separator_key)
                    self.separator = separator.strip()
                    break
