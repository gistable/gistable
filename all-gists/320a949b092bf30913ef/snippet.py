# AppData\Roaming\Sublime Text 3\Packages\User\default_syntax.py

import sublime, sublime_plugin

class DefaultSyntaxCommand(sublime_plugin.EventListener):
   def on_new(self, view):
    # Replace <Language> with desired default language
    # Check in AppData\Local\Sublime Text 3\Cache
    view.set_syntax_file('Packages/<Language>/<Language>.tmLanguage')