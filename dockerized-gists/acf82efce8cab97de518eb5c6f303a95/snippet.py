#!/usr/bin/env python

def make_masks(n):
    mask = [0] * n
    while True:

        # return the mask
        yield mask

        # increment the mask
        for i in range(n + 1):
            if i == n:
                return
            mask[i] += 1
            if mask[i] > 1:
                mask[i] = 0
            else:
                break


def apply_mask(choices, mask):
    masked = choices[:]
    for i, v in enumerate(mask):
        if v == 0:
            masked[i] = 0
    return masked


def main():
    choices = [2, 9, 4, 9]
    for mask in make_masks(len(choices)):
        total = sum(apply_mask(choices, mask))
        print(mask, total)
        
if __name__ == "__main__":
    main()
