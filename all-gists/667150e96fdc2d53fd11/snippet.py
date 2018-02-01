from __future__ import division

import os
import numpy
from PIL import Image, ImageDraw


class Renderer():
    def __init__(
            self, size=(640, 480), sampler=None,
            num_frames=100, samples_per_frame=1, fps=30, bg=None,
            save_dir="/tmp/sketch_images"):
        self.size = size
        self.sampler = sampler
        self.num_frames = num_frames
        self.samples_per_frame = samples_per_frame
        self.fps = fps
        self.bg = bg
        self.duration = num_frames*fps
        self.save_dir = os.path.expanduser(save_dir)

    def render(self):
        if self.sampler is None:
            raise Exception("No sampler defined for {}".format(self))

        self.prepare_render_dir()

        for frame_num in xrange(self.num_frames):
            cur_frame = numpy.zeros(
                (self.size[0], self.size[1], 3),
                numpy.float
            )
            for sample_num in xrange(self.samples_per_frame):
                sub_time = sample_num/self.samples_per_frame
                time = (frame_num + sub_time)/self.num_frames

                cur_sample = Image.new("RGB", self.size, self.bg)

                # TODO: Replace Pillow's shitty .Draw() module with
                # something useful.
                cur_drawer = ImageDraw.Draw(cur_sample)
                self.sampler(time, cur_drawer)

                numpy_sample = numpy.array(cur_sample, dtype=numpy.float)
                cur_frame += numpy_sample/self.samples_per_frame

            converted_frame = numpy.array(
                numpy.round(cur_frame),
                dtype=numpy.uint8
            )
            frame_image = Image.fromarray(converted_frame, mode="RGB")
            self.save_frame(frame_num, frame_image)

    def prepare_render_dir(self):
        path = self.save_dir
        if os.path.isdir(path):
            # Get rid of any existing (possibly conflicting) frames
            os.system("rm {}".format(os.path.join(path, "f*.png")))
        elif not os.path.exists(path):
            os.mkdir(path)
        else:
            raise Exception("Destination isn't a directory")

    def save_frame(self, frame_num, frame):
        # TODO: This breaks at over 999 frames
        filename = "f{:03d}.png".format(frame_num)
        path = os.path.join(self.save_dir, filename)
        frame.save(path)

    def render_gif(self, filename):
        self.render()
        # Using Graphicsmagick manually instead of Pillow's existing
        # gif conversion because... Well, it's shit.
        os.system("gm convert -delay {fps} {files} {output}".format(
            fps=(100/self.fps),
            files=(os.path.join(self.save_dir, "f*.png")),
            output=(filename)
        ))
