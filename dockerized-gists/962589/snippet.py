"""
Folding paper in half 50 times is 3/4 of the distance from earth to sun

From:
http://www.quora.com/What-are-some-of-the-most-mind-blowing-facts#answer_526501

Thickness of a sheet of paper: 0.1 mm (~0.004 inches)

"""


def fold(num_folds=50, thickness=0.1):
    """Simulate folding a sheet of paper in half.

    ``num_folds`` is the number of times we'll fold the paper in half.
    ``thickness`` is the the thickness of a sheet of paper (in millimeters).

    """

    for i in range(1, num_folds + 1):
        thickness = thickness * 2

        if thickness >= 10000:
            # convert to kilometers
            t = thickness / 10000.0
            units = 'km'
        elif thickness >= 1000:
            # convert to meters
            t = thickness / 1000.0
            units = 'm'
        elif thickness >= 100:
            # convert to centimeters
            t = thickness / 100.0
            units = 'cm'
        else:
            # keep in millimeters
            t = thickness
            units = 'mm'

        fmt_string = '{n} folds, thickness = {thickness:G} {units}'
        print(fmt_string.format(n=i, thickness=t, units=units))


if __name__ == "__main__":
    n = input("\n\nHow many folds? ")
    fold(n)
