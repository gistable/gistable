# For Python 2.x
# Dependencies are beautifulsoup4, workerpool, yattag
BASE_URL = '?'

import sys
no_pic = False
args = sys.argv
if len(args) == 2:
    if args[1] == 'n':
        no_pic = True

# Constants
RICH_DATE_FORMAT = '%B %d, %Y'
FILE_DATE_FORMAT = '%Y%m%d'

# Definitions
import collections
CodeInfo = collections.namedtuple('CodeInfo', 'code update_date detail_url')

import os
import shutil
UPDATE_PAGE_FILENAME = 'update.html'
IMG_FOLDER_NAME = 'img'


# Delete existing update page and img folder
def remove_old_update_page():
    if os.path.exists(UPDATE_PAGE_FILENAME):
        os.remove(UPDATE_PAGE_FILENAME)
        print('Removed old update page')
    if os.path.exists(IMG_FOLDER_NAME):
        shutil.rmtree(IMG_FOLDER_NAME)
        print('Removed old img folder')


# Create new update page and img folder
def create_new_update_page():
    update_page_file = open(UPDATE_PAGE_FILENAME, 'w')
    update_page_file.write("")
    update_page_file.close()
    print('Created update page')
    os.makedirs(IMG_FOLDER_NAME)
    print('Created img folder')

import time
LAST_UPDATE_FILENAME = 'LAST_UPDATE'


# Return last update time
def read_last_update_time():
    # create last update file if not exists and point date to 1970/1/1
    if not os.path.exists(LAST_UPDATE_FILENAME):
        new_file = open(LAST_UPDATE_FILENAME, 'w')
        new_file.write('19700101')
        new_file.close()
        print('Created ' + LAST_UPDATE_FILENAME)
    # read last update
    last_update_file = open(LAST_UPDATE_FILENAME)
    last_update = last_update_file.read()
    last_update = time.strptime(last_update, FILE_DATE_FORMAT)
    last_update_file.close()
    print('Last update was ' + time.strftime(RICH_DATE_FORMAT, last_update))
    return last_update

import urllib
from bs4 import BeautifulSoup
import re
URL_LIB_TIMEOUT_SLEEP = 0.5


# Read code info that are later than last update on multiple continuous pages
def read_updates(last_update):
    updated_code_info = []
    should_terminate = False
    url = BASE_URL
    index = 2
    while not should_terminate:
        code_info, terminate = read_update_per_page(url, last_update)
        updated_code_info.extend(code_info)
        should_terminate = terminate
        url = BASE_URL + 'page/' + str(index) + '/'
        index += 1
    return updated_code_info


# Read code info that are later than last update on one single page
def read_update_per_page(url, last_update):
    # read content
    while True:
        try:
            print('Reading ' + url + ' ...')
            content = urllib.urlopen(url).read()
            print("Read " + url)
            break
        except IOError:
            time.sleep(URL_LIB_TIMEOUT_SLEEP)
    # read posts that are later than last update
    soup = BeautifulSoup(content)
    content_archive = soup.find(name='div', id='content-archive')
    # detect 404 page
    if content_archive is None:
        return [], True
    all_posts = content_archive.findAll(name='div', id=re.compile('^post-'))
    updated_code_info = []
    terminate = False
    for post in all_posts:
        title = post.find(name='h2', class_='entry-title post-title')
        code = title.text
        date = post.find(name='time', class_='timestamp updated').text
        date = time.strptime(date, RICH_DATE_FORMAT)
        # do not terminate because we are still lacking updates
        if date > last_update:
            print('\t' + code + ' updated on ' + time.strftime(RICH_DATE_FORMAT, date))
            detail_url = title.find('a')['href']
            updated_code_info.append(CodeInfo(code=code, update_date=date, detail_url=detail_url))
        # terminate because we are fulfilled :)
        else:
            terminate = True
    return updated_code_info, terminate


