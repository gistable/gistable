#!/usr/bin/python -O

################################################################################
################################################################################
#
# State-Based Text Merging Algorithm
# For 6.033 Design Project 2
# TA: Katherine Fang
# 9 May 2012
#
# Stephan Boyer
# Ami Patel
# Vo Thanh Minh Tue
#
# Description:
#
#   Attempts to automatically perform a three-way merge.
#   Prints the result to standard output.
#
#   This is a proof of concept.  In a real system, we would
#   write at least the diff algorithm in a faster language.
#   This implementation quickly slows down for large files,
#   unless the fast diff approximation is used (see below).
#
#   For more information, see:
#     http://www.stephanboyer.com/post/26/3-way-text-merging-algorithm
#
# Usage:
#
#   merger.py ancestor_file alice_file bob_file
#
################################################################################
################################################################################

################################################################################
################################################################################
# String Diffing
################################################################################
################################################################################

# represents a change from one string to another
class Change:
  pass

# represents adding <text> to string b
class Insert(Change):
  def __init__(self, text, pos_a, range_b):
    self.text = text
    self.pos_a = pos_a
    self.range_b = range_b
  def __repr__(self):
    return "Insert(\"" + str(self.text) + "\", " + str(self.pos_a) + ", " + str(self.range_b) + ")"

# represents deleting <text> from string b
class Delete(Change):
  def __init__(self, text, range_a, pos_b):
    self.text = text
    self.range_a = range_a
    self.pos_b = pos_b
  def __repr__(self):
    return "Delete(\"" + str(self.text) + "\", " + str(self.range_a) + ", " + str(self.pos_b) + ")"

# takes 2 indexable objects (e.g. strings or lists)
# returns a list of Change objects (Delete or Insert)
# guaranteed to produce an optimal diff
def str_diff(a, b):
  ls = len(a)
  lf = len(b)
  memo = {}
  def min_diff(si, fi):
    if (si, fi) in memo:
      return memo[(si, fi)]
    ans = []
    if si == ls and fi == lf:
      ans = []
    elif si < ls and fi == lf:
      ans = []
      for i in range(si, ls):
        ans.append((i, "d"))
    elif fi < lf and si == ls:
      ans = []
      for j in range(fi, lf):
        ans.append((si, "i", b[j]))
    elif  a[si] == b[fi]:
      ans = min_diff(si + 1, fi + 1)
    else:
      alts = [(min_diff(si + 1, fi), (si, "d")), (min_diff(si, fi + 1), (si, "i", b[fi]))]
      best = min(alts, key=lambda t: len(t[0]))
      ans = [best[1]] + best[0]
    memo[(si, fi)] = ans
    return ans
  diff = sorted(min_diff(0, 0), key=lambda x: x[0])
  changes = []
  pos_diff = 0
  offset_b = 0
  while pos_diff < len(diff):
    length = 0
    pos_a_old = diff[pos_diff][0]
    while pos_diff < len(diff) and diff[pos_diff][1] == "i":
      if diff[pos_diff][0] != pos_a_old:
        break
      length +=  1
      pos_diff +=  1
    if length > 0:
      pos_a = pos_a_old
      range_b_0 = pos_a_old + offset_b
      range_b_1 = pos_a_old + offset_b + length
      changes.append(Insert(b[range_b_0:range_b_1], pos_a, (range_b_0, range_b_1)))
      offset_b +=  length
    if pos_diff >= len(diff):
      break
    length = 0
    pos_a_old = diff[pos_diff][0]
    while pos_diff < len(diff) and diff[pos_diff][1] == "d":
      if diff[pos_diff][0] != pos_a_old + length:
        break
      length +=  1
      pos_diff +=  1
    if length > 0:
      range_a_0 = pos_a_old
      range_a_1 = pos_a_old + length
      pos_b = pos_a_old + offset_b
      changes.append(Delete(a[range_a_0:range_a_1], (range_a_0, range_a_1), pos_b))
      offset_b -=  length
  return changes

