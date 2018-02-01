def merge_range_sorted(r):
  """Merges and sorts a range of numbers. Used for block merging.

  Worse-case runtime:
    O(n)

  Args:
    r: A **sorted**, from low to high, list of ranges in a tuple format.

  Returns:
    A list of ranges in the tuple format with the all overlaps merged. This list
    will be sorted as well.
  """
  if len(r) == 0:
    return []
  d = [r[0]]

  last_index = 0
  for i, rangee in enumerate(r):
    start, end = rangee
    if start > d[last_index][1]:
      last_index += 1
      d.append((start, end))
      continue

    if end > d[last_index][1]:
      d[last_index] = (d[last_index][0], end)
  return d


if __name__ == "__main__":
  print merge_range_sorted([(1, 2), (1, 5), (2, 5), (3, 10), (5, 6), (11, 14), (16, 17), (16, 19), (21, 23)])

# Some unittesting below.. but not completed as this is not a part of this really. Public domain anyway.
#class TestMergeRange(unittest.TestCase):
#  def test_merge_range(self):
#    r = [(0, 1), (2.5, 3), (3, 4), (4, 5)]
#    self.assertEquals([(0, 1), (2.5, 5)], merge_range_sorted(r))
#
#    r = [(0, 20), (2, 3), (3, 4), (10, 15)]
#    self.assertEquals([(0, 20)], merge_range_sorted(r))
#
#    r = [(1, 2), (1, 5), (2, 5), (3, 10), (5, 6), (11, 14), (16, 17), (16, 19), (21, 23)]
#    self.assertEquals([(1, 10), (11, 14), (16, 19), (21, 23)], merge_range_sorted(r))
#
#  def test_merge_range_datetime(self):
#    r = [
#      (datetime(2013, 3, 27, 18, 0, 0), datetime(2013, 3, 27, 19, 0, 0)),
#      (datetime(2013, 3, 27, 19, 0, 0), datetime(2013, 3, 27, 22, 0, 0)),
#      (datetime(2013, 3, 27, 21, 0, 0), datetime(2013, 3, 27, 22, 0, 0)),
#      (datetime(2013, 3, 27, 23, 0, 0), datetime(2013, 3, 28, 0, 0, 0)),
#    ]
#
#    self.assertEquals([(datetime(2013, 3, 27, 18, 0, 0), datetime(2013, 3, 27, 22, 0, 0)), (datetime(2013, 3, 27, 23, 0, 0), datetime(2013, 3, 28, 0, 0, 0))], merge_range_sorted(r))


from bisect import bisect
def merge_range_sorted_average_logn(r): # not proven. Initial tests with the test cases above shows that this is **slower**
  if len(r) == 0:
    return []
  d = [r[0]]
  current_min_index = 0
  running = True
  current_min_boundary, current_max_boundary = r[0]
  while running:
    i = bisect(r, (current_min_boundary, current_max_boundary), current_min_index)
    if i >= len(r):
      running = False
      i -= 1

    lower, higher = r[i]
    if lower > current_max_boundary:
      d.append((lower, higher))
      current_min_boundary, current_max_boundary = d[-1]
    else:
      if higher > current_max_boundary:
        d[-1] = (d[-1][0], higher)
        current_max_boundary = higher

    current_min_index = i+1

  return d