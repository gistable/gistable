'''
Use with Kivy Remote Shell:

    cat test.py | ssh -p8000 -t -t admin@192.168.x.x
'''

from jnius import autoclass, cast
from android.runnable import Runnable

activity = autoclass('org.renpy.android.PythonActivity').mActivity
AnalogClock = autoclass('android.widget.AnalogClock')
WebView = autoclass('android.webkit.WebView')
LinearLayout = autoclass('android.widget.LinearLayout')
LayoutParams = autoclass('android.view.ViewGroup$LayoutParams')

global clock
def create_clock():
    # works
    global clock
    clock = AnalogClock(activity)
    activity.addContentView(clock, LayoutParams(-1, -1))

def remove_clock():
    global clock
    cast(LinearLayout, clock.getParent()).removeView(clock)

def create_webview():
    # works
    webview = WebView(activity)
    activity.setContentView(webview)
    webview.loadData('<html><body>Hello<b>World</b></body></html>', 'text/html',
            None)

def create_clock2():
    # failed, sdlview?
    layout = LinearLayout(activity)
    layout.addView(activity.mView)
    clock = AnalogClock(activity)
    layout.addView(clock)
    activity.setContentView(layout)

def sdl_view():
    # failed, "Invalid indirect reference..."
    activity.setContentView(activity.mView)

def run(f, *args, **kwargs):
    # args/kwargs to runnable was a bug, fixed in main
    Runnable(f)(args, kwargs)

run(create_clock)
