from kivy.app import App
from kivy.lang import Builder

from jnius import autoclass

PythonActivity = autoclass('org.renpy.android.PythonActivity')
Intent = autoclass('android.content.Intent')
String = autoclass('java.lang.String')

root = Builder.load_string('''
Button:
    text: 'Share!'
    on_press: app.share()
''')

class TestApp(App):
    def build(self):
        return root

    def share(self):
        intent = Intent()
        intent.setAction(Intent.ACTION_SEND)
        intent.putExtra(Intent.EXTRA_TEXT, String('test share text'))
        intent.setType('text/plain')
        chooser = Intent.createChooser(intent, String('Share...'))
        PythonActivity.mActivity.startActivity(chooser)

if __name__ == '__main__':
    TestApp().run()
