import subprocess
import sublime, sublime_plugin
import re

# RailsCopyMigrationVersion
# ========
# 
# A Sublime Text 2 plugin that provides `copy_migration_version` command to copy migration version of current migration file.
#
class CopyMigrationVersionCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        match = re.search('\d{14}', self.view.file_name())
        if match:
            version = match.group()
            sublime.set_clipboard(version)
            sublime.status_message("copied: %s" % version)