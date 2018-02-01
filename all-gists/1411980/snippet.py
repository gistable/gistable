from __future__ import division

import os
import subprocess

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

try:
    from PIL import Image
except ImportError:
    import Image

class ImageMagickConversion(object):

    GRAVITY_CHOICES = ('northwest', 'north', 'northeast', 'west', 'center',
        'east', 'southwest', 'south', 'southeast')

    def __init__(self, image=None, image_path=None, output_format=None,
            image_magick_path='/usr/bin/', debug=False):
        if image is None and image_path is None:
            raise ValueError('Either an image or image path is required.')

        self.args = []
        self.out_format = None

        self.image = image
        self.image_path = image_path
        self.output_format = output_format
        self.image_magick_path = image_magick_path
        self.debug = debug

    def _cache_image_properties(self):
        try:
            pil_image = Image.open(self.image or self.image_path)
        except IOError:
            raise ValueError("Invalid image")
        self._width, self._height = pil_image.size
        self._format = pil_image.format
        if self.image:
            # reset the image to so it can be read again if needed
            self.image.reset()

    @property
    def width(self):
        if not hasattr(self, '_width'):
            self._cache_image_properties()
        return self._width

    @property
    def height(self):
        if not hasattr(self, '_height'):
            self._cache_image_properties()
        return self._height

    @property
    def format(self):
        if not hasattr(self, '_format'):
            self._cache_image_properties()
        return self._format

    def gravity(self, position):
        if position.lower() not in ImageMagickConversion.GRAVITY_CHOICES:
            raise ValueError("Invalid value for position.")
        self.args.extend(['-gravity', position])
        return self

    def crop(self, width, height, left=0, top=0):
        self.args.extend(['-crop', '%dx%d+%d+%d' % (width, height, left, top)])
        return self

    def resize(self, width, height, preserve_aspect_ratio=True,
            can_enlarge=False, outer=True):
        if preserve_aspect_ratio:
            if outer: # image can be bigger than resize box
                ratio = max(width / self.width, height / self.height)
            else: # image must fit within resize box
                ratio = min(width / self.width, height / self.height)
            if ratio >= 1 and not can_enlarge:
                return self
            width = int(round(self.width * ratio))
            height = int(round(self.height * ratio))
        self.args.extend(['-resize', '%dx%d' % (width, height)])
        return self

    def quality(self, quality):
        self.args.extend(['-quality', unicode(quality)])
        return self

    def _process_image(self, command, pre_input_args, post_input_args,
            input_image_path=None, input_image=None, output_image_path=None):

        # support pipe or filesystem i/o
        proc_kwargs = {}
        if input_image_path:
            input_arg = input_image_path
        else:
            input_arg = '-'
            proc_kwargs['stdin'] = subprocess.PIPE
        if output_image_path:
            output_arg = output_image_path
        else:
            output_arg = '-'
            proc_kwargs['stdout'] = subprocess.PIPE

        proc_args = [os.path.join(self.image_magick_path, command)]
        proc_args.extend(pre_input_args)
        proc_args.append(input_arg)
        proc_args.extend(post_input_args)
        if self.output_format:
            proc_args.append('%s:%s' % (self.output_format, output_arg))
        else:
            proc_args.append(output_arg)
        if self.debug:
            print 'ImageMagick: %s' % ' '.join(proc_args)
        proc = subprocess.Popen(proc_args, **proc_kwargs)

        if input_image:
            proc_input = input_image.read()
            input_image.reset()
        else:
            proc_input = None
        stdoutdata, stderrdata = proc.communicate(input=proc_input)

        if stdoutdata:
            new_image = StringIO()
            new_image.write(stdoutdata)
            return new_image
        else:
            return output_image_path

    def convert(self, output_image_path=None):
        args = ['-auto-orient']
        args.extend(self.args)

        return self._process_image('convert', [], args,
            input_image_path=self.image_path,
            input_image=self.image,
            output_image_path=output_image_path
        )

    def watermark(self, watermark_path, opacity=40, position='southeast',
            output_image_path=None):

        if position.lower() not in ImageMagickConversion.GRAVITY_CHOICES:
            raise ValueError("Invalid value for position.")

        if output_image_path:
            convert_image_path = self.convert(
                output_image_path=output_image_path)
            convert_image = None
        else:
            convert_image_path = None
            convert_image = self.convert()

        args = (['-dissolve', unicode(opacity), '-gravity', position,
            watermark_path])
        return self._process_image('composite', args, [],
            input_image_path=convert_image_path,
            input_image=convert_image,
            output_image_path=output_image_path
        )
