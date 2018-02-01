# -*- coding: utf-8 -*-
import csv
import codecs, cStringIO
from argparse import ArgumentParser

from monkeylearn import MonkeyLearn


class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")

class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def writerow(self, row):
        self.writer.writerow([s.encode("utf-8") for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data)
        # empty queue
        self.queue.truncate(0)

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


def parse_args():
    parser = ArgumentParser()
    parser.add_argument(
        '-s',
        '--samples',
        help='Number of samples to keep.',
        type=int,
        metavar='samples'
    )
    parser.add_argument(
        '-c',
        '--col',
        help='Column to use',
        type=int,
        default=0,
        metavar='col'
    )
    parser.add_argument(
        '-k',
        '--keywords',
        help='Number of keywords to extract.',
        type=int,
        default=10,
        metavar='keywords'
    )
    parser.add_argument(
        '-t',
        '--token',
        help='Your MonkeyLearn API token.',
        type=str,
        metavar='token'
    )
    parser.add_argument(
        'file_path',
        help='Input csv file to process.',
        metavar='path'
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    f = open(args.file_path)
    reader = UnicodeReader(f)

    MAX_SAMPLES = args.samples
    COL = args.col
    MAX_KEYWORDS = args.keywords
    API_TOKEN = args.token
    text = ''

    print "Reading data..."
    for i, row in enumerate(reader):
        text += row[COL]
        if i + 1 == MAX_SAMPLES:
            break

    print "Extracting keywords..."
    ml = MonkeyLearn(API_TOKEN)
    res = ml.extractors.extract('ex_y7BPYzNG', [text], max_keywords=MAX_KEYWORDS)

    for item in res.result[0]:
        print item['keyword']

    f.close()
