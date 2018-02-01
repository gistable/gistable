#!/usr/bin/env python3
"""
screenpy.py - a CLI wrapper around OSX's screencapture for easy screenshotting. I use it all the time for blogging
              technical tutorials that require a lot of screenshots:
              http://2015.padjo.org/tutorials/mapping/077-ok-schools-quakes/

Dependencies: Python 3.x, boto (for AWS S3 uploading), and PIL

Standard usage:

   $ screenpy /tmp/myimage.jpg

   Gives you 2 seconds to switch back to your desktop/application before `screencapture` is executed in interactive mode,
   allowing you to select/size a window for screenshotting. The resulting file is saved in the path, /tmp/myimage.jpg.

   The following is output to STDERR:

       Writing to: hello.jpg
        Format: jpeg
        optimize: True
        quality: 75
      ![image hello.jpg](/tmp/myimage.jpg)

  The following is output to STDOUT for easy copy-pasting:

      <img src="/tmp/myimage.jpg" alt="hello.jpg">

Integration with S3: If you aren't using a static site generator, sometimes you want a remote URL. Adjust the `S3`
global variables to your liking (e.g. S3_BUCKET and S3_DOMAIN), and then call screenpy as so:

      $ screenpy --s3 myonlinepicture.png
"""

S3_BUCKET = 'cdan.danwin.com'
S3_DOMAIN = 'http://cdan.danwin.com.s3-website-us-east-1.amazonaws.com/'
S3_DEFAULT_SUBFOLDER = 'screenpy-caps'

import argparse
import boto3

from datetime import datetime
from os import makedirs, unlink
from os.path import basename, dirname, expanduser, getsize, join, relpath, splitext
from PIL import Image
from subprocess import call
from tempfile import NamedTemporaryFile
from time import sleep
from sys import stderr, stdout
# http://stackoverflow.com/questions/89228/calling-an-external-command-in-python
APPROVED_FORMAT_ALIASES = ['jpg', 'jpeg', 'gif', 'png']
GIF_FORMAT = 'gif'
JPEG_FORMAT = 'jpeg'
PNG_FORMAT = 'png'
JPG_QUALITY_MAX = 95
JPG_QUALITY_DEFAULT = 75
PNG_COMPRESS_LEVEL_MAX = 9
PNG_COMPRESS_LEVEL_MIN = 0
PNG_COMPRESS_LEVEL_DEFAULT = 3

## DEFINE PARSER
parser = argparse.ArgumentParser()
parser.add_argument("output_path", nargs = 1, help = "Path to save file to")


parser.add_argument('--alt-text', '-a',
    type=str,
    help ="alt text for image" )

parser.add_argument('--best', '-b',
    action = "store_true",
    help ="Do not do any optimization or compression" )

parser.add_argument('--format', '-f',
    help ='Specify a format, such as jpg, png, gif' )

parser.add_argument('--pause', '-p',
    default = 2,
    help ='Number of seconds to wait before taking the screenshot')

parser.add_argument('--quality', '-q',
    help ='Set a quality level from 0 to 100' )

parser.add_argument('--s3', '-s', help='Send to S3', action="store_true")


################ HELPER FUNCTIONS
def get_canonical_format_name(ofmt):
    o = ofmt.lower().strip()
    # "jpg" must be "JPEG"
    if o == "jpg" or o == 'jpeg':
        return JPEG_FORMAT
    elif o == 'gif':
        return GIF_FORMAT
    elif o == 'png':
        return PNG_FORMAT
    else:
        oopsmsg = "Image output format or file extension was: %s\n It must be: %s" % (ofmt, ', '.join(APPROVED_FORMAT_ALIASES))
        raise Exception(oopsmsg)



def generate_s3_keyname(destname):
    """ simply returns join with default s3 subfolder and destname """
    return join(S3_DEFAULT_SUBFOLDER, destname)

def generate_s3_url(destname):
    return join(S3_DOMAIN, generate_s3_keyname(destname))


def save_image(srcname, destname, output_format, **kwargs):
    img = Image.open(tname).convert('RGBA')
    img.info['screenshot-timestamp'] = datetime.now().isoformat()
    img.save(destname, output_format, **kwargs)
    return destname


def tempscreencap(format='png'):
    """Screencapture to a temporary filename with a given file extension
    Returns: String, temporary filename, if screenshot taken
    """
    ## create a temp filename
    tfile = NamedTemporaryFile(suffix='.' + format, delete=False)
    tpath = tfile.name
    # yield to user control and take the screenshot
    call(["screencapture", "-i", "-o", "-s", tpath])
    if getsize(tpath) == 0:
        raise RuntimeError("No screenshot was taken.")
    else:
        return tpath


