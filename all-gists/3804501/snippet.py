#vsenc.py
#coding: utf-8

import sys
from subprocess import Popen, PIPE
import vapoursynth as vs


x264_binary_path = 'D:/tools/x86/x264.exe'
avconv_binary_path = 'D:/tools/x86/avconv.exe'


def enc_video(core, clip, cmdline):
    if clip.format.color_family == vs.RGB:
        clip = core.std.ShufflePlanes(clip, [1, 2, 0], vs.RGB)

    print(cmdline, file=sys.stderr)
    p = Popen(cmdline.split(), stdin=PIPE)
    clip.output(p.stdin)
    p.communicate()


def get_x264_csp(format):
    table = {vs.COMPATBGR32:('bgra',     'raw',                        8),
             vs.COMPATYUY2: ('yuyv422',  'lavf --input-fmt rawvideo',  8),
             vs.GRAY8:      ('gray',     'lavf --input-fmt rawvideo',  8),
             vs.GRAY16:     ('gray16',   'lavf --input-fmt rawvideo', 16),
             vs.RGB24:      ('gbrp',     'lavf --input-fmt rawvideo',  8),
             vs.RGB27:      ('gbrp9le',  'lavf --input-fmt rawvideo',  9),
             vs.RGB30:      ('gbrp10le', 'lavf --input-fmt rawvideo', 10),
             vs.RGB48:      ('gbrp16le', 'lavf --input-fmt rawvideo', 16),
             vs.YUV410P8:   ('yuv410p',  'lavf --input-fmt rawvideo',  8),
             vs.YUV411P8:   ('yuv411p',  'lavf --input-fmt rawvideo',  8),
             vs.YUV420P8:   ('i420',     'raw',                        8),
             vs.YUV420P9:   ('i420',     'raw',                        9),
             vs.YUV420P10:  ('i420',     'raw',                       10),
             vs.YUV420P16:  ('i420',     'raw',                       16),
             vs.YUV422P8:   ('i422',     'raw',                        8),
             vs.YUV422P9:   ('i422',     'raw',                        9),
             vs.YUV422P10:  ('i422',     'raw',                       10),
             vs.YUV422P16:  ('i422',     'raw',                       16),
             vs.YUV444P8:   ('i444',     'raw',                        8),
             vs.YUV444P9:   ('i444',     'raw',                        9),
             vs.YUV444P10:  ('i444',     'raw',                       10),
             vs.YUV444P16:  ('i444',     'raw',                       16)}
    return table.get(format)


def x264enc(core, clip, opts, tcfile_in=False, bin=None):
    if bin is None:
        bin = x264_binary_path

    csp = get_x264_csp(clip.format.id)
    if not csp:
        print('input format is unsupported.', file=sys.stderr)
        return

    cmdline = ('--frames {num} --input-csp {csp} --demuxer {demux} '
               '--input-depth {depth} --input-res {width}x{height})
    cmdline = cmdline.format(num=clip.num_frames, csp=csp[0],
                             demux=csp[1], depth=csp[2],
                             width=clip.width, height=clip.height)

    if tcfile_in == False:
        fps = ' --fps {num}/{den}'.format(num=clip.fps_num,
                                          den=clip.fps_den)
        cmdline += fps

    cmdline = '%s - %s %s' % (bin, cmdline, opts)
    enc_video(core, clip, cmdline)
    sys.stderr.flush()


def get_av_pix_fmt(format):
    table = {vs.COMPATBGR32:'bgra',        vs.COMPATYUY2:'yuyv422',
             vs.GRAY8:      'gray',        vs.GRAY16:    'gray16',
             vs.RGB24:      'gbrp',        vs.RGB27:     'gbrp9le',
             vs.RGB30:      'gbrp10le',    vs.RGB48:     'gbrp16le',
             vs.YUV410P8:   'yuv410p',     vs.YUV411P8:  'yuv411p',
             vs.YUV420P8:   'yuv420p',     vs.YUV420P9:  'Yuv420p9le',
             vs.YUV420P10:  'yuv420p10le', vs.YUV420P16: 'yuv420p16le',
             vs.YUV422P8:   'yuv422p',     vs.YUV422P9:  'yuv422p9le',
             vs.YUV422P10:  'yuv422p10le', vs.YUV422P16: 'yuv422p16le',
             vs.YUV444P8:   'yuv444p',     vs.YUV444P9:  'yuv444p9le',
             vs.YUV444P10:  'yuv444p10le', vs.YUV444P16: 'yuv444p16le'}
    return table.get(format)


def avenc(core, clip, opts, bin=None):
    if bin is None:
        bin = avconv_binary_path

    cmdline = ('{bin} -f rawvideo -pix_fmt {fmt} -s {width}x{height} '
               '-r {rnum}/{rden} -vframes {fnum} -i - {opts}')
    cmdline = cmdline.format(bin=bin, fmt=get_av_pix_fmt(clip.format.id),
                             width=clip.width, height=clip.height,
                             rnum=clip.fps_num, rden=clip.fps_den,
                             fnum=clip.num_frames, opts=opts)
    enc_video(core, clip, cmdline)


class Enc(object):
    def __init__(self, core):
        self.core = core

    def x264enc(self, clip, opts, tcfile_in=False, bin=''):
        return x264enc(self.core, clip, opts, tcfile_in, bin)

    def avenc(self, clip, opts, bin=''):
        return avenc(self.core, clip, opts, bin)
