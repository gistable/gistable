#!/usr/bin/python
"""
python3.4 ~/PycharmProjects/learn-python/download-images.py -u {url} -v
"""
import sys
import os
import getopt
from lxml import html
import urllib.request
import urllib.error
from urllib.request import urlopen
import urllib.parse
import threading
import math
import re
 
# COLORS
HEADER = '\033[95m'
OKBLUE = '\033[94m'
OKGREEN = '\033[92m'
WARNING = '\033[93m'
FAIL = '\033[91m'
ENDC = '\033[0m'
 
# variables
verbose = False
replace_files = False
base_url = ''
regex = re.compile("catalog/product/cache/\d+?/")
 
 
def error(message=""):
    print("{1}{0}{2}".format(message, FAIL, ENDC))
 
 
def warning(message):
    print("{0}{1}{2}".format(WARNING, message, ENDC))
 
 
def print_help():
    print("USAGE:")
    print("  options:")
    print("    -u {{url}} -> {0}required*{1}".format(WARNING, ENDC))
    print("    -p {path} -> default is the current directory")
    print("    -v -> show execution messages")
    print("    -r -> replace files")
    print("    --user {username} -> for http authentication")
    print("    --pass {password} -> for http authentication")
    print("    --realm {string} -> for http authentication")
 
 
def call_with_custom_opener(url=None, realm="Staging Area", user='', password=''):
    """ call external site and get site response object """
    global verbose
 
    if url is None:
        print("Please pass a URL to the function")
 
    if verbose:
        print("Send request to {0} with user:{1} and password:{2}".format(url, user, password))
 
    url_parser_object = urllib.parse.urlparse(url)
    uri = url_parser_object.netloc
    # set up authentication info
    auth_handler = urllib.request.HTTPBasicAuthHandler()
    auth_handler.add_password(realm, uri, user, password)
    # add HTTPBasicAuthentication handler to opener object
    opener = urllib.request.build_opener(auth_handler)
    # add the opener to the request object
    urllib.request.install_opener(opener)
    try:
        res = opener.open(url)
        return res
    except IOError as e:
        if hasattr(e, 'code'):
            if e.code != 401:
                error('We got another error')
                print(e.code)
            else:
                error("We have a authentication problem")
                print(e.headers)
                print(e.headers['www-authenticate'])
    if verbose:
        error("No result returned")
    return None
 
 
class ImagesDownloaderThread(threading.Thread):
    """ download images in a thread """
    base_path = '.'
    images_list = []
 
    def __init__(self, name='', images_list=[], base_path="."):
        threading.Thread.__init__(self, name=name)
        if images_list:
            self.images_list = images_list
        self.base_path = base_path
 
    def run(self):
        for image_url in self.images_list:
            self.copy_image_to_local(image_url)
 
    def copy_image_to_local(self, image_url=''):
        """ copy files locally """
        global verbose, replace_files, base_url
 
        image_url = self.prepare_url(image_url)
        if not image_url:
            return
 
        save_into_file = get_image_save(image_url=image_url, path=self.base_path)
        response = open_url(image_url, string_prefix=self.getName() + " -> ")
 
        if response is not None:
            if os.path.isfile(save_into_file):
                if replace_files:
                    if verbose:
                        warning(self.getName() + " -> Removing file: " + str(save_into_file))
                    os.unlink(save_into_file)
                else:
                    return
            image = open(save_into_file, "wb")
            content = response.read()
            image.write(content)
            image.close()
 
    def prepare_url(self, url):
        global base_url
        parse_object = urllib.parse.urlparse(url=url)
        if not bool(parse_object.scheme):
            url = base_url + url
            warning(self.getName() + " -> invalid URL changed to: " + str(url))
        return url
 
 
def get_image_path(image_url):
    """ get image path from url """
    parsed_url = urllib.parse.urlparse(url=image_url)
    return parsed_url.path
 
 
def open_url(url, post_data=None, header_raw=None, string_prefix=''):
    """ open url and mask user agent to the chrome one
    and returns a Request object """
    global verbose
    if verbose:
        print(string_prefix + "Call URL: {0}".format(url))
 
    try:
        if header_raw is None:
            header_raw = {
                'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.93 Safari/537.36"
            }
        if post_data is not None:
            post_data = urllib.parse.urlencode(post_data)
 
        request = urllib.request.Request(url, headers=header_raw)
        request_object = urllib.request.urlopen(request, post_data)
        return request_object
    except urllib.error.URLError as e:
        error(string_prefix + "Exception for URL: {0}".format(url))
        print(string_prefix + e.reason)
    except Exception as e:
        error(string_prefix + "Exception for URL: {0}".format(url))
        print(string_prefix + str(e))
 
 
