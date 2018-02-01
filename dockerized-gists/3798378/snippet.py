# YouTube playlist audio retreiver and iTunes-compliant podcast XML generation tool.

# This script will download each video file from the specified YouTube playlist, losslessly extract
# the audio, delete the video, and ultimately produce an iTunes-compliant podcast XML with the
# appropriate metadata, including chapter markers (if provided in the description). If you run the
# script again, only videos that haven't already been converted will be downloaded, allowing you to
# schedule the script to run as often as needed without stressing your internet connection or
# hard drive space. After generating the files and xml, you can easily host them on a local server
# in order to use them with iTunes or your favorite podcast aggregator -- but that's beyond this
# script's jurisdiction.

# Requires the following:
#  * Python 2.6 or later installed
#  * youtube-dl, compiled or .py, in the same directory as the script,
#    and updated to the latest version with -U
#  * ffmpeg, in the same directory as the script or in the path
#  * ffprobe, in the same directory as the script or in the path

# Installation instructions:
#  1. Download and install Python 2.6. Note that you might have to set the path
#     to the Python runtime manually below, or alternatively figure out how to
#     add it to your path. (I'm sorry, but I can't be bothered to script this.)
#  1. Download youtube-dl. Put youtube-dl in the same directory as this script.
#  2. Run "python youtube-dl -U" to update youtube-dl, either from cmd.exe or PowerShell
#     on Windows, or through Terminal in OSX.
#  3. Download the ffmpeg static build for your OS, if it's not already installed.
#     Put ffmpeg and ffprobe into the same directory as this script.
#  4. If you're on Windows, rename ffmpeg.exe and ffprobe.exe to just ffmpeg and ffprobe.
#     You might have to show file extensions for known file types by going to an
#     Explorer window, tapping Alt to show the menu bar, going to Tools/Folder Options,
#     going to view, and unchecking "Hide extensions for known file types". Feel free
#     to re-check this later.*
#  5. You should be all set! Run "python playlist-to-podcast.py" from cmd.exe/PowerShell
#     or Terminal, and feel free to schedule the script to run as often as you like.
#
#  * Note that this step is due to an apparent bug in youtube-dl. It will be removed
#    once youtube-dl is fixed, or once I find the stupid mistake in my own code.

# youtube-dl can currently be found here: http://rg3.github.com/youtube-dl/index.html
# ffmpeg can currently be found here: http://ffmpeg.org/download.html

# TODO: make paths unicode-friendly, like youtube-dl code
# TODO: allow youtube-dl, ffmpeg, and ffprobe to exist in script execution directory,
#       not just the current working directory

#####################
# Config Parameters #
#####################

playlist_url = "http://www.youtube.com/playlist?list=ELwUqsFXhm1Bk"

# Set these to specific numbers to limit the files downloaded, or set to None to download everything. 

playlist_range_start = 100
playlist_range_end = 101

# "high" will download 720p mp4, which has aac with maximum 192kbps. (Format 22.)
# "medium" will download 480p flv, which has aac with maximum 128kbps. (Format 35.)
# "low" will download 360p mp4, which has aac with maximum 96kbps. (Format 18.)
# "xlow" will download 240p flv, which has mp3 with maximum 64kbps. (Format 5.)

audio_quality = "medium"

# Check youtube-dl documentation for more info, but it's really quite intuitive.

download_rate_limit = "1.0m"

# If the current playlist includes timecodes in the description, this regex will try to get them.

timecode_regex = r"^(.*):\s+(\d+:\d+)\s*$"

# XML configuration.

xml_url = playlist_url
xml_base_url = "http://localhost/"
xml_title = "TotalBiscuit: Mailbox"
xml_author = None # if None, picks arbitrary author from one of the videos
xml_image_url = "http://i1.ytimg.com/vi/hR-lVgfGdKw/mqdefault.jpg" # if None, picks arbitrary thumbnail URL from one of the videos

# Default filenames and associated regular expressions. You probably don't have to worry about these.

