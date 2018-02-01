import random
import time

stop = 100000
difference_count = 10000
all_keys = range(stop)
random.shuffle(all_keys)
diff_keys = [random.randint(0, stop) for i in range(difference_count)]

s = time.time()
allowed_keys = [key for key in all_keys if key not in diff_keys]
e = time.time()
print(e - s)
# => ~15.11s

s = time.time()
allowed_keys = list(set(all_keys).difference(diff_keys))
e = time.time()
print(e - s)
# => ~0.01s