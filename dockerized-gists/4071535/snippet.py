# GDC Vault videos can't be watched on mobile devices and this is a very sad thing indeed!
# (Note: this has changed for GDC2013, which lets you watch raw MP4 streams. Kudos!)
# This script is designed to circumvent this by downloading the lecture and slideshow
# videos which can then be re-encoded into whatever format you wish. Obviously, you
# won't be able to do this without access to the Vault. This is strictly for the
# convenience of legitimate Vault users!

# Note: this code is rather flimsy and was written as fast as possible for my own personal use.
# The code only works for the most recent GDC Vault videos, since they all use the same player
# format. If the XML format used to run the player is changed (as it  has in the past), the code
# will have to be reconfigured. In the past, I was able to feed a wget-compatible cookies.txt
# file into the wget call, but I can't get it to trigger anymore. So for now, the way I download
# each video is I look at the source for the video page, find the player.html URL, and feed
# that into the script. Ugly and slow, but hey, it works.

# I generally hate reinventing the wheel and it does look like youtube-dl does some of the same
# stuff I'm doing, but I couldn't get it to work with the GDC URLs. So off to Python land we go!!!

# Usage is as follows:
#   gdc-downloader.py "[GDC player.html URL]" [output dir]
#
# A GDC video URL looks like this:
#   http://www.gdcvault.com/play/1015662/Creative-Panic-How-Agility-Turned
#
# A GDC player.html URL looks like this:
#   http://evt.dispeak.com/ubm/gdc/sf12/player.html?xmlURL=xml/201203238_1331124629609NXXJ.xml&token=1234567890
#
# The output dir should be the name of your video. For example, suppling TestDir/GDCVid will create
# TestDir/GDCVid/GDCVid.xml, TestDir/GDCVid/GDCVid-slide.flv, etc.

# You need to have Python 2.7 and rtmpdump installed in order for this script to work. I recommend macports.

#############
# Constants #
#############

xml_prefixes = { "default":"", "sf13":"xml/" }
rtmp_suffixes = { "default":"/fcs/ident", "gdc2009":"/ondemand" }
player_regular_expression = r"^(.*[/](.*?)[/])(.*?player\.html)(.*?xml.*?=(.*?)([&].*?)?)$"
swf_name_regular_expression = r"^.*embed the Flash Content SWF when all tests are passed.*?\"src\".*?\"(.*?)\".*$"

# DEPRECATED: This URL was retrieved from the player SWF, and may change in the future.
# rtmp_url = "rtmp://fms.digitallyspeaking.com/cfx/st/ondemand/fcs/ident"

########
# Code #
########

import sys
import os
import subprocess
import re
import argparse
from urlparse import urlparse
from urllib2 import urlopen
from urllib2 import Request
from urllib2 import HTTPError
from urllib2 import URLError
from xml.dom import minidom

def text(msg):
    print "[gdc_downloader] " + msg

def error(message):
    print "[gdc-downloader] Error: " + message
    sys.exit(1)

def message(msg):
    print "[gdc-downloader] Message: " + msg

def check_dependencies():
    # TODO: check rtmpdump
    pass

def dump_to_file(data, dest):
    dest_dir = os.path.abspath(os.path.split(dest)[0])
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)
    debug_file = open(dest, "w")
    debug_file.write(data)
    debug_file.close()

def download_url(url):
    r = Request(url=url)

    message("downloading url: " + url)

    try:
        response = urlopen(r)
    except HTTPError, e:
        error("http error: " + "\"" + str(e) + "\"")
    except URLError, e:
        error("url error (make sure you're online): " + "\"" + str(e) + "\"")
    
    return response.read()

def retrieve_data_from_base_url(url, xml_dest):
    html = url

    player_regex = re.compile(player_regular_expression)
    player_results = player_regex.match(html)

    if not player_results:
        error("player URL not found")

    dump_to_file(html, xml_dest)

    base_url = player_results.group(1)
    event_name = player_results.group(2)
    player_url = player_results.group(3)
    player_arguments = player_results.group(4)
    xml_url = player_results.group(5)

    full_xml_url = base_url + (xml_prefixes[event_name] if event_name in xml_prefixes else xml_prefixes["default"]) + xml_url

    message("player url is " + base_url + player_url)
    message("event name is " + event_name)
    message("player arguments are " + player_arguments)
    message("xml url is " + full_xml_url)

    player_html = download_url(base_url + player_url).replace('\n', '').replace('\r', '')

    swf_name_regex = re.compile(swf_name_regular_expression)
    swf_name_results = swf_name_regex.match(player_html)

    if not swf_name_results:
        error("SWF URL not found")

    swf_url = base_url + swf_name_results.group(1) + ".swf"

    message("swf url is " + swf_url)

    data = {}
    data["player_url"] = base_url + player_url + player_arguments
    data["event_name"] = event_name
    data["swf_url"] = swf_url
    data["xml_url"] = full_xml_url

    return data