"""

# Here is an alternative version of the str_diff(a, b) function.
# Unlike the version above, it is NOT guaranteed to produce optimal
# diffs.  Diffs that are not optimal can sometimes produce unexpected
# results.  However, this version is much faster.

import difflib

# takes 2 indexable objects (e.g. strings or lists)
# returns a list of Change objects (Delete or Insert)
# not guaranteed to produce an optimal diff
def str_diff(a, b):
  d = difflib.Differ()
  diff = list(d.compare(a, b))
  changes = []
  pos_a = 0
  pos_b = 0
  pos_diff = 0
  while pos_diff < len(diff):
    while pos_diff < len(diff) and diff[pos_diff][0] == " ":
      pos_diff +=  1
      pos_a +=  1
      pos_b +=  1
    while pos_diff < len(diff) and diff[pos_diff][0] == "?":
      pos_diff +=  1
    length = 0
    range_b_0 = pos_b
    while pos_diff < len(diff) and diff[pos_diff][0] == "+":
      length +=  1
      pos_diff +=  1
      pos_b +=  1
    if length > 0:
      changes.append(Insert(b[range_b_0:pos_b], pos_a, (range_b_0, pos_b)))
    text = []
    range_a_0 = pos_a
    while pos_diff < len(diff) and diff[pos_diff][0] == "-":
      length +=  1
      pos_diff +=  1
      pos_a +=  1
    if length > 0:
      changes.append(Delete(a[range_a_0:pos_a], (range_a_0, pos_a), pos_b))
  return changes

"""

################################################################################
################################################################################
# Levenshtein Distance
################################################################################
################################################################################

# compute the Levenshtein distance between two strings
def levenshtein(a, b):
  d = {}
  for i in range(len(a) + 1):
    d[(i, 0)] = i
  for j in range(len(b) + 1):
    d[(0, j)] = j
  for j in range(1, len(b) + 1):
    for i in range(1, len(a) + 1):
      if a[i - 1] == b[j - 1]:
        d[(i, j)] = d[(i - 1, j - 1)]
      else:
        d[(i, j)] = min([d[(i - 1, j)], d[(i, j - 1)], d[(i - 1, j - 1)]]) + 1
  return d[len(a), len(b)]

################################################################################
################################################################################
# Finding Move Actions
################################################################################
################################################################################

# the maximum normalized distance (0-1) between two strings for them to be considered the same
# for the purposes of finding Move actions
MAX_MOVE_DIST = 0.2

# the minimum number of items that can be considered a Move action
MIN_MOVE_LENGTH = 10

# represents moving <text_a> in range <range_a> to <text_b> in range <range_b>
class Move(Change):
  def __init__(self, text_a, range_a, pos_a, text_b, range_b, pos_b, first):
    self.text_a = text_a
    self.range_a = range_a
    self.pos_a = pos_a
    self.text_b = text_b
    self.range_b = range_b
    self.pos_b = pos_b
    self.first = first
  def __repr__(self):
    return "Move(\"" + str(self.text_a) + "\", " + str(self.range_a) + ", " + str(self.pos_a) + ", \"" + str(self.text_b) + "\", " + str(self.range_b) + ", " + str(self.pos_b) + ", " + str(self.first) + ")"

# find Move actions in a list of Change objects (mutates the input list).
# a Move action comes from an Insert-Delete pair where the strings differ
# by less than MAX_MOVE_DIST in terms of normalized Levenshtein distance
def find_moves(diff, first):
  indices_to_delete = []
  for i in range(len(diff)):
    if isinstance(diff[i], Delete):
      for j in range(len(diff)):
        if isinstance(diff[j], Insert):
          if not (i in indices_to_delete) and not (j in indices_to_delete):
            normalized_dist = float(levenshtein(diff[i].text, diff[j].text)) / max(len(diff[i].text), len(diff[j].text))
            if normalized_dist <= MAX_MOVE_DIST and max(len(diff[i].text), len(diff[j].text)) >= MIN_MOVE_LENGTH:
              indices_to_delete.append(i)
              indices_to_delete.append(j)
              diff.append(Move(diff[i].text, diff[i].range_a, diff[j].pos_a, diff[j].text, diff[j].range_b, diff[i].pos_b, first))
  indices_to_delete.sort()
  indices_to_delete.reverse()
  for i in indices_to_delete:
    diff.pop(i)

################################################################################
################################################################################
# Text Merging
################################################################################
################################################################################

# represents a list of merge conflicts
class MergeConflictList(Exception):
  def __init__(self, conflicts):
    self.conflicts = conflicts
  def __repr__(self):
    return self.conflicts