all_filenames_filename = "all-filenames.txt"
all_filenames_filename_temp = "all-filenames.txt.tmp"
download_urls_filename = "download-urls.txt"
downloaded_files_subdirectory_name = "downloaded"
podcast_xml_filename = "podcast.xml"
audio_file_output_format = "%(autonumber)s - %(upload_date)s [%(id)s].%(ext)s"
audio_file_output_format_id_regex = r"^.*\[(.*)\].*$"

# Absolute path to the Python runtime. 
# Set to None to attempt autodetect based on system path.
# Set manually to the absolute path if you're having issues.

python_path = None

########
# Code #
########

import os
import sys
import re
import json
import subprocess
import signal
import datetime
import json
import cgi

# Global variables and private config parameters.

current_directory = os.getcwd()
downloaded_files_directory = os.path.join(current_directory, downloaded_files_subdirectory_name)
current_date_formatter = "%a, %d %b %Y %H:%M:%S %Z"
quality_map = {"high":22, "medium":35, "low":18, "xlow":5}
allowed_video_formats = [".mp4", ".flv"]
allowed_audio_formats = [".aac", ".m4a", ".mp3"]
tmp_formats = [".part", ".tmp"]

def error(message):
    print "[" + "playlist-to-podcast" + "] " + message
    sys.exit(1)

def status_message(message):
    print "[" + "playlist-to-podcast" + "] " + message

# Stolen shamelessly from youtube-dl/PostProcessor.py and modified.
def detect_executables(program, absolute_path=False):
    if absolute_path == True:
        if os.path.isfile(program) and os.access(program, os.X_OK):
            return program
        return None
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if os.path.isfile(exe_file) and os.access(exe_file, os.X_OK):
                return exe_file
        return None

def format_is_aac(format):
    return (format == 22) or (format == 35) or (format == 18)
    
def format_for_html(str, escape_quotes=False):
    return cgi.escape(str, escape_quotes).encode("ascii", "xmlcharrefreplace")
    
def refresh_playlist_data():
    status_message("Retrieving playlist data from " + playlist_url + ".")

    try:
        all_filenames_file_temp = open(all_filenames_filename_temp, "w+")
    except Exception, e:
        error(str(e))

    arg_call = [python_path, "youtube-dl"]

    args = arg_call + ["--get-filename"]

    if playlist_range_start:
        args += ["--playlist-start", str(playlist_range_start)]
    if playlist_range_end:
        args += ["--playlist-end", str(playlist_range_end)]

    args += [playlist_url]

    status_message("Calling " + str(args) + ".")

    try:
        retval = subprocess.call(args, stdout=all_filenames_file_temp)
    except Exception, e:
        error(str(e))
    
    all_filenames_file_temp.seek(0)

    try:
        all_filenames_file = open(all_filenames_filename, "w+")
    except Exception, e:
        error(str(e))

    for line in all_filenames_file_temp:
        video_id = os.path.splitext(line)[0]
        all_filenames_file.write(video_id + "\n")

    all_filenames_file_temp.close()
    all_filenames_file.close()

    os.remove(all_filenames_filename_temp)

def refresh_download_batch_file():
    status_message("Generating list of missing videos in " + downloaded_files_directory + " to " + download_urls_filename + ".")

    try:
        all_filenames_file = open(all_filenames_filename, "r")
        download_urls_file = open(download_urls_filename, "w+")
    except Exception, e:
        error(str(e))

    existing_files = set()
    id_regex = re.compile(audio_file_output_format_id_regex)

    if os.path.isdir(downloaded_files_directory):
        for filename in os.listdir(downloaded_files_directory):
            base = os.path.splitext(filename)[0]
            extension = os.path.splitext(filename)[1]
            if extension in allowed_audio_formats:
                id_results = id_regex.match(base)
                if (id_results):
                    id = id_results.group(1)
                    existing_files.add(id)

    for id in all_filenames_file:
        if id.rstrip() not in existing_files:
            download_urls_file.write(id)
            status_message("Adding " + id.rstrip() + " to batch download file.")

    all_filenames_file.close()
    download_urls_file.close()

