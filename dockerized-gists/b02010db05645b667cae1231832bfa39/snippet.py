def foldl(zero, combine, elements):
    if callable(zero):
        result = zero()
    else:
        result = zero
    for x in elements:
        result = combine(result, x)
    return result

def foldr(zero, combine, elements):
  return foldl(zero, combine, reversed(elements))