def to_s3(srcname, destname, fileext=None):
    """
    MIME header based on destname extension by default, e.g.
      'image/png' for 'example.png'

    Returns the S3 URL for easy reference
    """
    fileext = fileext or splitext(destname)[1][1:]
    s3 = boto3.resource('s3')
    bucket = s3.Bucket(S3_BUCKET)
    key = bucket.Object(generate_s3_keyname(destname))
    with open(srcname, 'rb') as data:
        key.upload_fileobj(data, {'ACL': 'public-read',
                                  'ContentType': 'image/%s' % fileext})
    return generate_s3_url(destname)



if __name__ == '__main__':
    #######################
    # BEGIN ARGUMENT PARSING

    ### CLI
    args = parser.parse_args()
    abs_output_path = expanduser(args.output_path[0])
    output_path = relpath(abs_output_path)
    alt_text = args.alt_text or basename(output_path)
    pause_sec = int(args.pause)

    ## determine optimization level
    if args.best:
        do_optimization_pass = False
        qlevel = None

    else:
        do_optimization_pass = True
        qlevel =  str(args.quality).lower() if args.quality else None

    ## choose a format; either it's explicitly set via --format
    if args.format:
        _ofmt = args.format.lower()
    else:  # or it is implicit in output_path's extension
        _ofmt = splitext(output_path)[1].split('.')[-1].lower()
        # by default, make it a PNG if there is no extension
        _ofmt = _ofmt if _ofmt else 'png'

    output_format = get_canonical_format_name(_ofmt)



    # Save the file depending on output_format
    ##############
    # if output_format is jpg
    # http://pillow.readthedocs.org/en/latest/handbook/image-file-formats.html#jpg
    output_params = {}
    if output_format == JPEG_FORMAT:
        if do_optimization_pass:
            if qlevel == 'max':
                qlevel = JPG_QUALITY_MAX
            else:
                qlevel = int(qlevel) if qlevel else JPG_QUALITY_DEFAULT
        else:
            qlevel = JPG_QUALITY_MAX

        output_params.update({'optimize':do_optimization_pass, 'quality': qlevel})
    ##############
    # if format is png
    #
    # http://pillow.readthedocs.org/en/latest/handbook/image-file-formats.html#png
    # in the case of PNG files
    #  (optimize = True) overrides compress_level
    #    i.e. it will cause Image#save to automatically set
    #    compress_level to MAX_PNG_COMPRESS_LEVEL
    #    so instead, we set compress_level to the default and set optimize to False
    #    since we don't want that optimize parameter to override compress_level
    #
    #  if user specifies --best-quality, then compress_level is set to MIN_PNG_COMPRESS_LEVEL
    #    and optimize is set to False
    elif output_format == PNG_FORMAT:
        if do_optimization_pass:
            if qlevel == 'max':
                qlevel = PNG_COMPRESS_LEVEL_MAX
            else:
                if qlevel:
                    qlevel = round((int(qlevel) / 100) * PNG_COMPRESS_LEVEL_MAX)
                else:
                    qlevel = PNG_COMPRESS_LEVEL_DEFAULT
        else:
            qlevel = PNG_COMPRESS_LEVEL_MIN

        output_params.update({'optimize': False, 'compress_level': qlevel})
    # if format is GIF
    # there are no special parameters for GIF
    elif output_format == GIF_FORMAT:
        pass
    else:
        pass # meh why not

    ## Make the parent directories for the output_path
    ## TODO: MAke it not crash with relative dir
    abs_dir = dirname(abs_output_path)
    if abs_dir:
        makedirs(abs_dir, exist_ok = True)

    ## Might as well output information before we go to sleep...
    stderr.write("\nWriting to: %s" % output_path)
    stderr.write("\n\tFormat: %s" % output_format)
    for key, val in output_params.items():
        stderr.write("\n\t%s: %s" % (key, val))
    stderr.write('\n')

    HTML_TEMPLATE = """<img src="{src}" alt="{alt}">"""
    MD_TEMPLATE = """![image {alt}]({src})"""


    if(args.s3):
        output_src_url = generate_s3_url(output_path)
    else:
        output_src_url = output_path

    # We want to print markup and markdown to screen as quickly as possible
    stderr.write(MD_TEMPLATE.format(src=output_src_url, alt=basename(output_path)))
    stderr.write("\n")


    # Output HTMl to stdout, for pipeable reasons
    print(HTML_TEMPLATE.format(src=output_src_url, alt=basename(output_path)))


    ### Begin file-writing process
    ## Sleep
    sleep(pause_sec)

    ### Start the screencapture process
    tname = tempscreencap(output_format)


    if(args.s3):
        _s3url = to_s3(srcname=tname, destname=output_path)
        stderr.write("\n-----\nUploaded: \n%s\n\n" % _s3url)
    else:
        # reopen the saved screenshot file
        save_image(tname, abs_output_path, output_format, **output_params)

    # remove the temp screen grab file from memory
    unlink(tname)



