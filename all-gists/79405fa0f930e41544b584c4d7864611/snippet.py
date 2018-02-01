from kivy.app import App
from kivy.lang import Builder
from kivy.properties import NumericProperty
from kivy.uix.widget import Widget
from kivy.clock import Clock


KV = '''
#:import degrees math.degrees
#:import sin math.sin
#:import pi math.pi

Loading:
    angle_start: app.time
    angle_end: app.time + (2.5 * pi * sin(sin(app.time) ** 2. / 2 + .15))

    canvas:
        SmoothLine:
            ellipse:
                (
                self.x + self.width / 4.,
                self.center_y - self.width / 4.,
                self.width / 2.,
                self.width / 2.,
                degrees(self.angle_start or 0),
                degrees(self.angle_end or 0)
                )
            width: dp(50)
            cap: 'none'
            overdraw_width: 5
'''


class Loading(Widget):
    pass


class LoadingApp(App):
    time = NumericProperty()

    def build(self):
        Clock.schedule_interval(self.update_time, 0)
        return Builder.load_string(KV)

    def update_time(self, dt):
        self.time += dt


if __name__ == '__main__':
    LoadingApp().run()
