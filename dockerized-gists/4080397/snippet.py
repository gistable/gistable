import sys
import select
import gevent

def stdin_ready():
    infds, outfds, erfds = select.select([sys.stdin], [], [], 0)
    if infds:
        return True
    else:
        return False

def inputhook_gevent():
    try:
        while not stdin_ready():
            gevent.sleep(0.001)
    except KeyboardInterrupt:
        pass

    return 0

# install the gevent inputhook
from IPython.lib.inputhook import inputhook_manager
inputhook_manager.set_inputhook(inputhook_gevent)
inputhook_manager._current_gui = 'gevent'

# First import the embeddable shell class
from IPython.frontend.terminal.embed import InteractiveShellEmbed