def get_image_save(image_url, path=".", create_dir=False):
    """ get image save path, and create a directory if needed """
    if path == '':
        return ""
    image_path = get_image_path(image_url)
    add_slash = ""
    try:
        if path[-1] != os.sep and image_path[0] != os.sep:
            # check if we have slash at the end of the path or the beginning of the image_path
            add_slash = os.sep
    except (KeyError, IndexError) as e: # For dict, list|tuple
        error('could not get it')
    save_into_file = "{0}{1}{2}".format(path, add_slash, image_path)
    if create_dir:
        image_directory = os.path.dirname(save_into_file)
        if image_directory == '':
            return "" 
        if not os.path.isdir(image_directory):
            if verbose:
                warning("Creating a directory: " + str(image_directory))
            os.makedirs(image_directory)  # create image directory if it doesn't exist
 
    return save_into_file
 
 
def is_magento_cache_url(image_url=''):
    global regex
    if image_url == '':
        warning(image_url + ' is not a URL')
        return False
    if regex.search(image_url):
        # match catalog/product/cache/ + any number + /
        return True
    return False
 
 
def get_non_cache_url(image_url):
    # replace the cache path
    no_cache_image_url = re.sub("cache/\d.*/[0-9a-zA-Z][0-9a-zA-Z]+/", '', image_url)
    
    try:
		# fix for nice images + 
        search_string = "media/catalog/product/"
        start_index = int(no_cache_image_url.index(search_string)) + len(search_string)
        image_path_in_products_dir = no_cache_image_url[start_index:]
        if (image_path_in_products_dir.count('/')) > 2:
            file_extension = no_cache_image_url[no_cache_image_url.rfind("."):]
            no_cache_image_url = re.sub("\/[^\/]*$", '', no_cache_image_url)
            no_cache_image_url = no_cache_image_url + file_extension
    except ValueError as err:
        pass
    return no_cache_image_url
 
 
def execute_program(url, user, password, realm, path="."):
    global verbose
 
    if user != '' and password != '':
        if verbose:
            print("Call with realm authentication")
        request_object = call_with_custom_opener(url=url, realm=realm, user=user, password=password)
    else:
        if verbose:
            print("Call with NO realm authentication")
        request_object = open_url(url)
 
    doc = html.parse(request_object).getroot()
    images = []
    for elem in doc.iter():
        if elem.tag == 'img':
            image_url = elem.get("src")
            if is_magento_cache_url(image_url):
                image_url = get_non_cache_url(image_url)
 
            get_image_save(image_url=image_url, path=path, create_dir=True)
            if image_url not in images:
                images.append(image_url)
 
    number_of_images = len(images)
    number_of_threads_to_spawn = 7  # todo: make this an argument
    elements_per_thread = math.ceil(number_of_images / number_of_threads_to_spawn)
    for i in range(number_of_threads_to_spawn):
        # run a thread to download all images
        starting_index = i*elements_per_thread
        end_index = starting_index + elements_per_thread
        download_images = images[starting_index:end_index]
 
        if not download_images:
            continue
 
        new_thread = ImagesDownloaderThread(name="Thread-{0}".format(i + 1), images_list=download_images, base_path=path)
        new_thread.start()
 
 
def set_base_url(url):
    global base_url
    parse_object = urllib.parse.urlparse(url=url)
    if parse_object:
        base_url = parse_object.scheme + '://' + parse_object.netloc
 
 
def main():
    global verbose  # if true display errors
    global replace_files  # remove and replace existing files
 
    url = ''  # url from which to take the data
    user = ''  # server realm used to http authentication
    password = ''  # server realm used to http authentication
    realm = ''  # server realm used to http authentication
    path = '.'  # path where the files will be save
 
    try:
        # opts is the declared options in this
        # args is left over arguments passed to the script
        options, args = getopt.getopt(sys.argv[1:], "u:hvpr", ["user=", "password=", "realm=", "help", "path"])
    except getopt.GetoptError as err:
        # print help information and exit:
        print(err)
        print_help()
        sys.exit(2)
 
    for option, value in options:
        if option == "-v":
            verbose = True
        elif option in ("-h", "--help"):
            print_help()
            sys.exit()
        elif option == "-u":
            url = value
            set_base_url(url)
        elif option == "--user":
            user = value
        elif option == "--password":
            password = value
        elif option == "--realm":
            realm = value
        elif option in ("-p", "--path"):
            path = value
        elif option == "-r":
            replace_files = True
 
    if url == '':
        error("No URL was given, check help for more information (-h, --help)")
        sys.exit()
 
    execute_program(url=url, user=user, password=password, realm=realm, path=path)
 
 
if __name__ == "__main__":
    main()
