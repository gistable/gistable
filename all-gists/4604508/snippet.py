#!/usr/bin/python

import argparse
import sys
import math
import operator
import itertools
import Image, ImageDraw

# http://stackoverflow.com/questions/14423794/equivalent-of-haskell-scanl-in-python
def scanl(f, base, l):
    yield base
    for x in l:
        base = f(base, x)
        yield base


# scanl'
def scanl_(f, l):
    return scanl(f, l[0], itertools.islice(l, 1, None))


def draw_chart(data,
               width=2400, height=60,
               minWidth=1, isLogarithmicWidth=False,
               lastfill=(0, 0, 0),
               split=1,
               vspan=None,
               tics=0,
               color_tics="#000000",
               print_label=False):
    if vspan is None: vspan = height
    conv = (lambda x: int(math.log(x))) if isLogarithmicWidth else lambda x: x
    size = [i[1] for i in data]
    ssum = list(scanl(operator.add, 0, size))
    tics_size = [ssum[-1]*i/(1+tics) for i in range(1, 1+tics)]
    conved_size = [conv(i) for i in size]
    total_size = sum(conved_size)
    total_count = len(data)
    assert total_count * minWidth <= width
    width_list = [(minWidth
                   + round((width - total_count * minWidth)
                           * i * 1.0 / total_size)) for i in conved_size]
    actual_width = sum(width_list)
    pos_list = scanl(operator.add, 0, width_list)
    color_list = (i[2] for i in data)

    image = Image.new("RGB", (width, height), (0xff, 0xff, 0xff))
    draw = ImageDraw.Draw(image)
    cur_tic = 0
    for i, (p, w, c) in enumerate(itertools.izip(pos_list, width_list, color_list)):
        draw.rectangle(((p, 0), (p+w, height)), fill=c)
        label_pos = "0x%08X" % data[i][0]
        label_len = "0x%08X" % data[i][1]
        rect_pos = draw.textsize(label_pos)
        rect_len = draw.textsize(label_len)
        if (print_label
            and max(rect_pos[0], rect_len[0]) <= w
            and rect_pos[1] + rect_len[1] <= vspan):
            # match size
            draw.text((p, 0), label_pos, fill=(0, 0, 0))
            draw.text((p, rect_pos[1]), label_len, fill=(0, 0, 0))
        while cur_tic < tics and ssum[i] <= tics_size[cur_tic] < ssum[i+1]:
            p2 = p + (tics_size[cur_tic] - ssum[i]) * w / size[i]
            draw.rectangle((p2-1, height/2-1, p2+1, height/2+1),
                           fill=color_tics)
            cur_tic += 1
    draw.rectangle(((actual_width, 0), (width, height)), fill=lastfill)

    if split == 1: return image
    assert width / split * split == width
    image_ = Image.new("RGB", (width/split, vspan*split), lastfill)
    for i in xrange(split):
        image_.paste(image.crop((i*width/split, 0, (i+1)*width/split, height)),
                     (0, i*vspan, width/split, i*vspan+height))
    return image_


COLOR_NON_TRIED   = (0x99, 0x99, 0x99)
COLOR_NON_TRIMMED = (0x33, 0xff, 0x00)
COLOR_NON_SPLIT   = (0xff, 0x99, 0x00)
COLOR_BAD_SECTOR  = (0x99, 0x00, 0x00)
COLOR_FINISHED    = (0x00, 0x66, 0xff)


MONOCHROME_NON_TRIED   = (0xbb, 0xbb, 0xbb)
MONOCHROME_NON_TRIMMED = (0x99, 0x99, 0x99)
MONOCHROME_NON_SPLIT   = (0x66, 0x66, 0x66)
MONOCHROME_BAD_SECTOR  = (0x33, 0x33, 0x33)
MONOCHROME_FINISHED    = (0xee, 0xee, 0xee)


def s2color_c(c):
    if False: pass
    elif c == '?': return COLOR_NON_TRIED
    elif c == '*': return COLOR_NON_TRIMMED
    elif c == '/': return COLOR_NON_SPLIT
    elif c == '-': return COLOR_BAD_SECTOR
    elif c == '+': return COLOR_FINISHED
    else:
        raise ValueError("unexpected state character" ++ c)


def s2color_m(c):
    if False: pass
    elif c == '?': return MONOCHROME_NON_TRIED
    elif c == '*': return MONOCHROME_NON_TRIMMED
    elif c == '/': return MONOCHROME_NON_SPLIT
    elif c == '-': return MONOCHROME_BAD_SECTOR
    elif c == '+': return MONOCHROME_FINISHED
    else:
        raise ValueError("unexpected state character" ++ c)


def s2color(c, isMonochrome):
    return s2color_m(c) if isMonochrome else s2color_c(c)


def main():
    parser = argparse.ArgumentParser(description="Draw GNU ddrescue chart.")
    parser.add_argument("-m", "--monochrome",
                        action='store_true',
                        help="Make output image monochrome.")
    parser.add_argument("-l", "--logarithmic-width",
                        action='store_true',
                        help="Use logarithmic width instead of linear scale.")
    parser.add_argument("-w", "--width",
                        type=int, default=2400,
                        help="Total width of bar, not actual width of output.")
    parser.add_argument("-t", "--height",
                        type=int, default=40,
                        help="height of bar, not actual height of output.")
    parser.add_argument("-s", "--split",
                        type=int, default=1,
                        help="How many rows in the output image.")
    parser.add_argument("-p", "--vspan",
                        type=int, default=50,
                        help="vertical span of bar.")
    parser.add_argument("--tics",
                        type=int, default=0,
                        help="the number of tics in the bar.")
    parser.add_argument("--print-label",
                        action='store_true',
                        help="print labels on cells.")
    parser.add_argument("source",
                        help="GNU ddrescue logfile.")
    parser.add_argument("destination",
                        help="Output image file.")
    args = parser.parse_args()
    FILE = args.source
    DEST = args.destination
    state = []
    cursor = ()
    with open(FILE, "r") as f:
        for l in f:
            if l[0] == '#': continue
            ltuple = l.strip().split()
            if len(ltuple) == 2:
                cursor = l
            elif len(ltuple) == 3:
                x, y, z = ltuple
                state.append((int(x, 16), int(y, 16), s2color(z, args.monochrome)))
            else:
                print >>sys.stderr, "Unexpected format."
                exit()
    lf = (0xff, 0xff, 0xff) if args.monochrome else (0, 0, 0)
    im = draw_chart(state,
                    isLogarithmicWidth=args.logarithmic_width,
                    minWidth=(0 if args.logarithmic_width else 1),
                    lastfill=lf,
                    width=args.width, height=args.height,
                    split=args.split, vspan=args.vspan,
                    tics=args.tics,
                    print_label=args.print_label)
    if args.monochrome:
        im.convert("L")
    im.save(DEST)


if __name__ == "__main__":
    main()
