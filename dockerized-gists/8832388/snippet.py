#!/usr/bin/env python

import time

def search_steps(Z, factor=10, verbose=True):
    """
    Finds the number you're looking for.
    """

    # Initialize internal variables
    steps  = 0
    index  = 1
    prev   = 0
    high   = 0

    # Begin the search algorithm
    while True:
        steps += 1 # Increment the number of steps

        try:
            # Does our current number crash us?
            if index < Z:
                if verbose: print "%i UP!" % index
                prev = index # Save the previous state
                if high:
                    # Go halfway towards our bounding space
                    index = (index + high) / 2

                    # Termination condition
                    if index == prev:
                        if verbose: print "FOUND %i!" % (index)
                        break
                else:
                    # Improve exponentially to quickly find bounding space
                    index *= factor

            # We've seen a crash, the number is behind us.
            else:
                high = index # Save the highest seen bounding space
                if verbose: print "%i CRASHED!" % (index)

                # Go back half-way
                index = (index + prev) / 2

                # Termination condition
                if index <= prev:
                    if verbose: print "FOUND %i!" % (index)
                    break

            # Make it readable for humans
            if verbose: time.sleep(0.33)

        except KeyboardInterrupt:
            # Quit if requested
            break

    if verbose: print "Took %i steps" % (steps)
    return steps, index

if __name__ == '__main__':
    search_steps(372040)
