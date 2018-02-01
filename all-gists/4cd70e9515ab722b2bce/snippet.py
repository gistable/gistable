import random
import subprocess
from collections import namedtuple
from datetime import timedelta
from math import sqrt
import argparse
from os.path import join, exists
from os import getcwd, mkdir
from ffprobe import FFProbe
from pytube import YouTube
from PIL import Image, ImageDraw
from glob import glob
from os import unlink

try:
    import Image
except ImportError:
    from PIL import Image

Point = namedtuple('Point', ('coords', 'n', 'ct'))
Cluster = namedtuple('Cluster', ('points', 'center', 'n'))

def get_points(img):
    points = []
    w, h = img.size
    for count, color in img.getcolors(w * h):
        points.append(Point(color, 3, count))
    return points

rtoh = lambda rgb: '#%s' % ''.join(('%02x' % p for p in rgb))


def colorz(filename, n=3):
    img = Image.open(filename)
    img.thumbnail((100, 100))
    w, h = img.size
    points = get_points(img)
    clusters = kmeans(points, n, 1)
    rgbs = [map(int, c.center.coords) for c in clusters]
    return map(rtoh, rgbs)


def euclidean(p1, p2):
    return sqrt(sum([
        (p1.coords[i] - p2.coords[i]) ** 2 for i in range(p1.n)
    ]))


def calculate_center(points, n):
    vals = [0.0 for i in range(n)]
    plen = 0
    for p in points:
        plen += p.ct
        for i in range(n):
            vals[i] += (p.coords[i] * p.ct)
    return Point([(v / plen) for v in vals], n, 1)


def kmeans(points, k, min_diff):
    clusters = [Cluster([p], p, p.n) for p in random.sample(points, k)]

    while 1:

        plists = [[] for i in range(k)]

        for p in points:
            smallest_distance = float('Inf')
            for i in range(k):
                distance = euclidean(p, clusters[i].center)
                if distance < smallest_distance:
                    smallest_distance = distance
                    idx = i
            plists[idx].append(p)

        diff = 0
        for i in range(k):
            old = clusters[i]
            center = calculate_center(plists[i], old.n)
            new = Cluster(plists[i], center, old.n)
            clusters[i] = new
            diff = max(diff, euclidean(old.center, new.center))

        if diff < min_diff:
            break

    return clusters


def download_video(video_url, output):
    youtube = YouTube(video_url)
    video = youtube.filter('mp4')[0]
    return video.download(output)


def get_duration(video_path):
    metadata = FFProbe(video_path)
    for stream in metadata.streams:
        if stream.isVideo():
            return timedelta(seconds=float(stream.duration))


def extract_frames(video_path, output_path, num_of_frames, ffmpeg_path=None):
    print 'Extracting frames...'
    duration = get_duration(video_path)
    rval = 1 / (duration / num_of_frames).total_seconds()
    ffmpeg = ffmpeg_path or '/usr/local/bin/ffmpeg'
    command = '%(ffmpeg)s -i \'%(video)s\' -r %(rval)s -f image2 %(output)s'
    cmd_args = {'ffmpeg': ffmpeg, 'video': video_path, 'rval': rval,
                'output': output_path}
    command = command % cmd_args
    command = command + '/frame_%05d.jpg'

    response = subprocess.call(
        command, shell=True, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)

    if response != 0:
        return False

    return True

def timedelta_as_str(td):
    s = td.total_seconds()
    hours, remainder = divmod(s, 3600)
    minutes, seconds = divmod(remainder, 60)
    return '%02d:%02d:%02d' % (hours, minutes, seconds)


num_of_colors_per_frame = 1

def poster_renderer(colors, workbench, output_filename='palette-poster.html'):
    '''
    colors = [[color1, color2, color3], [color1, color2, color3]]
    '''
    TEMPLATE = '''
    <!doctype html>
    <html class="no-js" lang="">
      <head>
        <meta charset="utf-8">
        <meta http-equiv="x-ua-compatible" content="ie=edge">
        <title></title>
        <meta name="description" content="">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <link rel="apple-touch-icon" href="apple-touch-icon.png">
        <style>
        body   { padding: 50px; width: 700px; margin: 0 auto; background: white; }
        table  { width: 100%%; border-spacing: 0 }
        td     { height: %spx }
        h1, h2 { margin: 30px 0 10px 0; text-align: center; }
        h1     { font-size: 60px; }
        h2     { font-size: 22px; }
        </style>

      </head>
      <body>%s</body>
    </html>
    '''
    table = '<table>'
    for idx in range(len(colors)):
        print 'Frame: %s/%s' %(idx, args.nof)
        table += '<tr>'
        color_row = colors[idx]
        for color in color_row:
            table += '<td style="background: %s;"></td>' % color
        table += '</tr>\n'
    table += '</table>'

    if args.title:
        table += '<h1>%s</h1>' % args.title

    if args.subtitle:
        table += '<h2>%s</h2>' % args.subtitle

    output = TEMPLATE % (args.rh, table)

    with open(join(workbench, output_filename), 'w') as fp:
        fp.write(output)


def image_renderer(colors, workbench, rh=1, output_filename='pallette.png'):
    im = Image.new("RGB", (500, len(colors) * rh))
    draw = ImageDraw.Draw(im)
    for idx in xrange(len(colors)):
        box = [0, idx * rh, 500, (idx * rh) + (rh - 1)]
        draw.rectangle(box, colors[idx][0])
    im.save(join(workbench, output_filename))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Convert Youtube video to a color chart.')


    parser.add_argument(
        'video_url', type=str, nargs='?',
         help='URL of Youtube video that will be converted')

    parser.add_argument(
        'workbench_name', type=str, nargs='?',
        help='A foldername that will be created to download '
             'video and extract frames.')

    parser.add_argument('--number-of-frames', dest='nof', action='store', 
                        help='Number of frames that will be extracted from video.',
                        default=800, type=int)

    parser.add_argument('--colors-per-frame', dest='cpf', action='store', 
                        help='Number of colors that will be extracted from every frame.',
                        default=1, type=int)

    parser.add_argument('--row-height', dest='rh', action='store',
                        help='Color row height.', default=1, type=int)

    parser.add_argument('--title', dest='title', action='store', nargs='?',
                        help='Title for video.', type=str)

    parser.add_argument('--subtitle', dest='subtitle', action='store', nargs='?',
                        help='Subtitle for video.', type=str)

    args = parser.parse_args()

    print args.workbench_name

    video_url = args.video_url
    workbench = join(getcwd(), args.workbench_name)

    if not exists(workbench):
        mkdir(workbench)

    video_path = join(workbench, 'video.mp4')

    if not exists(video_path):
        print 'Downloading video...'
        download_video(video_url, video_path)

    frame_paths = glob(join(workbench, 'frame_*.jpg'))

    if len(frame_paths) < args.nof:
        extract_frames(video_path, workbench, args.nof)

    frame_paths = glob(join(workbench, 'frame_*.jpg'))

    colors = []
    for idx in range(args.nof):
        print 'Extracting colors from frame: %s' % idx
        frame_path = frame_paths[idx]
        colors.append(colorz(frame_path, n=args.cpf))

    poster_renderer(colors, workbench)
    image_renderer(colors, workbench)

    for frame_path in frame_paths:
        unlink(frame_path)
