import objc
from AppKit import *
from Foundation import *

class Alert(object):
    
    def __init__(self, messageText):
        super(Alert, self).__init__()
        self.messageText = messageText
        self.informativeText = ""
        self.buttons = []
    
    def displayAlert(self):
        alert = NSAlert.alloc().init()
        alert.setMessageText_(self.messageText)
        alert.setInformativeText_(self.informativeText)
        alert.setAlertStyle_(NSInformationalAlertStyle)
        for button in self.buttons:
            alert.addButtonWithTitle_(button)
        NSApp.activateIgnoringOtherApps_(True)
        self.buttonPressed = alert.runModal()
    
def alert(message="Default Message", info_text="", buttons=["OK"]):    
    ap = Alert(message)
    ap.informativeText = info_text
    ap.buttons = buttons
    ap.displayAlert()
    return ap.buttonPressed

def cocoa_dialogs(fn):
    class MainRunner(object):
        def runWithShutdown_(self, timer):
            fn()
            NSApp.stop_(None)

        def run(self):
            NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(1, self, 'runWithShutdown:', "", False)                    
                    
    def wrapped():
        NSApplication.sharedApplication()
        MainRunner().run()
        NSApp.run()
        
    return wrapped

@cocoa_dialogs
def main():
    alert("Hello!", "We'll rule the world...in Python!", ["OK"])
    print "I love it"
    #big time computation
    x = 10000 + 1
    alert("Some Error?", "Maybe something bad happened?", ["Oh Well", "Thanks"])
    print "End of the code"
    
if __name__ == "__main__":
    main()
