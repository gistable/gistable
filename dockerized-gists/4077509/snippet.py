"""
This python script encodes all files that have the extension mkv in the current
working directory.

Sources:
    http://ffmpeg.org/trac/ffmpeg/wiki/x264EncodingGuide
"""
import subprocess, os

#-------------------------------------------------------------------------------
# CONFIGURABLE SETTINGS
#-------------------------------------------------------------------------------

# controls the quality of the encode
CRF_VALUE = '21'

# h.264 profile
PROFILE = 'high'

# encoding speed:compression ratio
PRESET = 'fast'

# path to ffmpeg bin
FFMPEG_PATH = '/usr/local/bin/ffmpeg'

# font dir
FONT_DIR = '/var/www/.fonts'

#-------------------------------------------------------------------------------
# encoding script
#-------------------------------------------------------------------------------

def process():
    cwd = os.getcwd()

    # get a list of files that have the extension mkv
    filelist = filter(lambda f: f.split('.')[-1] == 'mkv', os.listdir(cwd))
    filelist = sorted(filelist)

    # encode each file
    for file in filelist:
        encode(file)


def encode(file):
    name = ''.join(file.split('.')[:-1])
    subtitles = 'temp.ass'.format(name)
    output = '{}.mp4'.format(name)

    try:
        command = [
            FFMPEG_PATH, '-i', file,
            '-c:v', 'libx264', '-tune', 'animation', '-preset', PRESET, '-profile:v', PROFILE, '-crf', CRF_VALUE,
        ]

        # create a folder called attachments and symlink it to FONT_DIR
        # extract attachments
        subprocess.call(['mkdir', 'attachments'])
        subprocess.call(['rm', '-f', FONT_DIR])
        subprocess.call(['ln', '-s', '{}/attachments'.format(os.getcwd()), FONT_DIR])

        os.chdir('attachments')

        subprocess.call([FFMPEG_PATH, '-dump_attachment:t', '', '-i', '../{}'.format(file)])

        os.chdir('..')

        # extract ass subtitles and and subtitle into command
        subprocess.call([FFMPEG_PATH, '-i', file, subtitles])
        if os.path.getsize(subtitles) > 0:
            command += ['-vf', 'ass={}'.format(subtitles)]

        command += ['-c:a', 'copy']             # if audio is using AAC copy it - else encode it
        command += ['-threads', '8', output]    # add threads and output
        subprocess.call(command)                # encode the video!

    finally:
        # always cleanup even if there are errors
        subprocess.call(['rm', '-fr', 'attachments'])
        subprocess.call(['rm', '-f', FONT_DIR])
        subprocess.call(['rm', '-f', subtitles])


if __name__ == "__main__":
    process()