def parse_xml_from_url(url, xml_dest, event_name):
    xml = download_url(url)

    dump_to_file(xml, xml_dest)

    parsed_xml = minidom.parseString(xml)

    # GDC2013 abandons the old rtmp streams in favor of raw mp4 urls
    mbr_video_tags = parsed_xml.getElementsByTagName("MBRVideo")
    mp4_video_tags = parsed_xml.getElementsByTagName("mp4video")
    small_video_tags = parsed_xml.getElementsByTagName("smallResolutionVideo")

    if (mbr_video_tags or mp4_video_tags or small_video_tags): # list the mp4 urls without downloading
        text("")
        text("Found raw mp4 urls, please download one of these with your favorite browser:")

        mp4_urls = []
        base_mp4_url = ""

        # the "mp4video" tag is likely to exist, and will provide a base url for the "MBRVideo" tags
        if mp4_video_tags:
            if mp4_video_tags[0].firstChild is not None:
                parsed_mp4_url = urlparse(mp4_video_tags[0].firstChild.nodeValue)
                if not parsed_mp4_url.netloc:
                    message("base mp4 url not found, please do some digging or contact the gist author")
                else:
                    base_mp4_url = "http://" + parsed_mp4_url.netloc + "/"
                    text("  * base mp4 url is " + base_mp4_url)
                    text("  * default mp4 url is " + mp4_video_tags[0].firstChild.nodeValue)

        # this isn't really necessary, but included for completion
        if small_video_tags:
            if small_video_tags[0].firstChild is not None:
                text("  * small video url is " + small_video_tags[0].firstChild.nodeValue)

        for subtag in mbr_video_tags:
            stream = subtag.getElementsByTagName("streamName")
            if stream:
                if stream[0].firstChild is not None:
                    # the streamName should conform to "mp4:path/to/video.mp4"
                    text("  * video url is " + base_mp4_url + stream[0].firstChild.nodeValue.partition(":")[2])

        text("")

        return {}
    else: # download the rtmp streams
        akamai_host_xml = parsed_xml.getElementsByTagName("akamaiHost")
        speaker_video_xml = parsed_xml.getElementsByTagName("speakerVideo")
        slide_video_xml = parsed_xml.getElementsByTagName("slideVideo")

        if not akamai_host_xml or not speaker_video_xml or not slide_video_xml:
            error("xml missing properties")

        if akamai_host_xml[0].firstChild is None or speaker_video_xml[0].firstChild is None or slide_video_xml[0].firstChild is None:
            error("xml missing properties")

        akamai_host = "rtmp://" + akamai_host_xml[0].firstChild.nodeValue + (rtmp_suffixes[event_name] if event_name in rtmp_suffixes else rtmp_suffixes["default"])
        speaker_video = speaker_video_xml[0].firstChild.nodeValue.replace(".flv", "")
        slide_video = slide_video_xml[0].firstChild.nodeValue.replace(".flv", "")

        message("akamai host is " + akamai_host)
        message("speaker video is " + speaker_video)
        message("slide video is " + slide_video)

        # some of the xml files contain exta audio tracks; we want those, don't we?
        audios = parsed_xml.getElementsByTagName("audios")
        audio_metadata = {}
        if (audios):
            for audio_node in audios[0].getElementsByTagName("audio"):
                audio_url = None
                code = None
                for (name, value) in audio_node.attributes.items():
                    if name == "url":
                        audio_url = value.replace(".flv", "")
                    elif name == "code":
                        code = value
                if code:
                    audio_metadata[code] = audio_url
                    message("audio " + code + " is " + audio_url)

        data = {}
        data["akamai"] = akamai_host
        data["speaker"] = speaker_video
        data["slide"] = slide_video
        data["audio"] = audio_metadata

        return data

def download_video(rtmp, playpath, swf_url, page_url, filename):
    args = ["rtmpdump", "--rtmp", rtmp, "--playpath", playpath, "--swfUrl", swf_url, "--pageUrl", page_url, "--flv", filename]

    try:
        retval = subprocess.call(args, stdin=None)
    except Exception, e:
        error("rtmpdump error")

    return None

def download_gdc_video_at_url(url, dest=""):
    dest_path = os.path.abspath(dest)
    dest_name = "GDCVideo" if os.path.split(dest)[1] == "" else os.path.split(dest)[1]

    # Step 0: Check dependencies.
    check_dependencies()

    # Step 1: Extract the following from the URL: player URL, SWF URL, XML URL.
    data = retrieve_data_from_base_url(url, os.path.join(dest_path, dest_name + "-player-url.txt"))

    # Step 2: Parse the XML and extract the speaker video URL, slide video URL, and metadata.
    metadata = parse_xml_from_url(data["xml_url"], os.path.join(dest_path, dest_name + ".xml"), data["event_name"])

    # Step 3: Download the videos.
    if (metadata):
        download_video(metadata["akamai"], metadata["slide"], data["swf_url"], data["player_url"], os.path.join(dest_path, dest_name + "-slide.flv"))
        download_video(metadata["akamai"], metadata["speaker"], data["swf_url"], data["player_url"], os.path.join(dest_path, dest_name + "-speaker.flv"))
        for code in metadata["audio"]:
            download_video(metadata["akamai"], metadata["audio"][code], data["swf_url"], data["player_url"], os.path.join(dest_path, dest_name + "-audio-" + code + ".flv"))

    message("All done!")

def _main():
    parser = argparse.ArgumentParser()
    parser.add_argument("player_url", help="the full player.html URL retrieved from the video page source")
    parser.add_argument("output_name", nargs='?', help="the name of the output directory")
    args = parser.parse_args()

    download_gdc_video_at_url(args.player_url, ("" if args.output_name is None else args.output_name));

if __name__ == "__main__":
    _main()