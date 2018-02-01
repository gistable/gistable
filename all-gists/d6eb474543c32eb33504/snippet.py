"""
MJpeg Viewer using pure Kivy + urllib
=====================================

.. author:: Mathieu Virbel <mat@meltingrocks.com>
"""

import io
import urllib
import threading
from kivy.uix.image import Image
from kivy.app import App
from kivy.properties import StringProperty
from kivy.core.image import Image as CoreImage
from kivy.clock import Clock
from collections import deque


class MjpegViewer(Image):

    url = StringProperty()

    def start(self):
        self.quit = False
        self._queue = deque()
        self._thread = threading.Thread(target=self.read_stream)
        self._thread.daemon = True
        self._thread.start()
        self._image_lock = threading.Lock()
        self._image_buffer = None
        Clock.schedule_interval(self.update_image, 1 / 30.)

    def stop(self):
        self.quit = True
        self._thread.join()
        Clock.unschedule(self.read_queue)

    def read_stream(self):
        stream = urllib.urlopen(self.url)
        bytes = ''
        while not self.quit:
            bytes += stream.read(1024)
            a = bytes.find('\xff\xd8')
            b = bytes.find('\xff\xd9')
            if a != -1 and b != -1:
                jpg = bytes[a:b + 2]
                bytes = bytes[b + 2:]

                data = io.BytesIO(jpg)
                im = CoreImage(data,
                               ext="jpeg",
                               nocache=True)
                with self._image_lock:
                    self._image_buffer = im

    def update_image(self, *args):
        im = None
        with self._image_lock:
            im = self._image_buffer
            self._image_buffer = None
        if im is not None:
            self.texture = im.texture
            self.texture_size = im.texture.size


if __name__ == "__main__":

    class MjpegViewerApp(App):
        def build(self):
            viewer = MjpegViewer(
                url=
                "http://195.235.198.107:3344/axis-cgi/mjpg/video.cgi?resolution=320x240")
            viewer.start()
            return viewer

    MjpegViewerApp().run()