def download_with_batch_file():
    # Exit early if no files to download.
    download_urls_directory = os.path.join(current_directory, download_urls_filename)
    try:
        download_urls_filesize = os.path.getsize(download_urls_directory)
    except Exception, e:
        error(str(e))
    if download_urls_filesize == 0:
        status_message("No files to download.")
        return

    status_message("Calling youtube-dl to download missing videos to " + downloaded_files_directory + ".")

    if not os.path.isdir(downloaded_files_directory):
        try:
            os.mkdir(downloaded_files_directory)
        except Exception, e:
            error(str(e))

    os.chdir(downloaded_files_directory)

    try:
        format = quality_map[audio_quality]
    except Exception, e:
        error("Error: invalid audio quality setting.")

    arg_call = [python_path, "youtube-dl.py"]

    args = arg_call + ["--rate-limit", download_rate_limit, "--write-info-json", "--console-title", "--format", str(format), "--extract-audio", "--output", audio_file_output_format, "--batch-file", download_urls_directory]

    if format_is_aac(format):
        args += ["--audio-format", "m4a"]      

    status_message("Calling " + str(args) + ".")

    try:
        retval = subprocess.call(args)
    except Exception, e:
        error(str(e))

    os.chdir(current_directory)

def generate_xml():
    status_message("Generating podcast xml.")

    if os.path.isdir(downloaded_files_directory):
        os.chdir(downloaded_files_directory)

        files = os.listdir(downloaded_files_directory)

        json_data = {}
        id_regex = re.compile(audio_file_output_format_id_regex)

        for filename in files:
            extension = os.path.splitext(filename)[1]
            if extension == ".json":
                id_results = id_regex.match(filename)
                if (id_results):
                    id = id_results.group(1)
                    try:
                        json_file = open(filename)
                    except Exception, e:
                        error(str(e))
                    json_datum = json.load(json_file)
                    json_data[id] = json_datum

        try:
            podcast_xml_file = open(podcast_xml_filename, "w+")
        except Exception, e:
            error(str(e))

        current_date = datetime.datetime.now()
        current_date_string = current_date.strftime(current_date_formatter)
        if (xml_image_url == None):
            # pick arbitrary element
            image_url = json_data[json_data.keys()[0]]["thumbnail"]
        else:
            image_url = xml_image_url
        if (xml_author == None):
            # pick arbitrary element
            author = json_data[json_data.keys()[0]]["uploader"]
        else:
            author = xml_author

        podcast_xml_file.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n")
        podcast_xml_file.write("<rss xmlns:itunes=\"http://www.itunes.com/dtds/podcast-1.0.dtd\" version=\"2.0\">\n")
        podcast_xml_file.write("\t<channel>\n")
        podcast_xml_file.write("\t\t<title>" + format_for_html(xml_title) + "</title>\n")
        podcast_xml_file.write("\t\t<link>" + format_for_html(playlist_url) + "</link>\n")
        podcast_xml_file.write("\t\t<language>en-us</language>\n")
        podcast_xml_file.write("\t\t<itunes:author>" + format_for_html(author) + "</itunes:author>\n")
        podcast_xml_file.write("\t\t<itunes:image href=\"" + format_for_html(image_url, True) + "\" />\n")

        #upload date 20120404

        for filename in files:
            base = os.path.splitext(filename)[0]
            extension = os.path.splitext(filename)[1]

            if extension in allowed_audio_formats:
                match = id_regex.match(filename)
                id = match.group(1)
                if (xml_image_url == None):
                    image_url = json_data[id]["thumbnail"]

                podcast_xml_file.write("\t\t\t<item>\n")
                podcast_xml_file.write("\t\t\t<enclosure url=\"" + format_for_html(xml_base_url + filename, True) + "\"></enclosure>\n")
                podcast_xml_file.write("\t\t\t<link>" + format_for_html(xml_base_url + filename) + "</link>\n")
                podcast_xml_file.write("\t\t\t<guid>" + format_for_html(xml_base_url + filename) + "</guid>\n")

                if id in json_data:
                    json_date = datetime.datetime.strptime(json_data[id]["upload_date"].encode("ascii", "ignore"), "%Y%m%d")
                    json_date_string = json_date.strftime(current_date_formatter)

                    podcast_xml_file.write("\t\t\t<title>" + format_for_html(json_data[id]["title"]) + "</title>\n")
                    podcast_xml_file.write("\t\t\t<itunes:author>" + format_for_html(json_data[id]["uploader"]) + "</itunes:author>\n")
                    podcast_xml_file.write("\t\t\t<itunes:image href=\"" + format_for_html(image_url, True) + "\" />\n")
                    podcast_xml_file.write("\t\t\t<itunes:summary>" + format_for_html(json_data[id]["description"]) + "</itunes:summary>\n")
                    podcast_xml_file.write("\t\t\t<pubDate>" + format_for_html(json_date_string) + "</pubDate>\n")

                podcast_xml_file.write("\t\t\t</item>\n")

        podcast_xml_file.write("\t</channel>\n")
        podcast_xml_file.write("</rss>\n")

        podcast_xml_file.close()

        os.chdir(current_directory)
    else:
        error("Error: " + downloaded_files_directory + " does not exist.")

