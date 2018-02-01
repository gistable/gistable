#!/usr/bin/env python3

import argparse
import functools
import itertools


# Legendary Mark cost per infusion
COST = 3


# ANSI color enum
class Color:
    black = '\033[0;30m'   # Black
    red = '\033[0;31m'     # Red
    green = '\033[0;32m'   # Green
    yellow = '\033[0;33m'  # Yellow
    blue = '\033[0;34m'    # Blue
    purple = '\033[0;35m'  # Purple
    cyan = '\033[0;36m'    # Cyan
    white = '\033[0;37m'   # White
    term = '\033[0m'       # Terminator


# Item quality enum
class Quality:
    rare = 1
    legendary = 2
    exotic = 3


def printc(string, color=Color.white):
    """Print string with ANSI color escape codes"""

    print("{}{}{}".format(color, string, Color.term))


@functools.total_ordering
class Item():
    """Item wrapper to store light/quality properties"""

    def __init__(self, item, quality=None):
        """Extract light value and quality flag"""

        # Shortcut if quality flag is provided to streamline temp objects
        if quality is not None:
            self.quality = quality
            self.light = item
            return

        # Quality flag is based on '+' or '-' prefix or none
        if item[0] == '+':
            self.quality = Quality.exotic
        elif item[0] == '-':
            self.quality = Quality.rare
        else:
            self.quality = Quality.legendary

        # Make sure light is an integer
        try:
            # Light is rest of string if quality provided, else whole string
            self.light = int(item[1:]
                             if self.quality is not Quality.legendary
                             else item)
        except:
            # Complain and bail
            printc('Error parsing "{}". Item format '
                   'must be: "[+]integer"'.format(item), Color.red)
            exit(2)

    # Handle operators for Items or ints
    def __sub__(self, other):
        return Item(self.light - (other.light if hasattr(other, 'light')
                    else other), self.quality)

    def __add__(self, other):
        return Item(self.light + (other.light if hasattr(other, 'light')
                    else other), self.quality)

    def __mul__(self, other):
        return Item(self.light * (other.light if hasattr(other, 'light')
                    else other), self.quality)

    def __lt__(self, other):
        return self.light < (other.light if hasattr(other, 'light')
                             else other)

    def __eq__(self, other):
        return self.light == (other.light if hasattr(other, 'light')
                              else other)

    # Can round the value too!
    def __round__(self):
        return Item(round(self.light), self.quality)

    # Treat Item like light of item by default
    def __repr__(self):
        return self.light

    def __str__(self):
        return str(self.light)


def permutate(low, mid, high):
    """
    Calculate permutations

    <- low:1, mid: 2 3, high:5
    1 5
    1 2 5
    1 3 5
    1 2 3 5
    """

    # Initialize permutations
    perms = [[low, high]]

    # For each sublist of middle values
    for l in range(1, len(mid) + 1):
        # For each permutation of sublist
        for perm in itertools.combinations(mid, l):
            # Store [low, permutation, high] list
            perms.append(list(itertools.chain([low], perm, [high])))

    return perms


def infuse(base, target):
    """
    Infuse base item with target item

    exotic <- !exotic: <= 4 or 70%
      290 <- 298 = 296
      296 <- 300 = 300
      290 <- 295 = 294
    exotic <- exotic: <= 5 or 70%
      300 <- 310 = 307
      290 <- 310 = 304
    !exotic <- !exotic: <= 6 or 80%
      294 <- 300 = 300
      290 <- 295 = 295
    !exotic <- exotic: <= 7 or 80%
      299 <- 310 = 308
      293 <- 300 = 300
      298 <- 310 = 308
    """

    # Store difference in items
    diff = target - base

    # Calculate close light range
    comp = (6 -
            (2 if base.quality is Quality.exotic else 0) +
            (1 if target.quality is Quality.exotic else 0))

    # Calculate far light percentage
    perc = 0.7 if base.quality is Quality.exotic else 0.8

    if diff <= comp:
        # No penalty, just return target light
        return target
    # Otherwise assess penalty
    else:
        # Resulting light is calculated percentage of the difference
        return base + round(diff * perc)


def walk(items):
    """Walk an infusion path"""

    # Store path reduction by chaining infusions
    result = functools.reduce(infuse, items)

    # Send it back with the step cost
    return (result, (len(items) - 1) * COST, items)


def render(item):
    """Render light with color based on quality"""

    if not hasattr(item, 'quality'):
        color = Color.red
    elif item.quality is Quality.rare:
        color = Color.cyan
    elif item.quality is Quality.exotic:
        color = Color.yellow
    elif item.quality is Quality.legendary:
        color = Color.purple

    return "{}{}{}".format(color, item, Color.term)


def calculate(args):
    """Calculate infusion paths"""

    # Store base item
    low = Item(args.base)

    # Get unique sorted list of Items, tossing items < base
    items = [item for item in sorted(map(Item, set(args.items)))
             if item > low]

    # Bail if base is the highest light item provided
    if len(items) == 0:
        printc('No items with more light than base. Nothing to do!', Color.red)
        exit(2)

    # Store highest and inbetween items
    high = items[-1]
    mid = items[:-1]

    printc("Possible infusion paths", Color.green)

    # Get permutations
    perms = permutate(low, mid, high)

    # Walk each path and store results, sorted by light result
    paths = sorted([walk(perm)
                   for perm in perms], key=lambda index: index[0])

    # Initialize best light/least marks and least marks/best light
    light_marks = marks_light = (Item('0'), 100, )

    # Collect results
    for path in paths:
        # Extract parts
        light, marks, steps = path

        # If light is best we've seen, or same light but least marks
        if (light > light_marks[0] or
                (light == light_marks[0] and marks < light_marks[1])):
            # Store it
            light_marks = (light, marks, steps)

        # If marks is least we've seen, or same marks but best light
        if (marks < marks_light[1] or
                (marks == marks_light[1] and light > marks_light[0])):
            # Store it
            marks_light = (light, marks, steps)

        # Print each possible path
        printc('Light: {}, Marks: {}, Infusion: {}'.format(
            render(light), render(marks), ' <- '.join(map(render, steps))),
            Color.white)

    # Show best light, but least marks
    light, marks, steps = light_marks
    print()
    printc('Best light with least marks', Color.green)
    printc('Light: {}, Marks: {}, Infusion: {}'.format(
        render(light), render(marks), ' <- '.join(map(render, steps))),
        Color.white)

    # Show least marks, but best light
    light, marks, steps = marks_light
    print()
    printc('Least marks with best light', Color.green)
    printc('Light: {}, Marks: {}, Infusion: {}'.format(
        render(light), render(marks), ' <- '.join(map(render, steps))),
        Color.white)

# Entry point
if __name__ == '__main__':
    # Initialize the argument parser
    parser = argparse.ArgumentParser(
        description='Calculates infusion paths, '
                    'showing costs and final light.',
        epilog="""
            At least two items are required -- the base item and one other
            item -- but multiple items can be provided in any order; duplicates
            will be pruned. The base item should be the lowest light, any other
            items with lower light than the base will be discarded. The highest
            light item is considered the target. All infusion paths from base
            to target will be calculated.\n
        """)

    # Add some args
    parser.add_argument('-v', '--version', action='version', version='1.0')
    parser.add_argument('base', metavar='BASE', help='integer light level of '
                        'base item to infuse (ex: 200, +200 for exotic, -200 '
                        'for rare)')
    parser.add_argument('items', metavar='ITEM', nargs='+', help='integer '
                        'light level of other item to consider (ex: 220, '
                        '+220 for exotic, -220 for rare)')

    # Do the needful
    calculate(parser.parse_args())