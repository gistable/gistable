"""Example to compute word frequency using simple map/reduce utility from openlibrary.

https://github.com/internetarchive/openlibrary/tree/master/openlibrary/data/mapreduce.py
"""
import sys
import logging
from openlibrary.data import mapreduce

class WordFrequecy(mapreduce.Task):
    def map(self, key, value):
        words = value.split()
        for w in words:
            yield w, ""

    def reduce(self, key, values):
        return key, sum(1 for v in values)
    
def read_files(filenames):
    for filename in filenames:
		for line in open(filename):
			yield line

def main():
	logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")

	lines = read_files(sys.argv[1:])
	records = enumerate(lines)

	task = WordFrequecy()
	for w, count in task.process(records):
		print w, count

if __name__ == "__main__":
	main()