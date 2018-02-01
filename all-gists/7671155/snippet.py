def disjoint2(A, B, C):
  """Return True if there is no element common to all three lists."""
  for a in A:
    for b in B:
      if a == b:            # only check C if we found match from A and B
        for c in C:
          if a == c         # (and thus a == b == c)
            return False    # we found a common value
  return True               # if we reach this, sets are disjoint