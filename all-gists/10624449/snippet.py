# To run, from shell type: python tweet_finder.py
# Must be run in the same directory as the downloaded csv file.

import csv

# Modify this number if you want a different nth Tweet
# Should be 1-based (i.e. first tweet is the 1th, not 0th)
num = 40000
# Change the path if you want to run it from a different directory
path = "tweets.csv"

with open(path, "r") as f:
  # [1:] to remove the header
  tweets = list(csv.reader(f))[1:]

if len(tweets) < num:
  print "There are less than %d tweets." % (num)
else:
  # Archive Format: Reverse chronological order. Last field is Tweet content.
  print tweets[-num][-1]