#!/usr/bin/python

# This script unshreds a shredded image (visit http://bit.ly/sCMAD5 for details)
# author: Zoreslav Khimich <zoreslav.khimich@gmail.com>

from PIL import Image, ImageChops, ImageStat
from argparse import ArgumentParser
import sys, heapq

MAGIC_THRESHOLD = 11 # carefully handpicked to work with your reference input

# calculate per-channel image difference and binarize the result, returns image
def image_diff(edge1, edge2):
    diff = ImageChops.difference(edge1, edge2) # abs(edge1-edge2)
    return Image.eval(diff, lambda i: i>MAGIC_THRESHOLD and 1) # binarize

# heuristics based on aggregate per-pixel difference; returns score (larger score = more differences)
def edge_score(edge1, edge2):
    edge_sum_rgb = ImageStat.Stat(image_diff(edge1, edge2)).sum
    return sum(edge_sum_rgb) # R+G+B

# vertical blur (5px mean, used for filtering out high frequencies)
def vblur(image):
    const_ = Image.new(image.mode, image.size)
    o = (ImageChops.add(ImageChops.offset(image, 0, d), const_, scale=5) for d in range(-2, 3))
    return reduce(ImageChops.add, o)

# unshred an image given known column width; returns iterable of column indices
def find_sequence(image, col_width):
    width, height = image.size;
    cols = width / col_width

    # extract edges (1px strip from left & right side of each column)
    left_edges = []
    right_edges = []
    for i in range(cols):
        left_edges+=vblur(image.crop((i*col_width, 0, i*col_width+1, height))),
        right_edges+=vblur(image.crop(((i+1)*col_width-1, 0, (i+1)*col_width, height))),

    # precalc fitness scores for each column pair
    scores = []
    for i in range(cols):
        row = []
        for j in range(cols):
            if i == j:
                row += sys.maxint, # forget about i==j cases
                continue
            row += edge_score(left_edges[i], right_edges[j]),
        scores += row,

    # find the best column to start reconstruction from
    best_starter = -1
    bst_left_score = bst_right_score = sys.maxint
    for i in range(cols):
        loc_best_l = min(scores[i])
        loc_best_r = min(scores[j][i] for j in range(cols))
        if loc_best_l < bst_left_score and loc_best_r < bst_right_score:
            bst_left_score = loc_best_l
            bst_right_score = loc_best_r
            best_starter = i

    remain = range(cols)
    remain.remove(best_starter)
    result = [best_starter,]

    # rebuild the rest of the f-ng owl
    while remain:
        #uncomment to dump step by step vis to files:
        #reorder_shreds(image, result, col_width).save('%d.jpg'%len(result))
        left = result[0]
        right = result[-1]
        left_score, left_idx = min((scores[left][rem_i], rem_i) for rem_i in remain)
        right_score, right_idx = min((scores[rem_i][right], rem_i) for rem_i in remain)
        if left_score < right_score:
            # put left
            remain.remove(left_idx)
            result.insert(0, left_idx)
        else:
            # put right
            remain.remove(right_idx)
            result.append(right_idx)
    return result

# reorder columns /given sequence; returns new image
def reorder_shreds(image, new_order, col_width = None):
    result = Image.new(image.mode, image.size)
    width,height = image.size
    if not col_width: col_width = width/len(new_order)
    for i,j in enumerate(new_order):
        col = image.crop((j*col_width, 0, (j+1)*col_width, height))
        result.paste(col, (i*col_width, 0))
    return result

MAGIC_LINES_TO_CONSIDER = 5
# heuristics based on longest continuous diff (similar to edge_score, but used for autodetection)
def edge_line_score(l1, l2):
    e = image_diff(l1, l2)
    w,h = e.size
    d = e.getdata()
    counter = 0
    lines = []
    for v in d:
        if sum(v) == 0:
            if counter != 0:
                heapq.heappush(lines, counter)
                counter = 0
            continue
        counter+=1    
    return sum(heapq.nlargest(MAGIC_LINES_TO_CONSIDER, lines))

# autodetects column width, returns positive integer (pixels) or 0 if failed
def detect_shred_width(image):
    width,height = image.size
    possible_col_no = filter(lambda x: 0==width%x, range(4, width/4+1))
    
    # estimates score for col. number hypothesis, higher score = more likely
    def calc_score(cols):
        col_width = width/cols
        def line_score(x):
            l1 = image.crop((x, 0, x+1, height))
            l2 = image.crop((x-1, 0, x, height))
            return edge_line_score(l1, l2)
        l_scores = []
        for i in range(1, cols):
            pre_l, l, post_l = (line_score(col_width*i+d) for d in range(-1, 2))
            l_scores += l-(pre_l+post_l),
        return float(sum(l_scores)) / (cols-1)

    # estimate score for all legit col numbers
    scores = map(calc_score, possible_col_no)

    # if the actual strip width is 32px, then 64, 128 and 256 will most probably
    # get good score as well (same for 5, 10, 20, 40, etc)
    # the following section tries to solve this by looking for the biggest
    # column number with a (relatively) good score
    best_guess = 1
    best_score = 0
    for score, guess in sorted(zip(scores, possible_col_no), reverse=True):
        if score <= 0: continue
        if guess > best_guess:
            times = guess/best_guess
            if score * times > best_score:
                best_guess = guess
                best_score = score
    if best_score == 0:
    	return 0
    return width/best_guess

# read file, autodetect width if needed, unshred, save
def unshred(in_filename, out_filename, shred_width = None):
    image = Image.open(in_filename)    
    if not shred_width:
        shred_width = detect_shred_width(image)
        if not shred_width:
        	print "Autodetection failed, try -w flag"
        	return
        print "Autodetected strip width %dpx" % shred_width
    print "Unshredding..."
    sequence = find_sequence(image, shred_width)
    reorder_shreds(image, sequence).save(out_filename)
    print "Done => %s" % out_filename

# parse command line args
def main():
    parser = ArgumentParser(description="Unshred a shredded image")
    parser.add_argument('input_image')
    parser.add_argument('output_image')
    parser.add_argument('--strip_width', '-w', help="force strip width W px. (disables autodetect)", type=int, default=0)
    args = parser.parse_args()
    unshred(args.input_image, args.output_image, args.strip_width)

if __name__ == "__main__":
    main()
 