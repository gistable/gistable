import sublime, sublime_plugin, functools

class IdleWatcher(sublime_plugin.EventListener):  
    pending = 0  
      
    def handleTimeout(self, view):  
        self.pending = self.pending - 1  
        if self.pending == 0:   
            self.on_idle(view)  

    def on_modified(self, view):  
        self.pending = self.pending + 1  
        # Ask for handleTimeout to be called in N ms  
        sublime.set_timeout(functools.partial(self.handleTimeout, view), 800)  
  
    def on_idle(self, view):  
        view.run_command("save")
        print "Current document saved"
