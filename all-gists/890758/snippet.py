from itertools import groupby
from operator import itemgetter

def first(length): return itemgetter(slice(None, length))
def remove_indent(group, n): return (line[n:] for line in group)
def combine(lines, sep): return sep.join(lines) + sep

def indented_sections(text): 
   """
   >>> example = 'One:\n   abc\n   def\nTwo:\n   ghi'
   >>> for section in indented_sections(example): 
   ...    print section.splitlines()
   ['abc', 'def']
   ['ghi']
   """
   groups = groupby(text.splitlines(), first(3))
   for prefix, group in groups: 
      if prefix == '   ': 
         yield combine(remove_indent(group, 3), '\n')

for section in indented_sections(__doc__): 
   if not section.startswith('>>>'): 
      exec(section)
