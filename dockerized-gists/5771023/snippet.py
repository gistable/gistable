#!/usr/bin/env python3.2
# Benjamin James Wright <bwright@cse.unsw.edu.au>
# Maximum Subarray

def max_subarray(L):
  current_sum = 0
  current_index = -1
  best_sum  = 0
  best_start_index = -1
  best_end_index = -1

  # Iterate over the array.
  for i in range(len(L)):
    val = current_sum + L[i]
    if val > 0:
        if current_sum == 0:
          current_index = i
        current_sum = val
    else:
      current_sum = 0

    if current_sum > best_sum:
      best_sum = current_sum
      best_start_index = current_index
      best_end_index = i
   
  return L[best_start_index:best_end_index + 1]

if __name__ == '__main__':
  print(max_subarray([1,-3,5,-2,9,-8,-6,4]))
