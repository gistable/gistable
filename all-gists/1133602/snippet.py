'''
@author Josh Bjornson

This work is licensed under the Creative Commons Attribution-ShareAlike 3.0 Unported License.
To view a copy of this license, visit http://creativecommons.org/licenses/by-sa/3.0/
or send a letter to Creative Commons, 171 Second Street, Suite 300, San Francisco, California, 94105, USA.
'''
# Plugin to provide access to the history of accessed files:
# https://gist.github.com/1133602
#
# The plugin stores a JSON file with the file history.
#
# Note: I tried checking for file existence in the history but this
# took more time than expected (especially with networked files) and
# made the plugin quite unresponsive.  The compromise is a command
# to cleanup the current project (with the option to clean up the
# global list as well).  The cleanup will remove any files in the
# project history that don't exist.
#
# To run the plugin:
# view.run_command("open_recently_closed_file")
# view.run_command("cleanup_file_history")
#
# Keymap entries:
# { "keys": ["ctrl+shift+t"], "command": "open_recently_closed_file"},
# { "keys": ["ctrl+alt+shift+t"], "command": "open_recently_closed_file", "args": {"show_quick_panel": false}  },
# { "keys": ["ctrl+alt+shift+t"], "command": "open_recently_closed_file", "args": {"current_project_only": false}  },
# { "keys": ["ctrl+alt+shift+c"], "command": "cleanup_file_history", "args": {"current_project_only": false}  },
#
# TODO use api function (not yet available) to get the project name/id (rather than using a hash of the project folders)
# TODO Get the settings below from a sublime-settings file?

import sublime
import sublime_plugin
import os
import hashlib
import json

# Maximum number of history entries we should keep (older entries truncated)
GLOBAL_MAX_ENTRIES = 100
PROJECT_MAX_ENTRIES = 50

# Which position to open a file at when the saved index in no longer valid
# (e.g. after a migration or if the saved index is non-existent).
# Options are: next tab and last tab
(TAB_POSITION_NEXT, TAB_POSITION_LAST) = ('next', 'last')
DEFAULT_NEW_TAB_POSITION = TAB_POSITION_NEXT

# Print out the debug text?
PRINT_DEBUG = False

# Should we show a preview of the history entries?
SHOW_FILE_PREVIEW = True

# Helper methods for "logging" to the console.
def debug(text):
    if PRINT_DEBUG:
        log(text)


def log(text):
    print('[%s] %s' % ('FileHistory', text))


# Class to read and write the file-access history.
class FileHistory(object):
    _instance = None

    """Basic singleton implementation"""
    @classmethod
    def instance(cls):
        if not cls._instance:
            cls._instance = cls()
        return cls._instance

    """Class to manage the file-access history"""
    def __init__(self):
        self.history_file = os.path.join(sublime.packages_path(), 'User', 'FileHistory.json')

        self.history = {}
        self.__load_history()

        self.calling_view = None

    def get_current_project_key(self):
        m = hashlib.md5()
        for path in sublime.active_window().folders():
            m.update(path.encode('utf-8'))
        project_key = m.hexdigest()

        # Try to use project_file_name (available in ST3 build 3014)
        # Note: Although it would be more appropriate, the name of the workspace is not available
        if hasattr(sublime.active_window(), 'project_file_name'):
            project_filename = sublime.active_window().project_file_name()
            if not project_filename:
                return project_key

            # migrate the old history entry (if it exists)
            if project_key in self.history:
                self.history[project_filename] = self.history[project_key]
                del(self.history[project_key])

            # use the new project key
            project_key = project_filename

        return project_key

    def __load_history(self):
        debug('Loading the history from file ' + self.history_file)
        if not os.path.exists(self.history_file):
            return

        f = open(self.history_file, 'r')
        try:
            updated_history = json.load(f)
        finally:
            f.close()

        self.history = updated_history

    def __save_history(self):
        debug('Saving the history to file ' + self.history_file)
        f = open(self.history_file, mode='w+')
        try:
            json.dump(self.history, f, indent=4)
            f.flush()
        finally:
            f.close()

    def get_history(self, current_project_only=True):
        """Return the requested history (global or project-specific): opened files followed by closed files"""

        # Make sure the history is loaded
        if len(self.history) == 0:
            self.__load_history()

        # Load the requested history (global or project-specific)
        if current_project_only:
            project_name = self.get_current_project_key()
        else:
            project_name = 'global'

        # Return the list of closed and opened files
        if project_name in self.history:
            return self.history[project_name]['closed'] + self.history[project_name]['opened']
        else:
            debug('WARN: Project %s could not be found in the file history list - returning an empty history list' % (project_name))
            return []

    def __ensure_project(self, project_name):
        """Make sure the project nodes exist (including 'opened' and 'closed')"""
        if project_name not in self.history:
            self.history[project_name] = {}
            self.history[project_name]['opened'] = []
            self.history[project_name]['closed'] = []

    def add_view(self, view, history_type):
        # Get the file details from the view
        filename = os.path.normpath(view.file_name()) if view.file_name() else None
        # Only keep track of files that exist (that have already been saved)
        if filename != None:
            project_name = self.get_current_project_key()
            (group, index) = sublime.active_window().get_view_index(view)

            if os.path.exists(filename):
                # Add to both the project-specific and global histories
                self.__add_to_history(project_name, history_type, filename, group, index)
                self.__add_to_history('global', history_type, filename, group, index)
            else:
                # If the file doesn't exist then remove it from the lists
                debug('The file no longer exists, so it has been removed from the history: ' + filename)
                self.__remove(project_name, filename)
                self.__remove('global', filename)

            self.__save_history()

    def __add_to_history(self, project_name, history_type, filename, group, index):
        debug('Adding %s file to project %s with group %s and index %s: %s' % (history_type, project_name, group, index, filename))

        # Make sure the project nodes exist
        self.__ensure_project(project_name)

        # Remove the file from the project list then
        # add it to the top (of the opened/closed list)
        self.__remove(project_name, filename)
        node = {'filename': filename, 'group':group, 'index':index}
        self.history[project_name][history_type].insert(0, node)

        # Make sure we limit the number of history entries
        max_num_entries = GLOBAL_MAX_ENTRIES if project_name == 'global' else PROJECT_MAX_ENTRIES
        self.history[project_name][history_type] = self.history[project_name][history_type][0:max_num_entries]

    def __remove(self, project_name, filename):
        # Only continue if this project exists
        if project_name not in self.history:
            return

        # Remove any references to this file from the project
        for history_type in ('opened', 'closed'):
            for node in iter(self.history[project_name][history_type]):
                if node['filename'] == filename:
                    self.history[project_name][history_type].remove(node)

    def clean_history(self, project_name):
        # Only continue if this project exists
        if project_name not in self.history:
            sublime.status_message("This project does not have any history")
            return

        # Remove any non-existent files from the project
        for history_type in ('opened', 'closed'):
            for node in reversed(self.history[project_name][history_type]):
                if not os.path.exists(node['filename']):
                    debug('Removing non-existent file from the project: %s' % (node['filename']))
                    self.history[project_name][history_type].remove(node)

        self.__save_history()
        sublime.status_message("File history cleaned")


