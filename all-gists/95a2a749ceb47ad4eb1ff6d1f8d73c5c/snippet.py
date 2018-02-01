#!/usr/bin/env python
# coding: utf-8
import requests
import StringIO
from PIL import Image
import os
import time

YES = 'X'
NO = '-'
BLACK = 0
WHITE = 255
HERE = os.path.dirname(os.path.abspath(__file__))
THRESHOLD = 135  # calculated manually by find_threshold()

def get_img(url, **kwargs):
    """ download image from url
    return Image object
    """
    r = requests.get(url, **kwargs)
    return Image.open(StringIO.StringIO(r.content))


def grey_img(image):
    """ too slow to be replaced by Image.convert()
    """
    gray_image = Image.new('L', image.size)
    gray_data = []
    raw_data = image.getdata()
    for r, g, b in raw_data:
        value = 0.299 * r + 0.578 * g + 0.114 * b
        # value = 0.44 * r + 0.44 * g + 0.44 * b
    gray_image.putdata(gray_data)
    return gray_image


def binarization(image ,threshold=127):
    """
    first convert RGB img to grey img
    image: Image  object
    threshold: int
    return modes “L” (luminance) greyscale image object
    """
    # img = grey_img(image)
    img = image.convert('L')
    raw_data = img.getdata()
    bin_data = []
    for d in raw_data:
        if d < threshold:
            bin_data.append(BLACK)
        else:
            bin_data.append(WHITE)
    img.putdata(bin_data)
    return img


def xprojection(img, box=()):
    """
    box is region of the img
        box: (left, upper, right, lower)
    return: list
    """
    if not box:
        left, upper, (right, lower) = 0, 0, img.size
    else:
        left, upper, right, lower = box
    shadow = [0]*(right-left)
    for x in xrange(left, right):
        for y in xrange(upper, lower):
            if img.getpixel((x, y)) == BLACK:
                shadow[x] += 1
    return shadow


def yprojection(img, box=()):
    """
    box is region of the img
        box: (left, upper, right, lower)
    return: list
    """
    if not box:
        left, upper, (right, lower) = 0, 0, img.size
    else:
        left, upper, right, lower = box
    shadow = [0]*(lower-upper)
    for y in xrange(upper, lower):
        for x in xrange(left, right):
            if img.getpixel((x, y)) == BLACK:
                shadow[y] += 1
    return shadow


def continuous_lines(segment, single=0):
    """ projection data partitioning the range
    segment: list by xprojection() or yprojection()
    single: boolean
    return list
    """
    if single:
        length = len(segment)
        start, end = 0, length
        for i in segment:
            if i > 0:
                break
            else:
                start += 1
        else:
            start = 0
        for i in segment[::-1]:
            if i > 0:
                break
            else:
                end -= 1
        else:
            end = 0
        return [start, end]
    else:
        areas = []
        start_end = []
        pre = 0
        length = len(segment)
        for i, j in enumerate(segment):
            if j > 0:
                if pre == BLACK:  # segment head
                    start_end = [i, None]  
                elif i == (length-1):  # segment end
                    start_end[1] = i+1 # end, range+1
                    areas.append(start_end)
            else:  # j == 0
                if start_end:
                    start_end[1] = i # end, range+1
                    areas.append(start_end)
                    start_end = []
            pre = j
        return areas

def lonely_pixel(pixs, pos):
    """
    pixs:  image.load()
    pos: (x,y)
    """
    x,y = pos
    xy = [-1,0,1]
    for i in xy:
        for j in xy:
            if i==0 and j==0:
                continue  # pixel self
            try:
                p = pixs[x+i,y+j]
            except IndexError:
                p = WHITE
            if p == BLACK:
                return False
    return True


def minesweeper(img):
    """ clear the only one black pixel in 2x2 grid
    img: img object must be mode "L"
    """
    def _2x2(pixs, pos):  # only black in 2x2
        x,y = pos
        m = None
        for i in range(0,2):
            for j in range(0,2):
                try:
                    p = pixs[x+i,y+j]
                except IndexError:
                    p = WHITE
                if p == BLACK:
                    if m: # already have a black pixel
                        return None
                    else:
                        m = (x+i, y+j)
        return m

    pixs = img.load()
    width, heigh = img.size
    for w in range(0, width, 2):
        for h in range(0, heigh, 2):
            m = _2x2(pixs, (w,h))
            if m:
                if lonely_pixel(pixs, m):
                    x,y = m
                    pixs[x,y] = WHITE
    return img


