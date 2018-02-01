import builtins
import random

def word_list(filename):
  with open(filename) as fp:
    for l in fp:
      yield l.split()

def batch(generator, size):
  batch = []
  for l in generator:
    batch.append(l)
    if len(batch) == size:
      yield batch
      batch = []
  if batch:
    yield batch

def shuffled(generator, size):
  for b in batch(generator, size):
    random.shuffle(b)
    for l in b:
      yield l

def sorted(generator, size, key):
  for b in batch(generator, size):
    for l in builtins.sorted(b, key=key):
      yield l

