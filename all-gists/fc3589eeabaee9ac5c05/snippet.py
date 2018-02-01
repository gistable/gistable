import kivy
kivy.require('1.8.1')

from kivy.app import App
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.utils import interpolate
from time import time

root = Builder.load_string('''
Button:
''')

class TestApp(App):
    def build(self):
        return root
    
    def on_start(self):
        self.starttime = time()
        Clock.schedule_interval(self.update, 0)
    
    def update(self, *args):
        t = time() - self.starttime
        ft = 1 - abs(t % 2 - 1)
        color = interpolate((1, 0, 0, 1), (0, 0, 1, 1), 1. / ft)
        self.root.background_color = color
    

if __name__ == '__main__':
    TestApp().run()
