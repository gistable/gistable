# Inspired by http://rarlindseysmash.com/posts/stupid-programmer-tricks-and-star-wars-gifs
#         via https://news.ycombinator.com/item?id=6633490
# Requires
# * a reasonably recent ffmpeg suite
# * Graphicsmagick or ImageMagick
# * optionally: Gifsicle
# * an input video file
# Usage:
#   python gifgif.py a_video_file.avi

from subprocess import Popen, PIPE
import json
import tempfile
import random
import glob
import os
import sys


def run(cmd):
    return Popen([str(c) for c in cmd], stdout=PIPE, stderr=PIPE).communicate()[0]

try:
    convert_command = ["gm", "convert"]
    run(convert_command)
except:
    convert_command = ["convert"]
    try:
        run(convert_command)
    except:
        raise ValueError("Unable to find 'convert' or 'gm convert'")


def get_duration(input_file):
    data = json.loads(run(["ffprobe", "-loglevel", "quiet", "-of", "json", "-show_streams", "-i", input_file]))
    return float(data["streams"][0]["duration"])


def get_frames(input_file, start, duration, fps=10):
    temp_dir = tempfile.mkdtemp(prefix="gif")
    run(["ffmpeg", "-loglevel", "quiet", "-i", input_file, "-ss", start, "-t", duration, "-r", fps, "-f", "image2", os.path.join(temp_dir, "%08d.png")])
    return glob.glob(os.path.join(temp_dir, "*.png"))


def make_gif(output_file, frames, fps):
    run(convert_command + ["-delay", "1x%d" % fps] + frames + ["-coalesce", output_file])
    try:
        run(["gifsicle", "-O2", "--colors", 256, "--batch", "-i", output_file])
    except:
        pass


def create_gif(input_file):
    output_file = "random-%d.gif" % random.randint(0, 150)
    total_duration = get_duration(input_file)
    start = random.uniform(0.2, 0.8) * total_duration
    frames = get_frames(input_file, start, 3, 8)
    make_gif(output_file, frames, 24)
    for frame in frames:
        os.unlink(frame)
    print output_file

if __name__ == '__main__':
    create_gif(sys.argv[1])
