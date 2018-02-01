import kivy
kivy.require('1.8.0')

from kivy.app import App
from kivy.lang import Builder

from jnius import autoclass
PythonActivity = autoclass('org.renpy.android.PythonActivity')
View = autoclass('android.view.View')
Params = autoclass('android.view.WindowManager$LayoutParams')

from android.runnable import run_on_ui_thread

root = Builder.load_string('''
BoxLayout:
    orientation: 'vertical'
    Button:
        text: 'Set Flag'
        on_press: app.setflag()
    Button:
        text: 'Clear Flag'
        on_press: app.clearflag()
''')

class DimTestApp(App):
    def build(self):
        return root

    #@run_on_ui_thread
    #def set_systemui_visibility(self, options):
    #   PythonActivity.mActivity.getWindow().getDecorView().setSystemUiVisibility(options)
    #
    #def dim(self, *args):
    #   self.set_systemui_visibility(View.SYSTEM_UI_FLAG_LOW_PROFILE)
    #
    #def undim(self, *args):
    #   self.set_systemui_visibility(0)

    @run_on_ui_thread
    def android_setflag(self):
        PythonActivity.mActivity.getWindow().addFlags(Params.FLAG_KEEP_SCREEN_ON)

    def setflag(self, *args):
        self.android_setflag()

    @run_on_ui_thread
    def android_clearflag(self):
        PythonActivity.mActivity.getWindow().clearFlags(Params.FLAG_KEEP_SCREEN_ON)

    def clearflag(self, *args):
        self.android_clearflag()

if __name__ == '__main__':
    DimTestApp().run()
