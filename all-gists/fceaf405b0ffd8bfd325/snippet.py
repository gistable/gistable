#!/usr/bin/env python
import locale
import random
import re
import sys
from codecs import encode
from copy import copy
from optparse import OptionParser

EXIT_SUCCESS = 0
EXIT_ERROR = 1

punct_re = re.compile(r"(?!\w)(?!\s).")

DEFAULT_PASSWORD_COUNT = 1
DEFAULT_NUMBER_OF_WORDS = 4
DEFAULT_DICT_PATH = "/usr/share/dict/words"
DEFAULT_MIN = 4
DEFAULT_MAX = 6

EXCLUSIONS = [
    # (name, test)
    ("upper", lambda s: any(c for c in s if c.isupper())),
    ("numeric", lambda s: any(c for c in s if c.isdigit())),
    ("punct", lambda s: punct_re.search(s)),
    ]

UNITS = [ # (multiplier, name_singular, name_plural)
    (1, "second", "seconds"),
    (60, "minute", "minutes"),
    (60, "hour", "hours"),
    (24, "day", "days"),
    (365.24, "year", "years"),
    (10, "decade", "decades"),
    (10, "century", "centuries"),
    (10, "millenium", "millenia"),
    ]

rot13 = lambda s: encode(s, "rot-13")

def build_parser():
    parser = OptionParser()
    parser.add_option("-d", "--dict", "--dictionary",
        help="The default dictionary to use (default: %s)" % DEFAULT_DICT_PATH,
        action="store",
        dest="dictionary",
        metavar="FILE",
        default=DEFAULT_DICT_PATH,
        )
    parser.add_option("-x", "--exclude",
        help="A file containing (optionally ROT13'ed) words to exclude such as profanity",
        action="store",
        dest="exclude",
        metavar="FILE",
        default=None,
        )
    parser.add_option("-c", "--count",
        help="The number of passwords to output (default: %i)" % DEFAULT_PASSWORD_COUNT,
        action="store",
        type="int",
        dest="count",
        default=DEFAULT_PASSWORD_COUNT,
        )
    parser.add_option("-i", "-n",
        help="The number of words to output (default: %i)" % DEFAULT_NUMBER_OF_WORDS,
        action="store",
        type="int",
        dest="length",
        default=DEFAULT_NUMBER_OF_WORDS,
        )
    parser.add_option("--min", "--min-len", "--min-length",
        help="The minimum length of word to consider (default: %i)" % DEFAULT_MIN,
        action="store",
        type="int",
        dest="min",
        default=DEFAULT_MIN,
        )
    parser.add_option("--max", "--max-len", "--max-length",
        help="The maximum length of word to consider (default: %i)" % DEFAULT_MAX,
        action="store",
        type="int",
        dest="max",
        default=DEFAULT_MAX,
        )
    for name, test in EXCLUSIONS:
        parser.add_option("--include-%s" % name,
            help="Include words containing %s chars" % name,
            action="store_true",
            default=False,
            dest=name,
            )
    parser.add_option("-v", "--verbose",
        help="Report additional statistics",
        action="store_true",
        dest="verbose",
        default=False,
        )
    parser.add_option("-g", "--guesses-per-second", "--guesses", "--gps",
        help="Guesses per second (for additional statistics)",
        action="store",
        type="int",
        dest="guesses_per_second",
        default=1000,
        )
    return parser

def main():
    parser = build_parser()
    options, args = parser.parse_args()
    for test, desc in [
            (options.count < 1, "Count must be positive"),
            (options.length < 1, "Number of words must be positive"),
            (options.min < 1, "Minimum length must be positive"),
            (options.max < options.min, "Maximum length must not be less than the minimum"),
            ]:
        if test:
            sys.stderr.write("%s\n" % desc)
            parser.print_help()
            return EXIT_ERROR
    exclusions = set()
    if options.exclude:
        try:
            f = open(options.exclude)
        except IOError:
            sys.stderr.write("Unable to open exclusion file %s\n" % options.exclude)
        else:
            try:
                for word in f:
                    word = word.strip().lower()
                    exclusions.add(word)
                    exclusions.add(rot13(word))
            finally:
                f.close()
    try:
        f = open(options.dictionary)
    except IOError:
        sys.stderr.write("Unable to open %s\n" % options.dictionary)
        return EXIT_ERROR
    else:
        try:
            word_list = []
            for word in f:
                word = word.rstrip() # get rid of the newline
                if word in exclusions: continue
                if options.min <= len(word) <= options.max:
                    # it's of the right length
                    for attr, exclusion_test in EXCLUSIONS:
                        if not getattr(options, attr):
                            if exclusion_test(word):
                                break
                    else:
                        word_list.append(word)
        finally:
            f.close()
        for i in range(options.count):
            result = " ".join(random.sample(word_list, options.length))
            print(result)
        if options.verbose:
            possibilities = len(word_list) ** options.length
            print("%i word dictionary, %i word(s) = %i possible" % (
                len(word_list),
                options.length,
                possibilities,
                ))
            seconds = possibilities / float(options.guesses_per_second)
            last_multiplier, last_name1, last_name_pl = UNITS[0]
            current_multiplier = last_multiplier
            for multiplier, name1, name_pl in UNITS:
                current_multiplier *= multiplier
                if current_multiplier > seconds:
                    break
                last_multiplier = current_multiplier
                last_name1 = name1
                last_name_pl = name_pl
            if options.guesses_per_second == 1:
                guess = "guess"
            else:
                guess = "guesses"
            dur = seconds / last_multiplier
            if abs(dur - 1.0) < 0.01: # arbitrary EPSILON
                last_name = last_name1
            else:
                last_name = last_name_pl
            print("%0.1f %s at %i %s per second" % (
                dur,
                last_name,
                options.guesses_per_second,
                guess,
                ))

    return EXIT_SUCCESS

if __name__ == "__main__":
    sys.exit(main())
