# WeChat aud file converter to wav files
# Dependencies:
#   SILK audio codec decoder (available at https://github.com/gaozehua/SILKCodec)
#   ffmpeg
#
# By Gabriel B. Nunes (gabriel@kronopath.net)
# Adapted from another script by Nicodemo Gawronski (nico@deftlinux.net)
# 

import os, argparse, subprocess
from datetime import datetime


def is_silk_file(file_path):
    # If the file has a SILK file header, we know it's a SILK file. Otherwise, we assume it's the
    # older AMR file format.
    input_file = open(file_path, 'rb');
    header = input_file.read(10)
    silk_header = '#!SILK_V3'
    # WeChat adds an extraneous byte at the beginning of its SILK files for some reason.
    input_file.close()
    return header[1:] == silk_header


def convert_amr_file(input_dir, input_file_name, output_dir):
    # These files are AMR files without the AMR header, so they can be converted by just adding the
    # AMR file header and then converting from AMR to WAV.

    input_file_path = os.path.join(input_dir, input_file_name);
    input_file = open(input_file_path, 'rb')

    intermediate_file_name = input_file_name.replace(".aud", ".amr")
    intermediate_file_path = os.path.join(output_dir, intermediate_file_name)
    intermediate_file = open(intermediate_file_path, 'wb')

    amr_header = "#!AMR\n"
    intermediate_file.write(amr_header + input_file.read())

    input_file.close()
    intermediate_file.close()

    output_file_name = input_file_name.replace(".aud", ".wav")
    output_file_path = os.path.join(output_dir, output_file_name)

    black_hole_file = open("black_hole", "w")
    subprocess.call(["ffmpeg", "-i", intermediate_file_path, output_file_path],
                    stdout = black_hole_file, stderr = black_hole_file)
    black_hole_file.close()
    
    # Delete the junk files
    os.remove("black_hole")
    os.remove(intermediate_file_path)


def convert_silk_file(input_dir, input_file_name, decoder_file_path, output_dir):
    # These files are encoded with the SILK codec, originally developed by Skype. They can be
    # converted by stripping out the first byte and then using the SILK decoder.

    input_file_path = os.path.join(input_dir, input_file_name);
    input_file = open(input_file_path, 'rb')

    intermediate_file_1_name = input_file_name.replace(".aud", ".silk")
    intermediate_file_1_path = os.path.join(output_dir, intermediate_file_1_name)
    intermediate_file_1 = open(intermediate_file_1_path, 'wb')

    # WeChat adds a single extra byte before their SILK files. We need to strip it out.
    intermediate_file_1.write(input_file.read()[1:])
    
    input_file.close()
    intermediate_file_1.close()

    intermediate_file_2_name = input_file_name.replace(".aud", ".pcm")
    intermediate_file_2_path = os.path.join(output_dir, intermediate_file_2_name)
    intermediate_file_2 = open(intermediate_file_2_path, 'wb')

    output_file_name = input_file_name.replace(".aud", ".wav")
    output_file_path = os.path.join(output_dir, output_file_name)
    
    black_hole_file = open("black_hole", "w")

    # Use the SILK decoder to convert it to PCM
    subprocess.call([decoder_file_path, intermediate_file_1_path, intermediate_file_2_path],
                    stdout = black_hole_file, stderr = black_hole_file)

    # And then ffmpeg to convert that to wav
    subprocess.call(["ffmpeg", "-f", "s16le", "-ar", "24000",
                    "-i", intermediate_file_2_path, output_file_path],
                    stdout = black_hole_file, stderr = black_hole_file)

    black_hole_file.close()
    intermediate_file_2.close()

    # Delete the junk files
    os.remove("black_hole")
    os.remove(intermediate_file_1_path)
    os.remove(intermediate_file_2_path)


class Main(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        
        audio_src = values
        now = datetime.utcnow()
        now = datetime.strptime(str(now), '%Y-%m-%d %H:%M:%S.%f')
        now = now.strftime('%d-%m-%Y %H.%M.%S')
        converted = now + "_converted"
        os.mkdir(converted)

        try:
            # Decide which one of these are AMR files and which are SILK, and then convert.
            for dirname, dirnames, filenames in os.walk(audio_src):
                for filename in filenames:
                    if filename[0] == '.': continue
                    input_path = os.path.join(dirname, filename)
                    if (is_silk_file(input_path)):
                        convert_silk_file(dirname, filename, namespace.silk_decoder, converted)
                    else:
                        convert_amr_file(dirname, filename, converted)

            print "Done!"
        except:
            print("Something went wrong converting the audio files.\n"
                "Common problems:\n"
                "You may be missing the dependencies (ffmpeg and/or the SILK codec decoder).\n"
                "The decoder (and its dependencies) must be in the specified path.\n"
                "The SILK codec decoder also can't handle very large file paths.\n"
                "Try a shorter path to your input directory.")


parser = argparse.ArgumentParser(description=".aud converter: convert wechat .aud files into .wav",
        epilog="This script is an open source tool under the GNU GPLv3 license. Uses content "\
                "modified from a tool originally for DEFT 8.")
parser.add_argument("Folder", action=Main, help=".aud files root folder.")
parser.add_argument("-s", "--silk-decoder", nargs="?", default="./decoder",
        help="Path to the SILK codec decoder program.")

args = parser.parse_args()
