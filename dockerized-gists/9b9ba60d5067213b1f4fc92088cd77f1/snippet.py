#!/usr/bin/env python3
# Author: Mahendra Yadav(userimack)
#  Run the script using the following command:
#
#  Python3 check_image.py <image url>
#
#  For example:
#
#  Python3 check_image.py 'https://dgplug.org/assets/img/main-dgp.png'
#  Output:
#  Image type detected: png
#  Success: Image is saved with name: main-dgp.png

import requests
import re
import os
import sys
import imghdr
from time import gmtime, strftime


def check_for_image(response):
    if 'image' in response.headers['Content-Type']:
        image_type = imghdr.what('', response.content)  # Using imaghdr module to verify the signature of the image
        if image_type:
            print("Image type detected: {0}".format(image_type))
            return True
        else:
            print("Error: Unable to verify the signature of the image")
            exit(1)
    return False


def get_image(url):
    try:
        response = requests.get(url)
    except:
        print("Error: While requesting url: {0}".format(url))
        exit(1)

    if response:
        if check_for_image(response):
            extension = os.path.basename(response.headers['Content-Type'])
            if 'content-disposition' in response.headers:
                content_disposition = response.headers['content-disposition']
                filename = re.findall("filename=(.+)", content_disposition)
            elif url[-4:] in ['.png', '.jpg', 'jpeg', '.svg']:
                filename = os.path.basename(url)
            else:
                filename = 'image_{0}{1}'.format(strftime("%Y%m%d_%H_%M_%S", gmtime()), '.' + str(extension))
            with open(filename, 'wb+') as wobj:
                wobj.write(response.content)
            print("Success: Image is saved with name: {0}".format(filename))
        else:
            print("Sorry: The url doesn't contain any image :(")


if __name__ == '__main__':
    if len(sys.argv) < 1:
        print("Error: No arguments supplied. Please give the url as arguments\nRun the script as:\npython3 check_image.py <some_url>")

    get_image(sys.argv[1])