def img_split(img):
    """
    parts of as small as possible world area
    return list region of image  object
    """
    xsize, ysize = img.size
    xsegment = xprojection(img)
    xs = continuous_lines(xsegment)
    regions = []
    for i,(start_x, end_x) in enumerate(xs):
        ysegment = yprojection(img, (start_x, 0, end_x, ysize))
        start_y, end_y = continuous_lines(ysegment, 1)
        box = (start_x, start_y, end_x, end_y)
        region = img.crop(box)
        regions.append(region)
    return regions


def img2str(img):
    """
    img: Image object
    return string
    """
    xsize, ysize = img.size
    content = ''
    for y in xrange(ysize):
        line = ''
        for x in xrange(xsize):
            c = YES if img.getpixel((x, y)) == BLACK else NO
            line += c
        content += '%s\n' %line
    return content


def img_compare(imga, imgb):
    """
    :imga source img
    :imgb model img
    return  0 <= float <= 1
    """
    count = 0
    a_x = xprojection(imga)
    b_x = xprojection(imgb)
    for i, n in enumerate(a_x):
        try:
            count += abs(n - b_x[i])
        except IndexError as e:
            count += n
    a_y = yprojection(imga)
    b_y = yprojection(imgb)
    for i, n in enumerate(a_y):
        try:
            count += abs(n - b_y[i])
        except IndexError as e:
            count += n
    x,y = imga.size
    return 1-count/2.0/(x*y)


def models_match(img):
    """
    return str, model name
    """
    counts = []
    models_path = os.path.join(HERE, 'models')
    filenames = filter(lambda n: n.endswith('png'), os.listdir(models_path))
    file_paths = map(lambda n: os.path.join(models_path, '%s' %n), filenames)
    for f in file_paths:
        model_img = Image.open(f)
        result = img_compare(img, model_img)
        if  result == 1.0: 
            return os.path.splitext(os.path.basename(f))[0]
        counts.append(result)
    else:
        index = counts.index(max(counts))
        return os.path.splitext(filenames[index])[0]


def gen_models():
    filenames = filter(lambda n: n.endswith('png'), os.listdir('models'))
    for f in filenames:
        name = os.path.splitext(f)[0]
        with open(os.path.join('models', '%s.txt' %name), 'w') as txt:
            img = Image.open('models/%s' %f)
            content = img2str(img)
            img.close()
            txt.write(content)

def find_threshold():
    """ compare threshold effect by manually
    """
    captcha = get_img(JZWJW_CAPTCHA_URL)
    for i in range(80,200):
        bin_captcha = binarization(captcha, i)
        bin_captcha.save(os.path.join('training','%s.png' %i ))
        bin_captcha.close()

def train():
    """ test for img_split
    """
    captcha = get_img(CAPTCHA_URL)
    bin_captcha = binarization(captcha, THRESHOLD)
    bin_captcha = minesweeper(bin_captcha)
    name = time.time()
    bin_captcha.save(os.path.join('training','%s.png' %name ))
    img_crop = img_split(bin_captcha)
    for i,img in enumerate(img_crop):
        img.save(os.path.join('training','%s-%s.png' %(name,i)))
    bin_captcha.close()


def hack_captcha(img, n=4):
    """ guess the captcha code, main to be used
    img: Image object
    n: char in the image
    return str
    """
    code = ''
    bin_captcha = binarization(img, THRESHOLD)
    bin_captcha = minesweeper(bin_captcha)
    for img in img_split(bin_captcha):
        code += models_match(img)
    return code[:n]


def main():
    """ test for hack_captcha()
    """
    count = 0
    for i in xrange(10):
        captcha = get_img(JZWJW_CAPTCHA_URL)
        captcha.show()
        print hack_captcha(captcha)
        r = raw_input('Y/N')
        if r == '\n':
            count += 1
    print count


if __name__ == '__main__':
    main()