#!/usr/bin/python

def water(levels, second_pass = False):
   # sanity check
   if len(levels) < 2:
      return 0

   # state machine
   filling = False
   h = 0
   h_index = 0
   total = 0
   cur = 0

   for i in xrange(1, len(levels)):
      # we can start filling once we see a first drop in level
      if not filling and levels[i] < levels[i-1]:
         filling = True
         h_index = i-1
         h = levels[h_index]

      if filling:
         # we need to stop filling if level is above the original wall
         if levels[i] >= h:
            total += cur
            cur = 0
            filling = False

         # otherwise, count this level as a puddle
         else:
            cur += h - levels[i]

   # close the final puddle by going backwards from -1 to h_index
   if not second_pass:
      final_puddle = [levels[l] for l in range(len(levels) -1, h_index, -1)]
      total += water(final_puddle, True)

   return total

if __name__ == "__main__":
   testcases = [
         ([1,0,1], 1),
         ([5,0,5], 5),
         ([0,1,0,1,0], 1),
         ([1,0,1,0], 1),
         ([1,0,1,2,0,2], 3),
         ([2,5,1,2,3,4,7,7,6], 10),
         ([5,1,0,1],1),                 # thanks https://news.ycombinator.com/item?id=6640085
         ([2,5,1,2,3,4,7,7,6,3,5], 12), # thanks https://news.ycombinator.com/item?id=6640105
         ]

   for case in testcases:
      w = water(case[0])
      if w == case[1]:
         print "TRUE: %s holds %s" % (case[0], w)
      else:
         print "MISMATCH: %s holds %s (got %s)" % (case[0], case[1], w)
