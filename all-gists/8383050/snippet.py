import sublime, sublime_plugin, re

class CountWordsInSelectionCommand(sublime_plugin.EventListener):

    def on_selection_modified(self, view):
        '''
        listen to event 'on_selection_modified' and count words in all selected
        regions when invoked.
        '''

        # clear status bar if nothing is selected
        if len(view.sel()) == 1 and view.sel()[0].size() == 0:
            view.set_status("words_in_selection", "")
            return

        count = 0
        for region in view.sel():
            for i in range(region.begin(), region.end()):
                if view.classify(i) & sublime.CLASS_WORD_START:
                    count += 1
        
        view.set_status("words_in_selection", "{} words".format(count))