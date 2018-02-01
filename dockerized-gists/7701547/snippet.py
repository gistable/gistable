import sys, os, threading
if sys.platform == 'darwin':
    def raise_window():
        os.system("""osascript -e 'tell app "Finder" to set frontmost of process "Python" to true'""")
    threading.Timer(0.1, raise_window).start()
