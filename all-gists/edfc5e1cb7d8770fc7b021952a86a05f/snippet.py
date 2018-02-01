import sys

def main():
    N = raw_input()
    elements = [int(element) for element in sys.stdin.read().split(' ')]

    L, R = 0, len(elements)

    # We got ourselves a maximum subarray problem, with inverted semantics.
    # The subarray we want to find is the one to flip all the bits in.
    # We will consider zero bits as having value of -1, and one bits as having value of 1.
    # Then we modify Kadane's algorithm to search for largest negative sum instead of positive:
    max_difference = 0
    flip_start, flip_end = -1, -1
    ones_to_flip = 0
    total_ones = 0

    current_difference = 0
    current_start = 0
    current_ones_to_flip = 0

    for idx in range(L, R):
        if elements[idx] == 0:
            current_difference -= 1
        else:
            current_difference += 1
            current_ones_to_flip += 1
            total_ones += 1

        if current_difference < max_difference:
            max_difference = current_difference
            flip_start = current_start
            flip_end = idx
            ones_to_flip = current_ones_to_flip
        elif current_difference > 0:
            current_difference = 0
            current_start = idx + 1
            current_ones_to_flip = 0

    # The total number of 1-bits is the number of 1-bits in the flipped range, plus the
    # number of 1-bits in the initial sequence minus those which will be flipped:
    if flip_end != -1:
        print(flip_end - flip_start + 1 - ones_to_flip + total_ones - ones_to_flip)
    else:
        print(total_ones)

main()
