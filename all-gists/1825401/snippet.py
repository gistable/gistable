# CTags based autocompletion plugin for Sublime Text 2
# You can add the file to the User Package in ~/Library/Application Support/Sublime Text 2/Packages and restart Sublime Text 2.
# generate the .tags file in your project root with "ctags -R -f .tags"

import sublime, sublime_plugin, os

class AutocompleteAll(sublime_plugin.EventListener):

    def on_query_completions(self, view, prefix, locations):
        tags_path = view.window().folders()[0]+"/.tags"
        results=[]
        if (not view.window().folders() or not os.path.exists(tags_path)): #check if a project is open and the .tags file exists
            return results
        f=os.popen("grep -i '^"+prefix+"' '"+tags_path+"' | awk '{ print $1 }'") # grep tags from project directory .tags file
        for i in f.readlines():
            results.append([i.strip()])
        results = [(item,item) for sublist in results for item in sublist] #flatten
        results = list(set(results)) # make unique
        results.sort() # sort
        return results