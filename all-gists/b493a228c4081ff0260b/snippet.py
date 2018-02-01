# -*- coding: utf-8 -*-

from django.core.files import File
from django.core.files.temp import NamedTemporaryFile

import requests
import urlparse


def save_image_from_url(field, url):

    r = requests.get(url)

    if r.status_code == requests.codes.ok:

        img_temp = NamedTemporaryFile(delete = True)
        img_temp.write(r.content)
        img_temp.flush()

        img_filename = urlparse.urlsplit(url).path[1:]

        field.save(img_filename, File(img_temp), save = True)

        return True

    return False