# takes indexable objects (e.g. strings or lists) a, b and their common ancestor
# returns the merged document
def merge(ancestor, a, b):
  # compute the diffs from the common ancestor
  diff_a = str_diff(ancestor, a)
  diff_b = str_diff(ancestor, b)

  # find Move actions
  find_moves(diff_a, True)
  find_moves(diff_b, False)

  # find conflicts and automatically resolve them where possible
  conflicts = []
  indices_to_delete_a = []
  indices_to_delete_b = []
  len_diff_a = len(diff_a)
  len_diff_b = len(diff_b)
  for i in range(len_diff_a):
    for j in range(len_diff_b):
      if j in indices_to_delete_b:
        continue
      if isinstance(diff_a[i], Delete) and isinstance(diff_b[j], Delete):
        # if two Delete actions overlap, take the union of their ranges
        if (diff_b[j].range_a[0] >= diff_a[i].range_a[0] and diff_b[j].range_a[0] < diff_a[i].range_a[1])  or \
           (diff_b[j].range_a[1] >= diff_a[i].range_a[0] and diff_b[j].range_a[1] < diff_a[i].range_a[1])  or \
           (diff_b[j].range_a[0] < diff_a[i].range_a[0]  and diff_b[j].range_a[1] > diff_a[i].range_a[1]):
          diff_a[i].range_a = (min(diff_a[i].range_a[0], diff_b[j].range_a[0]), max(diff_a[i].range_a[1], diff_b[j].range_a[1]))
          indices_to_delete_b.append(j)
      if isinstance(diff_a[i], Delete) and isinstance(diff_b[j], Insert):
        # Insert actions inside the range of Delete actions collide
        if diff_b[j].pos_a > diff_a[i].range_a[0] and diff_b[j].pos_a < diff_a[i].range_a[1]:
          conflicts.append("A is deleting text that B is inserting into.")
      if isinstance(diff_a[i], Delete) and isinstance(diff_b[j], Move):
        # Delete actions that overlap with but are not fully contained within PsuedoMove sources collide
        if diff_a[i].range_a[0] >= diff_b[j].range_a[0] and diff_a[i].range_a[1] <= diff_b[j].range_a[1]:
          pass
        elif diff_a[i].range_a[0] >= diff_b[j].range_a[0] and diff_a[i].range_a[0] < diff_b[j].range_a[1]:
          conflicts.append("B is moving only part of some text that A is deleting.")
        elif diff_a[i].range_a[1] >= diff_b[j].range_a[0] and diff_a[i].range_a[1] < diff_b[j].range_a[1]:
          conflicts.append("B is moving only part of some text that A is deleting.")
        elif diff_a[i].range_a[0] < diff_b[j].range_a[0] and diff_a[i].range_a[1] > diff_b[j].range_a[1]:
          conflicts.append("A is deleting text that B is moving.")
        # Move destinations inside the range of Delete actions collide
        if diff_b[j].pos_a > diff_a[i].range_a[0] and diff_b[j].pos_a < diff_a[i].range_a[1]:
          conflicts.append("A is deleting text that B is moving text into.")
      if isinstance(diff_a[i], Insert) and isinstance(diff_b[j], Delete):
        # Insert actions inside the range of Delete actions collide
        if diff_a[i].pos_a > diff_b[j].range_a[0] and diff_a[i].pos_a < diff_b[j].range_a[1]:
          conflicts.append("B is deleting text that A is inserting into.")
      if isinstance(diff_a[i], Insert) and isinstance(diff_b[j], Insert):
        # Insert actions at the same position collide unless the inserted text is the same
        if diff_a[i].pos_a == diff_b[j].pos_a:
          if diff_a[i].text == diff_b[j].text:
            indices_to_delete_b.append(j)
          else:
            conflicts.append("A and B are inserting text at the same location.")
      if isinstance(diff_a[i], Insert) and isinstance(diff_b[j], Move):
        # Insert actions at the same location as Move destinations collide unless the text is the same
        if diff_a[i].pos_a == diff_b[j].pos_a:
          if diff_a[i].text == diff_b[j].text_b:
            indices_to_delete_a.append(i)
          else:
            conflicts.append("A is inserting text at the same location that B is moving text to.")
      if isinstance(diff_a[i], Move) and isinstance(diff_b[j], Delete):
        # Delete actions that overlap with but are not fully contained within PsuedoMove actions collide
        if diff_b[j].range_a[0] >= diff_a[i].range_a[0] and diff_b[j].range_a[1] <= diff_a[i].range_a[1]:
          pass
        elif diff_b[j].range_a[0] >= diff_a[i].range_a[0] and diff_b[j].range_a[0] < diff_a[i].range_a[1]:
          conflicts.append("A is moving only part of some text that B is deleting.")
        elif diff_b[j].range_a[1] >= diff_a[i].range_a[0] and diff_b[j].range_a[1] < diff_a[i].range_a[1]:
          conflicts.append("A is moving only part of some text that B is deleting.")
        elif diff_b[j].range_a[0] < diff_a[i].range_a[0] and diff_b[j].range_a[1] > diff_a[i].range_a[1]:
          conflicts.append("B is deleting text that A is moving.")
      if isinstance(diff_a[i], Move) and isinstance(diff_b[j], Insert):
        # Insert actions at the same location as Move destinations collide unless the text is the same
        if diff_b[j].pos_a == diff_a[i].pos_a:
          if diff_b[j].text == diff_a[i].text_b:
            indices_to_delete_b.append(j)
          else:
            conflicts.append("B is inserting text at the same location that A is moving text to.")
      if isinstance(diff_a[i], Move) and isinstance(diff_b[j], Move):
        # PsuedoMove actions collide if their source ranges overlap unless one is fully contained in the other
        if diff_b[j].range_a[0] >= diff_a[i].range_a[0] and diff_b[j].range_a[1] <= diff_a[i].range_a[1]:
          pass
        elif diff_b[j].range_a[0] >= diff_a[i].range_a[0] and diff_b[j].range_a[0] < diff_a[i].range_a[1]:
          conflicts.append("A text move by A overlaps with a text move by B.")
        elif diff_b[j].range_a[1] >= diff_a[i].range_a[0] and diff_b[j].range_a[1] < diff_a[i].range_a[1]:
          conflicts.append("A text move by A overlaps with a text move by B.")
        elif diff_b[j].range_a[0] < diff_a[i].range_a[0] and diff_b[j].range_a[1] > diff_a[i].range_a[1]:
          pass
        # Move actions collide if their destination positions are the same
        if diff_a[i].pos_a == diff_b[j].pos_a:
          conflicts.append("A and B are moving text to the same location.")
  indices_to_delete_a.sort()
  indices_to_delete_a.reverse()
  for i in indices_to_delete_a:
    diff_a.pop(i)
  indices_to_delete_b.sort()
  indices_to_delete_b.reverse()
  for i in indices_to_delete_b:
    diff_b.pop(i)

  # throw an error if there are conflicts
  if len(conflicts) > 0:
    raise MergeConflictList(conflicts)

  # sort the actions by position in the common ancestor
  def sort_key(action):
    if isinstance(action, Delete):
      return action.range_a[0]
    if isinstance(action, Insert):
      return action.pos_a
  actions = sorted(diff_a + diff_b, key=sort_key)

  # compute offset lists
  offset_changes_ab = []
  for i in range(len(actions)):
    if isinstance(actions[i], Delete):
      offset_changes_ab.append((actions[i].range_a[0], actions[i].range_a[0] - actions[i].range_a[1]))
    if isinstance(actions[i], Insert):
      offset_changes_ab.append((actions[i].pos_a, len(actions[i].text)))
  offset_changes_a = []
  for i in range(len(diff_a)):
    if isinstance(diff_a[i], Delete):
      offset_changes_a.append((diff_a[i].range_a[0], diff_a[i].range_a[0] - diff_a[i].range_a[1]))
    if isinstance(diff_a[i], Insert):
      offset_changes_a.append((diff_a[i].pos_a, len(diff_a[i].text)))
    if isinstance(diff_a[i], Move):
      offset_changes_a.append((diff_a[i].range_a[0], diff_a[i].range_a[0] - diff_a[i].range_a[1]))
      offset_changes_a.append((diff_a[i].pos_a, len(diff_a[i].text_a)))
  offset_changes_b = []
  for i in range(len(diff_b)):
    if isinstance(diff_b[i], Delete):
      offset_changes_b.append((diff_b[i].range_a[0], diff_b[i].range_a[0] - diff_b[i].range_a[1]))
    if isinstance(diff_b[i], Insert):
      offset_changes_b.append((diff_b[i].pos_a, len(diff_b[i].text)))
    if isinstance(diff_b[i], Move):
      offset_changes_b.append((diff_b[i].range_a[0], diff_b[i].range_a[0] - diff_b[i].range_a[1]))
      offset_changes_b.append((diff_b[i].pos_a, len(diff_b[i].text_a)))

  # compute the preliminary merge
  preliminary_merge = ancestor[:]
  pos_offset = 0
  for i in range(len(actions)):
    if isinstance(actions[i], Delete):
      preliminary_merge = preliminary_merge[:actions[i].range_a[0] + pos_offset] + preliminary_merge[actions[i].range_a[1] + pos_offset:]
      pos_offset +=  actions[i].range_a[0] - actions[i].range_a[1]
      offset_changes_ab.append((actions[i].range_a[0], actions[i].range_a[0] - actions[i].range_a[1]))
    if isinstance(actions[i], Insert):
      preliminary_merge = preliminary_merge[:actions[i].pos_a + pos_offset] + actions[i].text + preliminary_merge[actions[i].pos_a + pos_offset:]
      pos_offset +=  len(actions[i].text)
      offset_changes_ab.append((actions[i].pos_a, len(actions[i].text)))

  # perform the "delete" part of the moves
  for i in range(len(actions)):
    if isinstance(actions[i], Move):
      range_a0 = actions[i].range_a[0]
      range_a1 = actions[i].range_a[1]
      for offset_pair in offset_changes_ab:
        if offset_pair[0] <= actions[i].range_a[0]:
          range_a0 +=  offset_pair[1]
        if offset_pair[0] <= actions[i].range_a[1]:
          range_a1 +=  offset_pair[1]
      offset_changes_ab.append((actions[i].range_a[0], actions[i].range_a[0] - actions[i].range_a[1]))
      preliminary_merge = preliminary_merge[:range_a0] + preliminary_merge[range_a1:]

  # perform the "add" part of the moves
  for i in range(len(actions)):
    if isinstance(actions[i], Move):
      pos_a = actions[i].pos_a
      for offset_pair in offset_changes_ab:
        if offset_pair[0] <= actions[i].pos_a:
          pos_a +=  offset_pair[1]
      text_ancestor = actions[i].text_a
      if actions[i].first:
        text_a = actions[i].text_b
        range_a0 = actions[i].range_a[0]
        range_a1 = actions[i].range_a[1]
        for offset_pair in offset_changes_b:
          if offset_pair[0] <= actions[i].range_a[0]:
            range_a0 +=  offset_pair[1]
          if offset_pair[0] <= actions[i].range_a[1]:
            range_a1 +=  offset_pair[1]
        text_b = b[range_a0:range_a1]
      else:
        text_b = actions[i].text_b
        range_a0 = actions[i].range_a[0]
        range_a1 = actions[i].range_a[1]
        for offset_pair in offset_changes_a:
          if offset_pair[0] <= actions[i].range_a[0]:
            range_a0 +=  offset_pair[1]
          if offset_pair[0] <= actions[i].range_a[1]:
            range_a1 +=  offset_pair[1]
        text_a = a[range_a0:range_a1]
      text = merge(text_a, text_b, text_ancestor)
      offset_changes_ab.append((actions[i].pos_a, len(text)))
      preliminary_merge = preliminary_merge[:pos_a] + text + preliminary_merge[pos_a:]
  return preliminary_merge

