# wodim, 17/07/2014 -- public domain

# This script can be used to get information and/or extract
# the .wav files inside the .raw files of the GTA 3 and Vice City games.
# They are located inside the /audio folder once the game is installed.

# There are two files: sfx.raw and sfx.sdt. The raw file includes the audio
# samples, and the sdt file includes pointers to each sample, with information
# such as the size and the sample rate. Here is a detailed description, from the
# GTAModding wiki site: http://www.gtamodding.com/index.php?title=SFX

# 4b - int - offset of audio file in sfx.raw
# 4b - int - size of audio file in bytes
# 4b - int - samples per sec, the speed of audio
# 4b - int - loop start, where looping would begin relative to audio file's position, 0 for beginning of audio file
# 4b - int - loop end, where looping would end relative to audio file's position, -1 for end of audio file

import os
import wave
import sys

if len(sys.argv) < 3:
    print("Usage: %s <sdt file> <raw file> [output folder]" % (sys.argv[0]))
    sys.exit(1)

dir_file = open(sys.argv[1], 'rb')
raw_file = open(sys.argv[2], 'rb')

if len(sys.argv) >= 4:
    extracted_dir = sys.argv[3]
    if not os.path.isdir(extracted_dir):
        os.mkdir(extracted_dir)
else:
    extracted_dir = None

sfx_count = 0
while True:
    field = dir_file.read(20)

    if len(field) < 20:
        break

    sfx_file = "sfx%05d" % (sfx_count,)
    offset = int.from_bytes(field[0:4], byteorder='little')
    size = int.from_bytes(field[4:8], byteorder='little')
    samples = int.from_bytes(field[8:12], byteorder='little')
    loop_start = int.from_bytes(field[12:16], byteorder='little')
    loop_end = int.from_bytes(field[16:20], byteorder='little')

    print('File:\t\t', sfx_file)
    print('Offset:\t\t', offset)
    print('Size:\t\t', size)
    print('Sample rate:\t', samples)
    print('Loop start:\t', loop_start)
    print('Loop end:\t', loop_end)
    print('==================================')

    if extracted_dir: # i.e. if the user wants to extract the file
        file_path = os.path.join(extracted_dir, '%s.wav' % (sfx_file,))

        # remove existing file
        if os.path.isfile(file_path):
            os.remove(file_path)

        raw_file.seek(offset, 0)
        sound = raw_file.read(size)
        
        with wave.open(file_path, 'wb') as output_file:
            output_file.setparams((1, 2, samples, 0, 'NONE', 'NONE'))
            output_file.writeframes(sound)

    sfx_count += 1

dir_file.close()
raw_file.close()