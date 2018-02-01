# Run this one-liner from the Sublime Text console if you need to revert all open documents
[ view.run_command('revert') for view in sublime.Window.views(sublime.active_window()) ]