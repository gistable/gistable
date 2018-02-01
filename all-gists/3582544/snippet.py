from kivy.app import App
from kivy.uix.widget import Widget
from kivy.graphics import Rectangle
from kivy.graphics.texture import Texture


class MyWidget(Widget):
    def __init__(self, **args):
        super(MyWidget, self).__init__(**args)

        self.texture = Texture.create(size=(2, 1), colorfmt='rgb')

        color1 = 0
        color2 = 255

        buf = ''.join(map(chr, [color1, color2]))

        self.texture.blit_buffer(buf, colorfmt='rgb', bufferfmt='ubyte')

        with self.canvas:
            Rectangle(pos=self.pos, size=self.size, texture=self.texture)


class TestApp(App):
    def build(self):
        return MyWidget(size=(200, 200))


if __name__ == '__main__':
    TestApp().run()