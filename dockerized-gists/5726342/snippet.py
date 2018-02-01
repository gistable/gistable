#!/usr/bin/env python

import requests
import re
from bs4 import BeautifulSoup
from subprocess import call, check_output
import string


def fetch_html(links):
    returns = []
    for link in links:
        link = "http://www.justinguitar.com/en/" + link
        print link
        returns.append(requests.get(link).text)
    return returns


# Return a tuple: (lesson_title, youtube_video_code)
def parse_info(page):
    soup = BeautifulSoup(page)

    title_raw = soup.find('title').string.split('|')[0]
    title = filter(lambda x: x in string.printable and x != '\n', title_raw)
    title = remove_double_space(title)

    pat = re.compile(u'watch\?v=(.+?)"')
    matches = pat.findall(page)

    if len(matches) == 0:
        return title, None

    return title, matches[0]


# Just for pretty lesson names
def remove_double_space(input_str):
    output = re.sub(' +', ' ', input_str)
    if output == input_str:
        return output
    else:
        return remove_double_space(output)

# Fetch index pages which has links to all beginner lessons
r = requests.get('http://www.justinguitar.com/en/BC-000-BeginnersCourse.php')
start_page = r.text

# Search for all links to lessons
pat = re.compile('<a href="(BC-[0-9]{3}-.+?)"')
pages = pat.findall(start_page)

# Fetch html for each lesson
pages_html = fetch_html(pages)

# Crawl each lesson page, pull out lesson names and youtube link code
youtube_codes = []
for html in pages_html:
    code = parse_info(html)
    print code
    if code not in youtube_codes:
        youtube_codes.append(code)

# Leech the hell out of them
for lesson in youtube_codes:

    # Ignore if lesson has no video
    if lesson[1] is None:
        call(['touch', lesson[0]])
        continue

    # Use youtube-dl to get fresh download link and file extension
    command = ['youtube-dl', lesson[1], '--skip-download', '--get-url',
               '--get-filename', '-f', '35/34/82/44/43/100']
    shell_output = str(check_output(command))
    direct_link, fname = shell_output.splitlines()
    file_ext = fname[fname.rfind('.'):]
    file_name = lesson[0] + file_ext

    # Then aria2 for serious multi-part download acceleration
    print 'Downloading ' + file_name + '...'
    command = ['aria2c', "-o", file_name, '-x2',
               "%s" % direct_link]
    shell_output = check_output(command)
    print shell_output

print 'All done! :)'
