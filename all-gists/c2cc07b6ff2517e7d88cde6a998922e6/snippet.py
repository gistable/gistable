import functools
import time

def timetrace(func):
  @functools.wraps(func)
  def _wrapper(*args, **kwargs):
    start = time.time()
    results = func(*args, **kwargs)
    end = time.time()
    print(f'Took {end - start} sec')
    return results
  return _wrapper

@timetrace
def gcd(pair):
  x, y = pair
  low = min(x, y)
  
  for i in range(low, 0, -1):
    if x % i == 0 and y % i == 0:
      return i
    
if __name__ == '__main__':
  import concurrent
  
  numbers = [
    (1963309, 2265973),
    (2030677, 3814172),
    (1551645, 2229620),
    (2039045, 2020802)
  ]
  
  pool = concurrent.futures.ProcessPoolExecutor(max_workers=4)
  results = list(pool.map(gcd, numbers))