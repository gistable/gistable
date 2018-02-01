import os
import re
import zipfile
import sys
import colorama
from subprocess import call
from selenium import webdriver
from termcolor import colored, cprint


# Your aria2c path
ARIA2C_PATH = 'aria2c'
# Your phantomjs path
PHANTOMJS_PATH = 'phantomjs'


def sanitize_filename(filename):
    return ''.join(c for c in filename if c not in ('\\', '/', ':', '*', '?', '"', '<', '>', '|')).rstrip()


def delete_dir(top):
    for root, dirs, files in os.walk(top, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))
    if os.path.isfile(top):
        os.remove(top)
    elif os.path.isdir(top):
        os.rmdir(top)


def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


def download_image(url, path, index, skip=True):
    # print(url)
    # print(path)
    if skip and os.path.isfile(path):
        cprint(colored(index + ": Existed", "magenta"))
        return True
    download_path = path + '.d'
    cmd = ARIA2C_PATH + ' -q --allow-overwrite=true --header="Referer: http://tw.ikanman.com/" -o "' + download_path + '" "' + url + '"'
    if call(cmd):
        cprint(colored(index + ": Download failed", "red"))
        return False
    else:
        os.rename(download_path, path)
        cprint(colored(index + ": Download successfully", "green"))
        return True


def get_image_filename(index, filename):
    name, extension = os.path.splitext(filename)
    return '{:06d}{}'.format(index + 1, extension)


def zip_dir(path, zip_obj):
    for root, dirs, files in os.walk(path):
        for file in files:
            zip_obj.write(os.path.join(root, file))


def download_chapter(index, url, folder, skip=True):
    print(url)
    driver.get(url)

    # Get chapter name
    chapter_name = driver.find_element_by_tag_name('h2').text
    print(chapter_name)
    chapter_name = sanitize_filename(chapter_name)

    # Get folder
    folder = os.path.join(folder, '{:06d}-{}'.format(index + 1, chapter_name))

    # Get zip filename
    zip_filename = folder + '.zip'

    # Check zip file
    if skip and os.path.isfile(zip_filename):
        return

    # Ensure folder
    ensure_dir(folder)

    # Prepare images
    image_url_prefix = driver.execute_script('return pVars.manga.filePath')
    image_filename_list = driver.execute_script('return cInfo.files')
    download_ok = False
    while not download_ok:
        print("Start turn")
        download_ok = True
        for i, filename in enumerate(image_filename_list):
            image_url = image_url_prefix + filename
            image_path = os.path.join(folder, get_image_filename(i, filename))
            download_result = download_image(image_url, image_path, str(index + 1) + '-' + str(i + 1))
            download_ok = download_ok and download_result

    # Zip folder
    zip_obj = zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED)
    zip_dir(folder, zip_obj)
    zip_obj.close()

    # delete folder
    delete_dir(folder)


def download_comic(url):
    print(url)
    driver.set_window_size(1024, 768)
    driver.get(url)

    # Create comic dir
    comic_name = driver.find_element_by_tag_name('h1').text
    print(comic_name)
    folder = sanitize_filename(comic_name)
    ensure_dir(folder)

    # Get all chapter urls
    chapter_urls = []
    for item in reversed(driver.find_elements_by_class_name('chapter-list')):
        for ul in item.find_elements_by_tag_name('ul'):
            for li in reversed(ul.find_elements_by_class_name('status0')):
                chapter_urls.append(li.get_attribute('href'))

    names = os.listdir(folder)
    # Download chapters
    for i in range(0, len(chapter_urls)):
        zip_name = None
        p = re.compile('^{:06d}.+?\\.zip$'.format(i + 1))
        for name in names:
            if p.match(name):
                zip_name = name
                break
        if not zip_name:
            download_chapter(i, chapter_urls[i], folder)
        else:
            cprint(colored(zip_name + " Existed", "magenta"))


if __name__ == '__main__':
    colorama.init()
    driver = webdriver.PhantomJS(executable_path=PHANTOMJS_PATH)
    for comic_url in sys.argv[1:]:
        download_comic(comic_url)
    driver.close()
