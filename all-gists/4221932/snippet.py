import commands
import sublime_plugin
import sublime

class WordCompletion(sublime_plugin.EventListener):
    def on_query_completions(self, view, prefix, locations):
        if len(prefix) < 3:
            return []

        words = self.look(view, prefix)
        return [(w.replace(prefix.lower(), prefix),) * 2 for w in words]

    def command(self, view):
        try:
            return view.settings().get("word_completion").get("command")
        except AttributeError:
            return "look"

    def look(self, view, prefix):
        result = commands.getoutput("%s %s" % (self.command(view), prefix))
        if len(result) > 0:
            return result.split("\n")
        else:
            return []