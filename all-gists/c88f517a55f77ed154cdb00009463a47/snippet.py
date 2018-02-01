# Python 2.7

import os
import sys
import time
import platform
import subprocess
import urllib2
import logging

""" Are we windows or linux """
is_windows = any(platform.win32_ver())

""" Edit the following values to your liking, pay special attention to the media_path, plex_url and plex_token values """

# Paths to ffmpeg, handbrake-cli and your log file
# If you need help finding your install points in Linux, try 'which ffmpeg' and 'which handbrake'
# Make sure you install the following on your platform, ffmpeg, handbrake AND handbrake-cli
ffmpeg_cli = '/usr/bin/ffmpeg' # 'C:\ffmpeg\bin\ffmpeg.exe'
handbrake_cli = '/usr/bin/HandBrakeCLI' # 'C:\Program Files\HandBrake\HandBrakeCLI.exe'

# Put log file here
if is_windows:
    log_file = os.path.expanduser('~/Desktop/simple_convert.log')
else:
    log_file = os.path.expanduser('~/simple_convert.log')

# Max media files to convert
max_convert_items = 0

# File types to convert
file_types = ('.avi', '.flv', '.mkv', '.mpeg')

# Plex Server Token - See URL below inorder to obtain your Token
# https://support.plex.tv/hc/en-us/articles/204059436-Finding-your-account-token-X-Plex-Token
enable_plex_update = False
plex_url = '{YOUR PLEX IP ADDRESS}:32400'
plex_token = '{YOUR PLEX TOKEN}'


""" Don't change the following unless you know what you are doing!! """

""" Set up the logger """
logging.basicConfig(filename=log_file, level=logging.INFO)

console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s: %(name)-12s - %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)
logger = logging.getLogger('simple_convert')

""" Update Plex Server """
def update_plex():
    logger.info("plex - sending request to update Plex")
    url = 'http://%s/library/sections/all/refresh?X-Plex-Token=%s' % (plex_url, plex_token)

    try:
        urllib2.urlopen(url).read()
    except urllib2.HTTPError, e:
        logger.warning("plex - unable to make request to Plex - HTTP Error %s", str(e.code))
    except urllib2.URLError, e:
        logger.warning("plex - unable to make request to Plex - URL Error %s", e.reason)
    else:
        logger.info("plex - update successful")

""" Build a array of files to convert """
def find_media_files(media_path):
    unconverted = []
    for root, dirs, files in os.walk(media_path):
        for file in files:
            if file.startswith('.'):
                continue

            if file.endswith(file_types):
                old_file = os.path.join(root, file)
                old_file_size = os.path.getsize(old_file)
                new_file = os.path.splitext(old_file)[0]+'.mp4'
                media_file = {
                    'old_file': old_file,
                    'old_file_size': old_file_size,
                    'new_file': new_file
                }
                unconverted.append(media_file)

    sorted_unconvered = sorted(unconverted, key=lambda k: k['old_file'])
    return sorted_unconvered[:max_convert_items] if max_convert_items else sorted_unconvered

""" Convert files found to mp4 using ffmeg """
def convert_ffmpeg(input_file, output_file):
    logger.info("ffmpeg - converting %s to %s", input_file, output_file)

    try:
        dev_null = open(os.devnull, 'w')
        return_code = subprocess.call([
            ffmpeg_cli,
            '-n',
            '-fflags', '+genpts',
            '-i', input_file,
            '-vcodec', 'copy',
            '-acodec', 'aac',
            '-strict', '-2',
            output_file
        ], stdout=dev_null, stderr=dev_null)

        # If the return code is 1 that means ffmpeg failed, use handbrake instead
        if return_code == 1:
            logger.warning("ffmpeg - failure converting %s", os.path.basename(input_file))
            remove_media_file(output_file)
            convert_handbrake(input_file, output_file)

    except OSError as e:
        if e.errno == os.errno.ENOENT:
            logger.warning("ffmpeg not found, install on your system to use this script")
            sys.exit(0)
    else:
        logger.info("ffmpeg - converting successful: %s", os.path.basename(input_file))

""" Convert files found to mp4 using HandBrakeCLI """
def convert_handbrake(input_file, output_file):
    logger.info("handbrakeCLI - converting %s to %s", input_file, output_file)

    try:
        dev_null = open(os.devnull, 'w')
        return_code = subprocess.call([
            handbrake_cli,
            '-i', input_file,
            '-o', output_file,
            '-f', 'mp4',
            '--loose-anamorphic',
            '--modulus', '2',
            '-e', 'x264',
            '-q', '19',
            '--cfr',
            '-a', '1',
            '-E', 'faac',
            '-6', 'dp12',
            '-R', 'Auto',
            '-B', '320',
            '-D', '0',
            '--gain', '0',
            '--audio-copy-mask', 'none',
            '--audio-fallback', 'ffac3',
            '-x', 'level=4.0:ref=16:bframes=16:b-adapt=2:direct=auto:me=tesa:merange=24:subq=11:rc-lookahead=60:analyse=all:trellis=2:no-fast-pskip=1'
        ], stdout=dev_null, stderr=dev_null)

        # If the return code is 1 that means handbrakeCLI failed
        if return_code == 1:
            logger.warning("handbrakeCLI - failure converting %s", os.path.basename(input_file))
            remove_media_file(output_file)
            sys.exit(0)

    except OSError as e:
        if e.errno == os.errno.ENOENT:
            logger.warning("handbrakeCLI not found, install on your system to use this script")
            sys.exit(0)
    else:
        logger.info("handbrakeCLI - converting successful for %s", os.path.basename(input_file))

""" Remove files quietly if they don't exist """
def remove_media_file(filename):
    try:
        os.remove(filename)
    except OSError as e:
        if e.errno != os.errno.ENOENT:
            raise
    else:
        logger.info("system - deleted file %s", os.path.basename(filename))

""" Main Application """
def main(argv):
 


    if len(argv) == 1:
        path, binary = os.path.split(argv[0])
        print "Usage: {} [directory ...]".format(binary)
        sys.exit(0)

    media_path = argv[1]

    if not os.path.exists(media_path):
        logger.error("Unable to find directory: %s", media_path)
        sys.exit(0)


    media_files = find_media_files(media_path)

    logger.info("%d total files to convert", len(media_files))

    i = 1
    for item in media_files:
        logger.info("converting %d of %d items", i, len(media_files))

        try:
            convert_ffmpeg(item['old_file'], item['new_file'])
        except KeyboardInterrupt:
            remove_media_file(item['new_file'])

        new_file_size = os.path.getsize(item['new_file'])

        # Remove old file if successful
        if (new_file_size >= item['old_file_size']):
            remove_media_file(item['old_file'])

        # Remove new file if failure, run handbrake instead
        elif (new_file_size < (item['old_file_size'] * .75)):

            logger.warning("ffmpeg - failure converting %s", os.path.basename(item['new_file']))
            remove_media_file(item['new_file'])

            try:
                convert_handbrake(item['old_file'], item['new_file'])
            except KeyboardInterrupt:
                remove_media_file(item['new_file'])

        # Remove old file if successful
        elif (new_file_size < item['old_file_size']):
            remove_media_file(item['old_file'])

        # Update Plex
        if enable_plex_update == True:
        	update_plex()

        # Keep a counter of item processed
        i = i + 1

if __name__ == '__main__':
    main(sys.argv)
