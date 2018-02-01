'''
Bunch of functions to do basic image similarity detection
See:
http://www.gossamer-threads.com/lists/python/python/901273
http://sourceforge.net/projects/imsim/?source=dlp
'''

from PIL import Image
from PIL import ImageStat


def row_column_histograms (file_name):
    '''Reduce the image to a 5x5 square of b/w brightness levels 0..3
    Return two brightness histograms across Y and X
    packed into a 10-item list of 4-item histograms.'''
    im = Image.open (file_name)
    im = im.convert ('L')       # convert to 8-bit b/w
    w, h = 300, 300
    im = im.resize ((w, h))
    imst = ImageStat.Stat (im)
    sr = imst.mean[0]   # average pixel level in layer 0
    sr_low, sr_mid, sr_high = (sr*2)/3, sr, (sr*4)/3

    def foo (t):
        if t < sr_low: return 0
        if t < sr_mid: return 1
        if t < sr_high: return 2
        return 3

    im = im.point (foo) # reduce to brightness levels 0..3
    yhist = [[0]*4 for i in xrange(5)]
    xhist = [[0]*4 for i in xrange(5)]
    for y in xrange (h):
        for x in xrange (w):
            k = im.getpixel ((x, y))
            yhist[y / 60][k] += 1
            xhist[x / 60][k] += 1
    return yhist + xhist


def difference_ranks (test_histogram, sample_histograms):
    '''Return a list of difference ranks between the test histograms and
    each of the samples.'''
    result = [0]*len (sample_histograms)
    for k, s in enumerate (sample_histograms):  # for each image
        for i in xrange(10):    # for each histogram slot
            for j in xrange(4): # for each brightness level
                result[k] += abs (s[i][j] - test_histogram[i][j])
    return result


if __name__ == '__main__':
    import getopt, sys
    opts, args = getopt.getopt (sys.argv[1:], '', [])
    if not args:
        args = [
            'bears1.jpg',
            'bears2.jpg',
        ]
        test_pic = 'bears0.jpg'
    else:
        test_pic, args = args[0], args[1:]

    z = [row_column_histograms (a) for a in args]
    test_z = row_column_histograms (test_pic)

    file_ranks = zip (difference_ranks (test_z, z), args)
    file_ranks.sort()

    print '%12s' % (test_pic,)
    print '--------------------'
    for r in file_ranks:
        print '%12s %7.2f' % (r[1], r[0] / 3600.0,)