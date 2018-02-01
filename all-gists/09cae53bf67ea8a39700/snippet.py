"""
Download wallpapers from the FACETS website.
"""

import urllib.request
from urllib.error import HTTPError, URLError
from bs4 import BeautifulSoup

"""
Grab all images from the front page, and save them to a folder.
"""
def save_all_images(url, folder):
    html = get_response(url).decode("utf-8")
    image_links = get_images_links_from_html(html)
    for link in image_links:
        image = get_image_with_name(link)
        save_image(folder, image)

"""
Grab the image and image name given a URL.
"""
def get_image_with_name(url):
    html = get_response(url).decode("utf-8")
    soup = BeautifulSoup(html, "lxml")
    image_num = soup.select("#content .size13 strong")[0].contents[0]
    print(image_num)
    image_src = soup.select("#facet-image img")[0]["src"]
    image = get_response(image_src)
    return (image_src, image)

"""
Make an HTTP request to the following URL, and return the response.
"""
def get_response(url):
    try:
        http_request = urllib.request.urlopen(url)
        response_body = http_request.read()
        return response_body
    except HTTPError:
        return None
    except URLError as error:
        print(error.message)
        exit(1)

"""
Grab the image (a) links given the HTML source.
"""
def get_images_links_from_html(html):
    soup = BeautifulSoup(html, "lxml")
    image_links = [image_a["href"] for image_a in soup.select("div.thumb-image a")]
    return image_links

"""
Save the image to a given folder.
"""
def save_image(folder, image):
    if not image:
        return

    image_src = image[0]
    image_name = image_src[(image_src.rfind("/") + 1):]
    file_name = folder + image_name
    try:
        file = open(file_name, 'xb') # wb for overwriting
        file.write(image[1])
        file.close()
    except FileExistsError:
        return

# Client code
BASE_WALLPAPER_URL = "http://www.facets.la/wallpapers/"
WALLPAPER_FOLDER = "YOUR/FOLDER/HERE"

save_all_images(BASE_WALLPAPER_URL, WALLPAPER_FOLDER)
