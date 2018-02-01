#!/usr/bin/python

__author__ = 'umair'

FONTS = (
    "/usr/share/fonts/truetype/ubuntu-font-family/Ubuntu-R.ttf",
    "/usr/share/fonts/truetype/droid/DroidSerif-Regular.ttf",
    "/usr/share/fonts/truetype/ttf-dejavu/DejaVuSans.ttf",
    "/home/umair/Downloads/Dosis/Dosis-ExtraBold.ttf"
)

try:
    from PIL import Image, ImageDraw, ImageFont, ImageEnhance
except:
    import Image, ImageDraw, ImageFont, ImageEnhance

class ImpropertlyConfigured(Exception):
    pass



def ReduceOpacity(im, opacity):
    """
    Returns an image with reduced opacity.
    Taken from http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/362879
    """
    assert opacity >= 0 and opacity <= 1
    if im.mode != 'RGBA':
        im = im.convert('RGBA')
    else:
        im = im.copy()
    alpha = im.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
    im.putalpha(alpha)
    return im

def Imprint(im, inputtext, font=None, color=None, opacity=0.6, margin=(30,30)):
    """
    imprints a PIL image with the indicated text in lower-right corner
    """
    if im.mode != "RGBA":
        im = im.convert("RGBA")
    textlayer = Image.new("RGBA", im.size, (0,0,0,0))
    textdraw = ImageDraw.Draw(textlayer)
    textsize = textdraw.textsize(inputtext, font=font)
    textpos = [(im.size[i]/2)-(textsize[i]/2)-margin[i] for i in [0,1]]
    textdraw.text(textpos, inputtext, font=font, fill=color)
    if opacity != 1:
        textlayer = ReduceOpacity(textlayer,opacity)
    return Image.composite(textlayer, im, textlayer)

def watermark(image, text, font_path, font_scale=None, font_size=None, color=(0,0,0), opacity=0.6, margin=(0, 0)):
    """
    image - PIL Image instance
    text - text to add over image
    font_path - font that will be used
    font_scale - font size will be set as percent of image height
    """
    if font_scale and font_size:
        raise ImpropertlyConfigured("You should provide only font_scale or font_size option, but not both")
    elif font_scale:
        width, height = image.size
        font_size = int(font_scale*height)
    elif not (font_size or font_scale):
        raise ImpropertlyConfigured("You should provide font_scale or font_size option")
    font=ImageFont.truetype(font_path, font_size)
    im0 = Imprint(image, text, font=font, opacity=opacity, color=color, margin=margin)
    return im0

import os, sys

def main():
    if len(sys.argv) < 2:
        print "Image path is required"
        return

    if len(sys.argv) < 3:
        print "Watermark text is required"
        return

    watermarked_path = sys.argv[1] + "/Watermarked"
    if not os.path.exists(watermarked_path):
        os.makedirs(watermarked_path)

    for (dirpath, dirnames, filenames) in os.walk(sys.argv[1]):
        if not dirpath.endswith("Watermarked"):
            for filename in filenames:
                try:
                    im = Image.open("%s/%s" % (dirpath, filename))
                    result = watermark(im, sys.argv[2], color=(255,255,255), opacity=0.4,
                                        font_path=FONTS[3], font_size=100)
                    result.save("%s/%s" % (watermarked_path, filename))
                except:
                    pass

if __name__ == "__main__":
    main()