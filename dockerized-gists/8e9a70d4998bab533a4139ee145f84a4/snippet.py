import argparse
import sys

from mutagen.id3 import USLT
from mutagen.mp3 import MP3


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('MP3FILE')
    parser.add_argument('--lang', default='rus')
    parser.add_argument('--desc', default='')
    parser.add_argument('--input-encoding', default='utf-8')
    args = parser.parse_args()

    # Read lyrics from stdin
    text = sys.stdin.read().decode(args.input_encoding)
    # In Python 3 it should be::
    #
    #     text = sys.stdin.buffer.read().decode(args.input_encoding)

    audio = MP3(args.MP3FILE)
    if audio.tags is None:
        audio.add_tags()

    audio.tags.add(USLT(encoding=1, lang=args.lang, desc=args.desc, text=text))
    audio.save(v2_version=3)

if __name__ == '__main__':
    main()
