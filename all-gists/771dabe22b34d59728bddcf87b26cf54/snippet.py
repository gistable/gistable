__author__ = "Ali Bahraminezhad - antipattern.ir"
__license__ = "GPL"
__version__ = "1.0.0"
__maintainer__ = "Ali Bahraminezhad"


import re
import os
import tempfile
import json
import urllib.request
import xml.etree.ElementTree as ET
from urllib.parse import urlparse

# url patterns to downlaod and get course strucutres from Microsoft Virtual Academy
urlPattern = "https://api-mlxprod.microsoft.com/services/products/anonymous/{}?languageId=12"
courseDetailsPattern = "https://cp-mlxprod-static.microsoft.com/{}/en-us/coursedetails.xml"
manifestPattern = "https://cp-mlxprod-static.microsoft.com/{}/en-us/imsmanifestlite.json"
videoPattern = "https://cp-mlxprod-static.microsoft.com/{}/en-us/content/content_{}/videosettings.xml"
subtitlePattern = "https://cp-mlxprod-static.microsoft.com/{}/en-us/{}"

"""Replace all \/ with /"""
def fix_slash(str):
    return str.replace('\/', '/')

"""Replace some invalid characters for filenames"""
def fix_name(str):
    not_allowed_chars = ['!', '<', '>', '?', '*', '|', '"', ':', '/', '\\', '.']
    for char in not_allowed_chars:
        str = str.replace(char, ' ').strip();
    return str

"""Windows clear console"""
def cls():
    os.system('cls')

"""Download html from a URL with utf-8-sig encoding"""
def download_string(url):
    response = urllib.request.urlopen(url)
    data = response.read()
    return data.decode('utf-8-sig')

"""Download and save html/text with utf-8-encoding and save it to the disk"""
def download_and_save(url, filePath):
    with open(filePath, mode='w', encoding='utf-8') as a_file:
        a_file.write(download_string(url)) 

"""Append string to a text file"""
def append_to_file(str, filePath):
    with open(filePath, "a") as myfile:
        myfile.write(str)

"""Create a text file with some string"""
def create_text_file(str, filePath):
    with open(filePath, mode='w', encoding='utf-8') as a_file:
        a_file.write(str) 

"""Use regex to extract course id from MVA urls"""
def extract_cource_id(url):
    url = urlparse(url).path
    return re.search('-(\d*)$', url).group(1)

"""Use regex to extract complete course id from MVA xmls"""
def extract_main_cource_id(url):
    return re.search('(\d+-\d+)', url).group(1) 


if __name__ == "__main__":

    # Course titles will store here
    titles = []

    # Each video course has a subtitle, subtitle links will store here
    subtitles = []

    # Depands on the course, each course might have several video qualities
    # Urls will store here by their quality
    courseItems = {
        '1080p': [],
        '720p': [],
        '540p': [],
        '360p': [],
    }

    # Let the game begins
    courceUrl = input("Enter course url:")
    courseId = extract_cource_id(courceUrl)

    cls()
    print('Getting course details, pelase wait...')

    # get the main url
    try:
        mainUrl = fix_slash(download_string(urlPattern.format(courseId)))
        mainCourseId = extract_main_cource_id(mainUrl)
    except:
        print('Error: Course URL IS NOT VALID')
        raise SystemExit
    
    # download course data
    courseDetails = ET.fromstring(download_string(courseDetailsPattern.format(mainCourseId)))
    manifest = json.loads(download_string(manifestPattern.format(mainCourseId)))['manifest']
    
    # print course data
    print(manifest['metadata']['title'].strip())

    # getting table of contents
    print("Getting table of contents, video links and subtitles, please wait ...")
    for item in manifest['organizations']['organization']:
        for i in item['item']:
            for j in i['item']:
                titles.append(j['title'].strip())     
                # getting video urls
                if j['resource']['metadata']['learningresourcetype'].lower() == 'video':
                    videoSetting = ET.fromstring(download_string(videoPattern.format(mainCourseId, j['@identifier'].lower())))                 

                    # extract download links and subtitle
                    videos = videoSetting.find(".//MediaSources[@videoType='progressive']")
                    subtitle = videoSetting.find(".//MarkerResourceSource[@type='ttml']")

                    if subtitle != None and subtitle.text != None:
                        subtitles.append(subtitlePattern.format(mainCourseId, subtitle.text))

                    for video in videos:
                       courseItems[video.get('videoMode')].append(video.text.strip())                
    
    # create directory for downloaded files
    projectDir = './' + fix_name(manifest['metadata']['title'])
    subtitleDir = projectDir + '/subtitles/'
    if not os.path.exists(projectDir):
        os.makedirs(projectDir)
        os.makedirs(subtitleDir)

    # download subtitles by user desire
    if len(subtitles) > 0:
        downloadSubtitles = input('Would you like to download subttiles? (y/n)')
        if downloadSubtitles.lower() == 'y':
            print('Downloading subtitles, please wait ...')
            for counter in range(0, len(subtitles)):
                download_and_save(subtitles[counter], '{}/{}-{}{}'.format(subtitleDir,(counter + 1), fix_name(titles[counter]), '.ttml'))
    
    print('Exporting video links, please wait ...')
    # save download links into text files
    for quality, links in courseItems.items():
        # create a empty file for quality
        txt_quality_file_path = './{}/{}.txt'.format(projectDir, quality)
        create_text_file('', txt_quality_file_path)

        if len(links) == 0:
            os.remove(txt_quality_file_path)
            continue

        counter = 0
        for url in links:
            append_to_file(titles[counter], txt_quality_file_path)
            append_to_file('\n', txt_quality_file_path)
            append_to_file(url, txt_quality_file_path)
            append_to_file('\n\n', txt_quality_file_path)
            counter = counter + 1


    print('Files saved in "{}"'.format(os.path.abspath(projectDir)))


