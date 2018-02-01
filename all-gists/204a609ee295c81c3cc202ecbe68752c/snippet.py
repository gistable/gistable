# Copyright (c) 2016 Kenneth Blomqvist
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

############################
## How to use
############################
# To scrape images run e.g. python scrape.py <Search keyword> --count 200 --label <label>
# The images will be saved in a subfolder called "images" and it will contain another folder called whatever 
# you passed in as the label parameter. This enables you to easily scrape a bunch of different searches while still 
# keeping the images organized. The image files will be saved as jpeg images and named by the image contents sha1 hash.

import os
import re
import time
import argparse
import requests
import io
import hashlib
import itertools
import base64
from PIL import Image
from multiprocessing import Pool
from selenium import webdriver

argument_parser = argparse.ArgumentParser(description='Download images using google image search')
argument_parser.add_argument('query', metavar='query', type=str, help='The query to download images from')
argument_parser.add_argument('--count', metavar='count', default=100, type=int, help='How many images to fetch')
argument_parser.add_argument('--label', metavar='label', type=str, help="The directory in which to store the images (images/<label>)", required=True)


def ensure_directory(path):
    if not os.path.exists(path):
        os.mkdir(path)

def largest_file(dir_path):
    def parse_num(filename):
        match = re.search('\d+', filename)
        if match:
            return int(match.group(0))

    files = os.listdir(dir_path)
    if len(files) != 0:
        return max(filter(lambda x: x, map(parse_num, files)))
    else:
        return 0

def fetch_image_urls(query, images_to_download):
    image_urls = set()

    search_url = "https://www.google.com/search?safe=off&site=&tbm=isch&source=hp&q={q}&oq={q}&gs_l=img"
    browser = webdriver.Firefox()
    browser.get(search_url.format(q=query))
    def scroll_to_bottom():
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)

    image_count = len(image_urls)
    delta = 0
    while image_count < images_to_download:
        print("Found:", len(image_urls), "images")
        scroll_to_bottom()

        images = browser.find_elements_by_css_selector("img.rg_ic")
        for img in images:
            image_urls.add(img.get_attribute('src'))
        delta = len(image_urls) - image_count
        image_count = len(image_urls)

        if delta == 0:
            print("Can't find more images")
            break

        fetch_more_button = browser.find_element_by_css_selector(".ksb._kvc")
        if fetch_more_button:
            browser.execute_script("document.querySelector('.ksb._kvc').click();")
            scroll_to_bottom()

    browser.quit()
    return image_urls

def persist_image(dir_image_src):
    label_directory = dir_image_src[0]
    image_src = dir_image_src[1]

    size = (256, 256)
    try:
        image_content = requests.get(image_src).content
    except requests.exceptions.InvalidSchema:
        # image is probably base64 encoded
        image_data = re.sub('^data:image/.+;base64,', '', image_src)
        image_content = base64.b64decode(image_data)
    except Exception as e:
        print("could not read", e, image_src)
        return False

    image_file = io.BytesIO(image_content)
    image = Image.open(image_file).convert('RGB')
    resized = image.resize(size)
    with open(label_directory + hashlib.sha1(image_content).hexdigest() + ".jpg", 'wb')  as f:
        resized.save(f, "JPEG", quality=85)

    return True


if __name__ == '__main__':
    args = argument_parser.parse_args()

    ensure_directory('./images/')

    query_directory = './images/' + args.label + "/"
    ensure_directory(query_directory)

    image_urls = fetch_image_urls(args.query, args.count)

    values = [item for item in zip(itertools.cycle([query_directory]), image_urls)]

    print("image count", len(image_urls))

    pool = Pool(12)
    results = pool.map(persist_image, values)
    print("Images downloaded: ", len([r for r in results if r]))


