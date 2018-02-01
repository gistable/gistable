import argparse
import urllib.request
import os
import img2pdf

from os import walk
from os.path import join
from bs4 import BeautifulSoup

work_dir = os.path.dirname(__file__)


def download_images(url):
    html = urllib.request.urlopen(url).read()
    soup = BeautifulSoup(html)
    title = 'pdf_images'  # soup.title.string
    images = soup.findAll('img', {'class': 'slide_image'})

    for image in images:
        image_url = image.get('data-full').split('?')[0]
        command = 'wget %s -P %s --quiet' % (image_url, title)
        os.system(command)

    convert_pdf(title)


def convert_pdf(url):
    f = []
    for (dirpath, dirnames, filenames) in walk(join(work_dir, url)):
        f.extend(filenames)
        break
    f = ["%s/%s" % (url, x) for x in f]
    print("Making pdf")

    pdf_bytes = img2pdf.convert(f, dpi=300, x=None, y=None)
    doc = open('presentation.pdf', 'wb')
    doc.write(pdf_bytes)
    doc.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("url", type=str,
                        help="download an slideshare presentation given the url")
    args = parser.parse_args()

    download_images(args.url)
    os.system('rm -r pdf_images')
