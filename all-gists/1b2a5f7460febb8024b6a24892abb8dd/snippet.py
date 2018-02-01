#!/usr/bin/env python
from math import ceil, floor, log10


ones = {
    1: 'one',
    2: 'two',
    3: 'three',
    4: 'four',
    5: 'five',
    6: 'six',
    7: 'seven',
    8: 'eight',
    9: 'nine'
}

tens = {
    1: "ten",
    2: "twenty",
    3: "thirty",
    4: "forty",
    5: "fifty",
    6: "sixty",
    7: "seventy",
    8: "eighty",
    9: "ninety"
}


def places_list(num):
    """Return a list of integers, where each member is the digit in a
    position in `num`.

    ex:

    ```
    places_list(372)
    >> [2, 7, 3]

    places_list(905)
    >> [5, 0, 9]
    ```

    Reversing this operation can be achieved by multiplying each value by
    10 raised to the value's 0-indexed position in the list, e.g.:

    ```
    places = places_list(372)
    sum([i * (10**idx) for idx, i in enumerate(places)])
    >> 372
    ```
    """
    num_log = log10(num)
    places = []

    fac = int(ceil(num_log))

    for i in range(1, fac + 1):
        x = num % (10 ** i)
        val = x / 10 ** (i - 1)
        places.append(val)

    if ceil(num_log) == floor(num_log):
        places.append(1)

    return places


def group_digits(list_of_digits):
    """Group list of items in groups of 3, at most.

    ex:

    ```
    group_digits([1,2,3,4,5,6])
    >> [[1,2,3], [4,5,6]]

    group_digits([1,2,3,4,5,6,7])
    >> [[1,2,3], [4,5,6], [7]]
    ```

    Useful when wanting to group digits by "hundreds."
    """
    return [
        list_of_digits[i-3:i]
        for i in range(3, len(list_of_digits)+3, 3)
    ]


def process_group(group):
    tens_and_ones = process_tens_and_ones(*group[:2])

    if len(group) <= 2 or (len(group) == 3 and group[2] == 0):
        return tens_and_ones
    else:
        hundreds = "{}-hundred".format(ones[group[2]])

        if tens_and_ones:
            return "{} and {}".format(hundreds, tens_and_ones)
        else:
            return hundreds


def process_tens_and_ones(ones_digit, tens_digit=0):
    if ones_digit == 0:
        # If both digits are zero, return an empty string.
        # If only the ones digit is zero, return the correct value from the
        # `tens` dict.
        if tens_digit == 0:
            return ""
        else:
            return tens[tens_digit]

    if tens_digit == 0 :
        return ones[ones_digit]
    if tens_digit == 1:
        return teens(ones_digit)

    return "{}-{}".format(tens[tens_digit], ones[ones_digit])


def teens(ones_digit):
    """Return string analog for numbers between 10 and 20, about half of
    which are edge cases.
    """
    if ones_digit == 1:
        return "eleven"
    elif ones_digit == 2:
        return "twelve"
    elif ones_digit == 3:
        return "thirteen"
    elif ones_digit == 5:
        return "fifteen"
    else:
        return '{}teen'.format(ones[ones_digit % 10])


def main(num):
    suffixes = {
        0: "",
        1: "thousand",
        2: "million",
        3: "billion",
        4: "trillion",
        5: "quadrillion",
        6: "quintillion",
        7: "sextillion",
        8: "septillion",
        9: "octillion",
        10: "nonillion",
        11: "decillion"
    }

    if num == 0:
        return "zero"

    negative = num < 0

    if negative:
        num = abs(num)

    ps = places_list(num)
    strings = []

    for idx, group in enumerate(group_digits(ps)):
        value = process_group(group)

        if not value:
            continue

        suffix = suffixes[idx]

        if suffix:
            value = " ".join([value, suffix])

        strings.append(value)

    retval = ", ".join(reversed(strings))

    if negative:
        retval = 'negative {}'.format(retval)

    return retval


if __name__ == "__main__":
    import sys
    print main(int(sys.argv[1]))
