import sublime, sublime_plugin

class Copy_on_select(sublime_plugin.EventListener):
     def on_selection_modified(self, view):
        for region in view.sel(): 
            if not region.empty():  
                print(view.substr(region))  
                view.run_command('copy')