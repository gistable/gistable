import concurrent.futures
import functools
import operator
import time
from pprint import pprint

TEXT = """Lorem ipsum dolor sit amet, consectetuer adipiscing elit.
Donec odio. Quisque volutpat mattis eros. Nullam malesuada erat ut turpis.
Suspendisse urna nibh, viverra non, semper suscipit, posuere a, pede.
Donec nec justo eget felis facilisis fermentum. Aliquam porttitor mauris
sit amet orci. Aenean dignissim pellentesque felis. Morbi in sem quis
dui placerat ornare. Pellentesque odio nisi, euismod in, pharetra a,
ultricies in, diam. Sed arcu. Cras consequat. Praesent dapibus, neque
id cursus faucibus, tortor neque egestas augue, eu vulputate magna eros
eu erat. Aliquam erat volutpat. Nam dui mi, tincidunt quis, accumsan
porttitor, facilisis luctus, metus."""

print(TEXT)
print()

#
# Step 1: Split the work into independent chunks.
#
# We're using line breaks here because that's convenient --
# alternatively we could split after a fixed number of characters,
# or based on some other metric.
LINES = TEXT.split('\n')

pprint(LINES)
print()


def count_words(line):
    print(f'Counting words in chunk of length {len(line)}')
    time.sleep(1)
    return len(line.split())


start = time.time()

#
# Step 2: Map -- Count the number of words in each chunk in parallel
#
with concurrent.futures.ProcessPoolExecutor() as executor:
    map_result = tuple(executor.map(count_words, LINES))

#
# Step 3: Reduce -- Combine partial results into final output
#
# Alternatively this could be done with "sum(map_result)"
# but it hides the underlying "reduce" step in MapReduce :-)
reduce_result = functools.reduce(operator.add, map_result, 0)

end = time.time()

print(f'\nTime to complete: {end - start:.2f}s\n')
print(f'Result of "map" phase (words per line): {map_result}')
print(f'Result of "reduce" phase (total word count): {reduce_result}')

"""
Expected output:

Lorem ipsum dolor sit amet, consectetuer adipiscing elit.
Donec odio. Quisque volutpat mattis eros. Nullam malesuada erat ut turpis.
Suspendisse urna nibh, viverra non, semper suscipit, posuere a, pede.
Donec nec justo eget felis facilisis fermentum. Aliquam porttitor mauris
sit amet orci. Aenean dignissim pellentesque felis. Morbi in sem quis
dui placerat ornare. Pellentesque odio nisi, euismod in, pharetra a,
ultricies in, diam. Sed arcu. Cras consequat. Praesent dapibus, neque
id cursus faucibus, tortor neque egestas augue, eu vulputate magna eros
eu erat. Aliquam erat volutpat. Nam dui mi, tincidunt quis, accumsan
porttitor, facilisis luctus, metus.

['Lorem ipsum dolor sit amet, consectetuer adipiscing elit.',
 'Donec odio. Quisque volutpat mattis eros. Nullam malesuada erat ut turpis.',
 'Suspendisse urna nibh, viverra non, semper suscipit, posuere a, pede.',
 'Donec nec justo eget felis facilisis fermentum. Aliquam porttitor mauris',
 'sit amet orci. Aenean dignissim pellentesque felis. Morbi in sem quis',
 'dui placerat ornare. Pellentesque odio nisi, euismod in, pharetra a,',
 'ultricies in, diam. Sed arcu. Cras consequat. Praesent dapibus, neque',
 'id cursus faucibus, tortor neque egestas augue, eu vulputate magna eros',
 'eu erat. Aliquam erat volutpat. Nam dui mi, tincidunt quis, accumsan',
 'porttitor, facilisis luctus, metus.']

Counting words in chunk of length 57
Counting words in chunk of length 74
Counting words in chunk of length 69
Counting words in chunk of length 72
Counting words in chunk of length 69
Counting words in chunk of length 68
Counting words in chunk of length 69
Counting words in chunk of length 71
Counting words in chunk of length 68
Counting words in chunk of length 35

Time to complete: 3.03s

Result of "map" phase (words per line): (8, 11, 10, 10, 11, 10, 10, 11, 11, 4)
Result of "reduce" phase (total word count): 96
"""