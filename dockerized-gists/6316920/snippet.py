# This simple python utility crawls the current directory and finds all images.
# It will then search the directory for files using these images and also mark
# any xcode projects which include these images.
#
# Allowing you to easily find images which are no longer used (or even images
# included in xcode and not used).
#
# Usage, cd into your repository and then run:
#
#    curl https://gist.github.com/kylef/6316920/raw/images.py -# | python -
#
# Example output:
#     ==> PLVSendButton-background-normal wasn't found.
#     ==> PLVSendButton-background-selected wasn't found (in project).
#
# Please note, there may be false positives with image names which are generated
# in code. For example with a PNG sequence:
#
# - image-sequence-1.png
# - image-sequence-2.png
# - image-sequence-1.png
#
# When these are used with something like `[NSString stringWithFormat:@"image-sequence-%d.png"]`.
#
import os
import sys
import logging

logger = logging.getLogger(__name__)


def filewalk(directory):
    for filename in os.listdir(directory):
        fullpath = os.path.join(directory, filename)

        if not filename.startswith('.') and not os.path.islink(fullpath):
            if os.path.isdir(fullpath):
                for filename in filewalk(fullpath):
                    yield filename
            else:
                yield fullpath


if __name__ == '__main__':
    if '-v' in sys.argv:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)

    logger.addHandler(logging.StreamHandler())

    images = []

    for filename in filewalk('.'):
        if filename.endswith('.png') or filename.endswith('.jpeg') or filename.endswith('.jpg') or filename.endswith('.gif'):
            filename = os.path.basename(filename).lower()

            for string in ('.png', '@2x', '~ipad', '~iphone', '.jpeg', '.jpg', '.gif'):
                filename = filename.replace(string, '')

            filename = filename.strip()
            images.append(filename)

    images = set(images)  # we want distinct results

    logger.debug('\033[94m==> Found {} images.'.format(len(images)))

    for imagename in set(images):
        matches = []

        for filename in filewalk('.'):
            if filename.endswith('.png'):
                continue

            with open(filename, 'r') as f:
                for line in f.readlines():
                    if imagename in line.lower():
                        matches.append(filename)
                        break

        if len(matches) == 0:
            logger.info('\033[94m==> \033[91m{}\033[94m wasn\'t found.'.format(imagename.strip()))
        else:
            project_matches = 0

            for match in matches:
                if match.endswith('.pbxproj'):
                    project_matches += 1

            if len(matches) == project_matches:
                logger.info('\033[94m==> \033[91m{}\033[94m wasn\'t found (in project).'.format(imagename.strip()))