# Download detail images for updated code info
def download_detail_images(updated_code_info):
    if not no_pic:
        # ready to crawl images from each detail page
        import workerpool
        import urllib
        image_urls_crawler_pool = workerpool.WorkerPool(size=len(updated_code_info))

        class ImageDownloader(workerpool.Job):
            def __init__(self, path, url):
                object.__init__(self)
                self.path = path
                self.url = url

            def run(self):
                while True:
                    try:
                        urllib.urlretrieve(url=self.url, filename=self.path)
                        return
                    except IOError:
                        time.sleep(URL_LIB_TIMEOUT_SLEEP)

        class ImageUrlsCrawler(workerpool.Job):
            def __init__(self, code, url):
                object.__init__(self)
                self.code = code
                self.url = url

            def run(self):
                while True:
                    try:
                        # Read content
                        print('Downloading ' + self.code + ' images from ' + self.url + ' ...')
                        content = urllib.urlopen(self.url).read()

                        # Get all image urls
                        soup = BeautifulSoup(content)
                        post_entry = soup.find(name='div', class_='post-entry')
                        all_images = post_entry.findAll(name='img')
                        all_image_urls = map(lambda t: t['src'], all_images)

                        # Create image folder
                        image_folder_name = IMG_FOLDER_NAME + os.path.sep + self.code
                        os.makedirs(image_folder_name)

                        # Ready to download each image
                        image_downloader_pool = workerpool.WorkerPool(len(all_image_urls))

                        # Download each image
                        for i in range(len(all_image_urls)):
                            file_path = image_folder_name + os.path.sep + str(i) + '.jpg'
                            image_downloader_pool.put(ImageDownloader(path=file_path, url=all_image_urls[i]))

                        # Finish up
                        image_downloader_pool.shutdown()
                        image_downloader_pool.wait()
                        print('Saved ' + self.code + ' images from ' + self.url + ' ...')
                        return
                    except IOError:
                        time.sleep(URL_LIB_TIMEOUT_SLEEP)
        # crawl each detail url for images
        for code_info in updated_code_info:
            image_urls_crawler_pool.put(ImageUrlsCrawler(code=code_info.code, url=code_info.detail_url))
        # finish up
        image_urls_crawler_pool.shutdown()
        image_urls_crawler_pool.wait()
        print('Finished downloading images')
    else:
        print('No images')

import yattag


# Report
def report(updated_code_info):
    doc, tag, text = yattag.Doc().tagtext()
    with tag('html'):
        with tag('body'):
            with tag('table', id='contents'):
                with tag('tr'):
                    headers = ['Code', 'Update', 'URL', 'Images']
                    for header in headers:
                        with tag('th'):
                            text(header)
                for code_info in updated_code_info:
                    with tag('tr'):
                        with tag('td'):
                            text(code_info.code)
                        with tag('td'):
                            text(time.strftime(RICH_DATE_FORMAT, code_info.update_date))
                        with tag('td'):
                            doc.asis('<a href="' + code_info.detail_url + '">Link</a>')
                        if not no_pic:
                            with tag('td'):
                                image_folder_name = IMG_FOLDER_NAME + os.path.sep + code_info.code
                                build_name = lambda n: image_folder_name + os.path.sep + n
                                image_file_names = map(build_name, os.listdir(image_folder_name))
                                for image_file_name in image_file_names:
                                    doc.asis('<img src="' + image_file_name + '"></img>')
    html = doc.getvalue()
    update_page_file = open(UPDATE_PAGE_FILENAME, 'w')
    update_page_file.write(html)
    update_page_file.close()
    print('Finished generating update report')

if __name__ == "__main__":
    remove_old_update_page()
    create_new_update_page()
    LAST_UPDATE = read_last_update_time()
    UPDATED_CODE_INFO = read_updates(LAST_UPDATE)
    download_detail_images(UPDATED_CODE_INFO)
    report(UPDATED_CODE_INFO)

