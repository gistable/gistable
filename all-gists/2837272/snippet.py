#!/usr/bin/python

from collections import defaultdict

def slow(num_immortals):
  stack = [1 << x for x in range(num_immortals)]
  seen = []

  while stack:
    gene = stack.pop()
    for mate in seen:
      if not gene & mate:
        stack.append(gene | mate)
    seen.append(gene)

  return len(seen)

def fast(num_immortals):
  seen = defaultdict(int)
  queue = defaultdict(int)

  for x in range(num_immortals):
    queue[1 << x] = 1

  while queue:
    gene, count = queue.popitem()
    for mate, mate_count in seen.items():
      if not gene & mate:
        queue[gene | mate] += count * mate_count
    seen[gene] += count

  return sum(seen.values())