class OpenRecentlyClosedFileEvent(sublime_plugin.EventListener):
    """class to keep a history of the files that have been opened and closed"""

    def on_close(self, view):
        FileHistory.instance().add_view(view, 'closed')

    def on_load(self, view):
        window = sublime.active_window()

        # If this view is being previewed (transient), then don't trigger the file history event
        add_to_history = True
        if hasattr(window, 'transient_view_in_group'):
            if view == window.transient_view_in_group(window.active_group()):
                add_to_history = False

        if add_to_history:
            FileHistory.instance().add_view(view, 'opened')


class CleanupFileHistoryCommand(sublime_plugin.WindowCommand):
    def run(self, current_project_only=True):
        # Cleanup the current project
        h = FileHistory.instance()
        h.clean_history(h.get_current_project_key())

        # If requested, also cleanup the global history
        if not current_project_only:
            h.clean_history('global')


class OpenRecentlyClosedFileCommand(sublime_plugin.WindowCommand):
    """class to either open the last closed file or show a quick panel with the recent file history (closed files first)"""

    def run(self, show_quick_panel=True, current_project_only=True):
        # Remember the view that the command was run from (aka the "calling" view), so:
        # (1) we can return to the "calling" view if the user cancels
        # (2) we can show something if a file in the history no longer exists
        FileHistory.instance().calling_view = sublime.active_window().active_view()

        # Prepare the display list with the file name and path separated
        self.history_list = FileHistory.instance().get_history(current_project_only)
        display_list = []
        for node in self.history_list:
            file_path = node['filename']
            display_list.append([os.path.basename(file_path), os.path.dirname(file_path)])

        if show_quick_panel:
            # The new ST3 API supports an "on_highlight" function in the "show_quick_panel" call
            if int(sublime.version()) >= 3000:
                self.window.show_quick_panel(display_list, self.open_file, on_highlight=self.show_preview)
            else:
                self.window.show_quick_panel(display_list, self.open_file)
        else:
            self.open_file(0)


    def is_valid(self, selected_index):
        return selected_index >= 0 and selected_index < len(self.history_list)


    # Note: This function will never be called in ST2
    def show_preview(self, selected_index):
        if not SHOW_FILE_PREVIEW:
            return
        if self.is_valid(selected_index):
            # Preview the file if it exists, otherwise show the previous view (aka the "calling_view")
            node = self.history_list[selected_index]
            if os.path.exists(node['filename']):
                self.window.open_file(node['filename'], sublime.TRANSIENT)
            else:
                sublime.active_window().focus_view( FileHistory.instance().calling_view )


    def open_file(self, selected_index):
        if self.is_valid(selected_index):
            node = self.history_list[selected_index]

            # Get the group of the new view (the currently active group is the default)
            group = node['group']
            if group < 0 or group >= self.window.num_groups():
                group = self.window.active_group()

            # Get the alternative tab index (in case the saved index in no longer valid):
            # The file could be opened in the last tab (max_index) or after the current tab (next_index)...
            max_index = len(self.window.views_in_group(group))
            if max_index:
                next_index = self.window.get_view_index(self.window.active_view_in_group(group))[1] + 1
            else:
                next_index = 0

            # Get the index of the new view
            index = node['index']
            if index < 0 or index > max_index:
                index = next_index if DEFAULT_NEW_TAB_POSITION == TAB_POSITION_NEXT else max_index

            debug('Opening file in group %s, index %s (based on saved group %s, index %s): %s' % (group, index, node['group'], node['index'], node['filename']))

            # Open the file and position the view correctly
            new_view = self.window.open_file(node['filename'])
            self.window.set_view_index(new_view, group, index)

            # Add the file we just opened to the FileHistory
            FileHistory.instance().add_view(new_view, 'opened')
        else:
            # The user cancelled the action - give the focus back to the "calling" view
            sublime.active_window().focus_view( FileHistory.instance().calling_view )
            FileHistory.instance().calling_view = None
