#!/usr/bin/env python3

"""
I’ve stopped updating this a while ago because some people made a proper respository with a few necessary fixes and changes.
Just get this version from now on: https://github.com/Infiziert90/getnative
"""

import os
import re
import time
import argparse
import vapoursynth as vs
import matplotlib.pyplot as plot

# Author: kageru
# Performance optimizations and other changes: Frechdachs
# Prerequisites:
# matplotlib http://matplotlib.org/users/installing.html
# fmtc: https://github.com/EleonoreMizo/fmtconv/releases
# Depending on source filter:
# ffms2: https://github.com/FFMS/ffms2/releases
# or L-Smash: http://forum.doom9.org/showthread.php?t=167435

# and imwri(f) for png/bmp input: 64bit: https://ddl.kageru.moe/kjP6s.7z
# if you need 32bit: http://forum.doom9.org/showthread.php?p=1769737#post1769737

# This script's success rate is far from perfect.
# If possible, do multiple tests on different frames from the same source.
# Bright scenes generally yield the most accurate results.
# Graphs tend to have multiple notches, so the script's assumed resolution may be incorrect.
# Also, due to the current implementation of the autoguess, it is not possible for the script to automatically recognize 1080p productions.
# Use your eyes or anibin if necessary.

# general settings
# target directory (home directory will be prepended, e.g. C:/Users/kageru + targetdir)
targetdir = os.path.join('Desktop', 'getnative')
# format of the output image. can be svg, png, pdf, rgba, jp(e)g, tif(f), and probably more
imageFormat = 'svg'
# scaling of the y axis. can be 'linear' or 'log'
plotScaling = 'log'

parser = argparse.ArgumentParser(description='Find the native resolution(s) of upscaled material (mostly anime)')
parser.add_argument('--input', '-i', dest='input_file', type=str, help='string. Absolute or relative path to the input file')
parser.add_argument('--frame', '-f', dest='frame', type=int, default=None,
                    help='int. Specify a frame for the analysis. Random if unspecified')
parser.add_argument('--kernel', '-k', dest='kernel', type=str, default='bilinear', help='string. Resize kernel to be used')
parser.add_argument('--generate-images', '-out', dest='image_output', type=bool, default=True,
                    help='save detail mask as png')
parser.add_argument('--min-height', '-min', dest='min_height', type=int, default=600, help='int. Minimum height to consider')
parser.add_argument('--max-height', '-max', dest='max_height', type=int, default=1000,
                    help='int. Maximum height to consider')
parser.add_argument('--bicubic-b', '-b', dest='b', type=float, default=1 / 3, help='float. b parameter of bicubic resize')
parser.add_argument('--bicubic-c', '-c', dest='c', type=float, default=1 / 3, help='float. c parameter of bicubic resize')
# TODO implement this
parser.add_argument('--number-of-resolutions', '-r', dest='num_resolutions', type=str, default=None,
                    help='Force a number of different resolutions to be considered in the analysis. This is useful for anime with different resolutions in one frame if the autodetection fails')
parser.add_argument('--input-is-image', '-img', dest='input_is_image', type=bool, default=None,
                    help='bool. Force image input. This is automatically detected for png, bmp, and jpg input')
parser.add_argument('--aspect-ratio', '-a', dest='ar', type=float, default=None,
                    help='float. Force aspect ratio. Only useful for anamorphic input')
parser.add_argument('--use-lsmash', '-lsmash', dest='use_lsmash', type=bool, default=True,
                    help='bool. Use lsmash for input. If false, ffms2 will be used')
args = parser.parse_args()
inputFile = args.input_file
frame = args.frame
kernel = args.kernel
image_output = args.image_output
minHeight = args.min_height
maxHeight = args.max_height
b = args.b
c = args.c
num_resolutions = args.num_resolutions
input_is_image = args.input_is_image
ar = args.ar
use_lsmash = args.use_lsmash


core = vs.get_core()
if not (hasattr(core, 'fmtc') and hasattr(core, 'lsmas') or hasattr(core, 'ffms2') and hasattr(core, 'imwri') or hasattr(core, 'imwrif')):
    raise AttributeError('One or more dependencies could not be found.')
imwri = 'imwri' if hasattr(core, 'imwri') else 'imwrif'
if input_is_image is None:
    if bool(re.match('.*\.(png|jpg|bmp)$', inputFile)):
        input_is_image = True
    else:
        input_is_image = False

if input_is_image:
    src = eval('core.{:s}.Read(r"{:s}")'.format(imwri, inputFile))
    frame = 0
elif use_lsmash:
    src = core.lsmas.LWLibavSource(inputFile)
    src = core.std.ShufflePlanes(src, 0, vs.GRAY)
else:
    src = core.ffms2.Source(inputFile)
    src = core.std.ShufflePlanes(src, 0, vs.GRAY)
src_16 = core.fmtc.bitdepth(src, bits=16)
if frame is None:
    frame = src.num_frames // 3
if ar is None:
    ar = src.width / src.height
txtOutput = ''
resolutions = []
starttime = time.time()


def getw(h, only_even=True):
    w = h * ar
    w = int(round(w))
    if only_even:
        w = w // 2 * 2
    return w


def scalemask(clip, w, h):
    down = core.fmtc.resample(clip, w, h, kernel=kernel, a1=b, a2=c, invks=True)
    up = core.fmtc.resample(down, getw(src.height), src.height, kernel=kernel, a1=b, a2=c)
    smask = core.std.Expr([clip, up], 'x y - abs')
    smask = core.std.Expr(smask, 'x 1000 < 0 x ?')
    smask = core.std.CropRel(smask, 5, 5, 5, 5)
    return smask


