#!/usr/bin/python -O

# partition A[p:r] in place about x, and return the final position of the pivot
def partition(A, p, r, x):
  # find the index of the pivot
  i = -1
  for j in range(p, r):
    if A[j] == x:
      i = j
      break

  # move the pivot to the end
  if i != -1:
    t = A[r - 1]
    A[r - 1] = A[i]
    A[i] = t

  # keep track of the end of the "less than" sublist
  store_index = p

  # iterate
  for j in range(p, r - 1):
    if A[j] < x:
      t = A[j]
      A[j] = A[store_index]
      A[store_index] = t
      store_index += 1

  # put the pivot in its final place
  if i != -1:
    t = A[r - 1]
    A[r - 1] = A[store_index]
    A[store_index] = t

  # return the store index
  return store_index

# find the ith biggest element in A[p:r]
def select(A, p, r, i):
  # make a copy of the array
  A = A[:]

  # divide the n elements of A into n / 5 groups
  groups = [[]] * (((r - p) + 4) / 5)
  for x in range(p, r):
    groups[(x - p) / 5] = groups[(x - p) / 5] + [A[x]]

  # find the median of each group
  medians = [sorted(l)[(len(l) - 1) / 2] for l in groups]

  # find the median of medians
  if len(medians) == 1:
    median_to_rule_them_all = medians[0]
  else:
    median_to_rule_them_all = select(medians, 0, len(medians), (len(medians) - 1) / 2)

  # partition A around the median of medians
  partition_index = partition(A, p, r, median_to_rule_them_all)

  # base case
  if p + i < partition_index:
    return select(A, p, partition_index, i)
  if p + i > partition_index:
    return select(A, partition_index + 1, r, p + i - partition_index - 1)
  return A[p + i]