def check_dependencies():
    global python_path
    python_found = False
    if python_path == None:
        python_absolute_path = detect_executables("python")
        if not python_absolute_path:
            python_absolute_path = detect_executables("python.exe")
            if  python_absolute_path:
                python_found = True
        else:
            python_found = True
    else:
        python_absolute_path = detect_executables(python_path, True)
        python_found = (python_absolute_path != None)

    if python_found:
        python_path = python_absolute_path
        status_message("python found at " + python_absolute_path + ".")
    else:
        error("Error: python not found.")

    ffmpeg_path = detect_executables("ffmpeg")
    if ffmpeg_path:
        status_message("ffmpeg found at " + ffmpeg_path + ".")
    else:
        error("Error: ffmpeg not found.")

    ffprobe_path = detect_executables("ffprobe")
    if ffprobe_path:
        status_message("ffprobe found at " + ffprobe_path + ".")
    else:
        error("Error: ffprobe not found.")

    if os.path.isfile("youtube-dl"):
        status_message("youtube-dl found.")
    elif os.path.isfile("youtube-dl.py"):
        status_message("youtube-dl.py found.")
    else:
        error("Error: youtube-dl not found.")

def cleanup():
    status_message("Cleaning up any lingering temporary files.")

    if os.path.isdir(downloaded_files_directory):
        files = os.listdir(downloaded_files_directory)
        for filename in files:
            filepath = os.path.join(downloaded_files_directory, filename)
            extension = os.path.splitext(filename)[1]
            if extension in tmp_formats:
                os.remove(filepath)
    for filename in os.listdir(current_directory):
        filepath = os.path.join(current_directory, filename)
        extension = os.path.splitext(filename)[1]
        if extension in tmp_formats:
            os.remove(filepath)

def playlist_to_podcast():
    # Add working directory to path.

    current_path = os.environ["PATH"]
    os.environ["PATH"] = current_directory + os.pathsep + current_path

    # Step 0. Check all dependencies.
    check_dependencies()

    # Step 1: Refresh YouTube playlist filenames and URLs via youtube-dl.
    refresh_playlist_data()

    # Step 2: Scan currently existing audio files and match against filenames pulled from server. Generate batch download list.
    refresh_download_batch_file()

    # Step 3: Download videos from batch download list via youtube-dl.
    download_with_batch_file()

    # Step 4: Generate XML using downloaded metadata, with optional chapter times.
    generate_xml()

    # Step 5: Cleanup extra part/video files, just in case.
    # TODO: commenting out for liability purposes; need to ensure 100%
    #       that the user can't accidentally delete their system :)
    # cleanup()

    status_message("Done! Enjoy.")

########
# Main #
########

if __name__ == "__main__":
    try:
        playlist_to_podcast()
    except KeyboardInterrupt:
        print "[" + os.path.basename(__file__) + "] " + "Program interrupted."
        sys.exit(0)
