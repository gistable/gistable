#!/usr/bin/env python

# NOTE : This script assumes that the aligments are in the src-tgt format

import optparse
import pprint
import sys
import numpy as np

optparser = optparse.OptionParser()
optparser.add_option("-s", "--source", dest="source", help="The source training corpus", default="data/ex.de")
optparser.add_option("-t", "--target", dest="target", help="The training training corpus", default="data/ex.en")
optparser.add_option("-a", "--align", dest="alignment", help="The alignment file", default="data/ex.align")
optparser.add_option("-o", "--output", dest="output", help="The output file", default="data/ex.output")
optparser.add_option("-v", "--verbose", dest="verbose", action="store_true", default=False,  help="Verbose mode (default=off)")
opts = optparser.parse_args()[0]


def bitmap(sequence):
  """ Generate a coverage bitmap for a sequence of indexes """
  return long(''.join([str(x) for x in sequence]),2)


def bitmap2str(b, n, on='1', off='0'):
  """ Generate a length-n string representation of bitmap b """
  return '' if n==0 else bitmap2str(b>>1, n-1, on, off) + (on if b&1==1 else off)


def extract(f_start, f_end, e_start, e_end, f, e, A, is_f_aligned):
  """
    Performs consistency check of the source and the target spans
    and then extracts phrases.
    Also extracts phrases where the target tokens are unaligned
  """
  # check if at least one alignment point exists
  if f_end < 0: return set()

  for (f_i, e_i) in A:
    # Check to see if alignment points violate consistency
    if f_start <= f_i and f_i <= f_end and (e_i < e_start or e_i > e_end):
      return set()

  E = set()
  f_s = f_start
  while True:
    f_e = f_end
    while True:
      E.add(((e_start, e_end), (f_s, f_e)))
      #E.add((" ".join(np.array(e)[range(e_start, e_end + 1)]),
            #" ".join(np.array(f)[range(f_s, f_e + 1)])))
      # The next portion of this loop is for the benefit of
      # unaligned tokens
      f_e += 1
      if f_e in is_f_aligned or f_e == len(f):
        break
    f_s -= 1
    if f_s in is_f_aligned or f_s < 0:
      break
  return E


# Source = e, Target = f
def getPhrasePairs(f, e, A, is_f_aligned):
  """
    Wrapper for the phrase extraction process
    Decides which spans correspond to phrase pairs
    Consistency check does is taken care of the
    `extract` method
  """
  BP = set()
  for e_start in range(len(e)):
    for e_end in range(e_start, len(e)):
      # find the minimally matching foreign phrase
      f_start = len(f) - 1
      f_end = -1
      for (f_i, e_i) in A:
        if e_start <= e_i and e_i <= e_end:
          f_start = min(f_i, f_start)
          f_end = max(f_i, f_end)
      # This set removes duplicates
      BP.update(extract(f_start, f_end, e_start, e_end, f, e, A, is_f_aligned))
  return BP


def monotoneCoverageVector(e, f, phraseDict, sentId):
  e_start = 0
  e_end = 0
  sourceCoverage = bitmap([0 for k in range(len(f))])
  while True:
    #print e_start, e_end
    if (e_start, e_end) in phraseDict:
      source_phrase_cands = []
      for (x,y) in phraseDict[(e_start, e_end)]:
        phraseCoverage = bitmap([1 if x <= k <= y else 0 for k in range(len(f))])
        if phraseCoverage & sourceCoverage == 0:
            source_phrase_cands.append((x,y))

      source_span = max(source_phrase_cands, key = lambda x: x[1] - x[0])
      phraseCoverage = bitmap([1 if source_span[0] <= k <= source_span[1] else 0 for k in range(len(f))])
      e_phrase = np.array(e)[range(e_start, e_end + 1)]
      f_phrase = np.array(f)[range(source_span[0], source_span[1] + 1)]
      sourceCoverage = sourceCoverage | phraseCoverage
      if opts.verbose:
          print " ".join(e_phrase), " ||| ", " ".join(f_phrase), " ||| ", bitmap2str(phraseCoverage, len(f)), " ||| ", bitmap2str(sourceCoverage, len(f))
      # Write coverage to output file
      output.write(str(sentId) + " ||| " + bitmap2str(sourceCoverage, len(f)) + "\n")
      e_end += 1
      e_start = e_end
    else:
      e_end += 1
    if e_end == len(e):
      break


with open(opts.source) as s:
  source_sentences = s.readlines()

with open(opts.target) as t:
  target_sentences = t.readlines()

source_sentences = [s.strip().split() for s in source_sentences]
target_sentences = [t.strip().split() for t in target_sentences]

output = open(opts.output, "w+")

# Now read alignments
with open(opts.alignment) as a:
  alignment = a.readlines()

alignment = [a.split() for a in alignment]
for a_i in range(len(alignment)):
  alignment[a_i] = [tuple(int(p) for p in a.split("-")) for a in alignment[a_i]]

sentId = -1
for (f, e, A) in zip(source_sentences, target_sentences, alignment):
  sentId += 1
  f_aligned = [x[0] for x in A]
  phrases = getPhrasePairs(f, e, A, f_aligned)
  # Convert to dictionary
  phraseDict = {}
  for (x, y) in phrases:
    if x not in phraseDict:
      phraseDict[x] = []
    phraseDict[x].append(y)

  monotoneCoverageVector(e, f, phraseDict, sentId)

output.close()
