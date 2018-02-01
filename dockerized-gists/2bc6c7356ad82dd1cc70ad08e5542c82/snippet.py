import sys, os
import logging
import re

ALREADY_SKIPPED_COMMENTS_IN_BEGINNING = False
REVIEW_VIDEO_ID = None


ERROR_TABLE = {
    # ERROR_CODE: ERROR_MESSAGE
    -1: "found an unexpected commented line",
    -100: "too few fields (comma-separated)",
    -200: "found a different video id (there should be only one)",
    -300: "found a bad caption id",
    -400: "found a bad grammar assessment",
    -500: "found a bad precision aseessment"
}

def print_usage():
    print("Usage: python %s <YOUR_ID.txt>" % (__file__))

def check_line(line):
    global ALREADY_SKIPPED_COMMENTS_IN_BEGINNING, REVIEW_VIDEO_ID
    if line.startswith('#'):
        # it's a commented line
        if ALREADY_SKIPPED_COMMENTS_IN_BEGINNING:
            return -1
        return 0
    else:
        # it's a normal line
        ALREADY_SKIPPED_COMMENTS_IN_BEGINNING = True
        tokens = line.strip().split(',')
        if len(tokens) < 5:
            return -100
        # extract fields
        video_id   = tokens[0]
        caption_id = tokens[1]
        caption    = tokens[2:-2] # just in case the caption contains comma
        grammar    = tokens[-2]
        precision  = tokens[-1]
        # check the fields
        # 1) check video id
        if REVIEW_VIDEO_ID == None:
            REVIEW_VIDEO_ID = video_id
        if video_id != REVIEW_VIDEO_ID:
            return -200
        # 2) check caption id
        try:
            pattern = re.compile(r'^[0-9]+$')
            re.match(pattern, caption_id).span() == (0, len(caption_id))
        except:
            return -300
        # 3) check grammar
        if not grammar in ["1", "2", "3", "4", "5"]:
            return -400
        # 4) check precision
        if not precision in ["1", "2", "3", "4", "5"]:
            return -500
        return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    #
    # check argument
    #
    if len(sys.argv) != 2 or not os.path.exists(sys.argv[1]):
        print_usage()
        sys.exit()
    #
    # open file and then check
    #
    with open(sys.argv[1], 'r') as f:
        for lineNum, line in enumerate(f):
            res = check_line(line)
            if res != 0:
                logging.error('line %d: %s' % (lineNum + 1, ERROR_TABLE[res]))
    print('finished checking.')
