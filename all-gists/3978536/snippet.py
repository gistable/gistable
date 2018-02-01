# On Debian, you need to install these packages:
# jpegoptim optipng pngcrush advancecomp

import subprocess
from os.path import splitext

from django.dispatch import receiver
from easy_thumbnails.signals import saved_file, thumbnail_created

# on-save image optimization
@receiver(saved_file)
def optimize_file(sender, fieldfile, **kwargs):
    optimize(fieldfile.path)

# thumbnail optimization
@receiver(thumbnail_created)
def optimize_thumbnail(sender, **kwargs):
    optimize(sender.path)

def optimize(path):
    # taken from trimage (http://trimage.org/)
    runString = {
        ".jpeg": u"jpegoptim -f --strip-all '%(file)s'",
        ".jpg": u"jpegoptim -f --strip-all '%(file)s'",
        ".png": u"optipng -force -o7 '%(file)s' && advpng -z4 '%(file)s' && pngcrush -rem gAMA -rem alla -rem cHRM -rem iCCP -rem sRGB -rem time '%(file)s' '%(file)s.bak' && mv '%(file)s.bak' '%(file)s'"
    }

    ext = splitext(path)[1].lower()
    if ext in runString:
        subprocess.Popen(runString[ext] % {'file': path}, shell=True)