################################################################################
################################################################################
# Demo
################################################################################
################################################################################

import sys

# split a string by spaces / newlines, but unlike the built-in split function,
# we want to preserve the separators so we can reconstruct the document
# afterward.  to do this, we treat whitespace characters as words.
def smart_split(s):
  result = []
  was_word = False
  for i in range(len(s)):
    if s[i] == " " or s[i] == "\n" or s[i] == "\r" or s[i] == "\t":
      was_word = False
      result.append(s[i])
    else:
      if not was_word:
        result.append("")
        was_word = True
      result[-1] +=  s[i]
  return result

# check the number of arguments
if len(sys.argv) != 4:
  print ""
  print "State-Based Text Merging Algorithm"
  print "For 6.033 Design Project 2"
  print "TA: Katherine Fang"
  print "9 May 2012"
  print ""
  print "Stephan Boyer"
  print "Ami Patel"
  print "Vo Thanh Minh Tue"
  print ""
  print "Description:"
  print ""
  print "  Attempts to automatically perform a three-way merge."
  print "  Prints the result to standard output."
  print ""
  print "Usage:"
  print ""
  print "   merger.py ancestor_file alice_file bob_file"
  print ""
  exit(0)

# open files a, b, and c (a is the common ancestor)
try:
  # note that the merge(ancestor, a, b) function will work on any
  # "list - like" object, including strings and lists. instead of
  # merging the raw strings of characters, we choose to split the
  # text into words and do the merge on that granularity.  this
  # gives more intuitive results.
  a = smart_split(open(sys.argv[1], "r").read())
  c = smart_split(open(sys.argv[2], "r").read())
  b = smart_split(open(sys.argv[3], "r").read())
except:
  print "error:  unable to one or more open input files"
  exit(0)

# try to merge
try:
  # since we merged lists of words rather than the raw strings, we
  # need to join the words back into a string for nice printing
  print "".join(merge(a, b, c))

# report any conflicts
except MergeConflictList as mc:
  for c in mc.conflicts:
    print "conflict:  " + str(c)