def geterror(w, h):
    mask = scalemask(src_16[frame], w, h)
    mask = core.std.PlaneStats(mask)
    luma = mask.get_frame(0).props.PlaneStatsAverage
    return luma


def getnative():
    global txtOutput

    def get_filename():
        if kernel == 'bicubic':
            bic = '_b{:.2f}_c{:.2f}'.format(b, c)
        else:
            bic = ''
        fn = u'{:d}_{:s}{:s}_({:d}-{:d})'.format(frame, kernel, bic, minHeight, maxHeight)
        return fn

    def prepareSaveDirectory():
        home = os.path.expanduser('~')
        savedir = os.path.join(home, targetdir)
        if not os.path.exists(savedir):
            os.makedirs(savedir)
        return home

    def analyzeResults():
        global txtOutput
        global resolutions

        last = 0
        for i in range(1, len(vals)):
            last = vals[i - 1]
            current = vals[i]
            if current == 0:
                ratio = 0
            else:
                ratio = last / current
            ratios.append(ratio)

        sorted = ratios[:]  # make a copy of the array. we need the unsorted array later
        sorted.sort()
        i = 2
        max_difference = sorted[len(sorted) - 1]
        differences = [max_difference]
        while i < 6:
            if sorted[len(sorted) - i] - 1 > (max_difference - 1) * 0.33:
                differences.append(sorted[len(sorted) - i])
                i += 1
            else:
                break
        #differences = differences[::-1]
        for diff in differences:
            current = ratios.index(diff)
            accept = True
            # don't allow results within 20px of each other
            for res in resolutions:
                if bool(list(set(range(res - 20, res + 20)) & set([current]))):
                    accept = False
            if accept:
                resolutions.append(current)

        if kernel == 'bicubic':
            bicubic_params = 'Scaling parameters:\nb = {:.2f}\nc = {:.2f}\n'.format(b, c)
        else:
            bicubic_params = ''
        txtOutput += u'Resize Kernel: {:s}\n{:s}Native resolution(s) (best guess): {:s}\nPlease check the graph manually for more accurate results\n\n'.format(
            kernel, bicubic_params, 'p, '.join([str(r + minHeight) for r in resolutions]) + 'p')

    def savetxt():
        global txtOutput
        text_file = open(path + '.txt', 'w')
        txtOutput += '\nProcessing Time: ' + str(time.time() - starttime)
        text_file.write(txtOutput)
        text_file.close()

    def save_plot():
        plot.style.use('dark_background')
        plot.plot(range(minHeight, maxHeight + 1), vals, '.w-')
        plot.title(filename)
        plot.ylabel('Relative error')
        plot.xlabel('Resolution')
        plot.yscale(plotScaling)
        plot.savefig(path + '.' + imageFormat)

    def save_images(res, path):
        src = src_16[frame]
        core = vs.get_core()
        temp = eval("core.{:s}.Write(src[0].fmtc.bitdepth(bits=8), 'png', path + '_source{:s}d.png')".format(imwri, '%'))   # using %% inside the string does not work
        _ = temp.get_frame(0)  # trick vapoursynth into rendering the frame
        for r in res:
            r += minHeight
            image = mask_detail(src, getw(r), r)
            # TODO: use PIL for output
            t = eval("core.{:s}.Write(image.fmtc.bitdepth(bits=8), 'png', path + '_mask_{:d}p{:s}d.png')".format(imwri, r, '%'))
            _ = t.get_frame(0)
            t = eval("core.{:s}.Write(src.fmtc.resample(getw(r), r, kernel=kernel, a1=b, a2=c, invks=True).fmtc.bitdepth(bits=8), 'png', path + '_{:d}p{:s}d.png')".format(imwri, r, '%'))
            _ = t.get_frame(0)
            print('Writing ' + path + '_{:d}p.png'.format(r))

    # Original idea by MonoS @github: https://github.com/MonoS/VS-MaskDetail
    def mask_detail(clip, final_width, final_height, kernel='bilinear', a1=1/3, a2=1/3):
        depth = clip.format.bits_per_sample
        core = vs.get_core()
        startclip = core.fmtc.bitdepth(clip, bits=16)
        original = (startclip.width, startclip.height)
        target = (final_width, final_height)
        temp = core.fmtc.resample(startclip, *target[:2], kernel=kernel, invks=True, invkstaps=4, taps=4, a1=a1, a2=a2)
        temp = core.fmtc.resample(temp, *original, kernel=kernel, taps=4, a1=a1, a2=a2)
        mask = core.std.Expr([startclip, temp], 'x y - abs 1024 < 0 x y - abs 16 * ?').std.Inflate()
        mask = core.fmtc.resample(mask, *target, taps=4)
        return core.fmtc.bitdepth(mask, bits=8, dmode=1)

    home = prepareSaveDirectory()

    filename = get_filename()
    path = os.path.join(home, targetdir, filename)
    analyzeResults()
    save_plot()
    if image_output:
        save_images(resolutions, path)
    txtOutput += 'Raw data:\n'
    txtOutput += 'Resolution\t | Relative Error\t | Relative difference from last\n'
    last = 0
    for i, error in enumerate(vals):
        txtOutput += '{:4d}\t\t | {:.6f}\t\t\t | {:.2f}\n'.format(i + minHeight, error, ratios[i])
        last = error
    savetxt()


if __name__ == '__main__':
    vals = []
    ratios = [0]
    for h in range(minHeight, maxHeight + 1):
        w = getw(h)
        print('Processing resolution: {} x {}'.format(w, h))
        vals.append(geterror(w, h))
    getnative()
    print('done in {:.2f} s'.format(time.time() - starttime))
