# I needed to print out ascii tables from data in the form:
# [ ('column 0 title', 'column 1 title'  ..),
#   ('row 0, column 0 data', 'row 0, column 1 data' ...) ...]
#
# and surprisingly it got complicated because of variable lengths of the data.
# I googled for 'standard' ways of doing this and I found suggestions like:
# http://stackoverflow.com/questions/5909873/python-pretty-printing-ascii-tables
# ...which were a bit dated and hard to read or full scale modules like:
#
# http://pypi.python.org/pypi/texttable/
# http://pypi.python.org/pypi/text_table/
# http://pypi.python.org/pypi/asciitable/
#
# ...which were an overkill. So I decided to write my own function and am quite
# pleased with what I got ! :)
#
# Sample usage:
#
# >>> l = [ ('title 0', 'title 1', 'title 2'),
# ...       ('row 0 column 0', 'row 0 column 1 which is long', 'row 0 column 2'),
# ...       ('row 1 column 0', 'row 1 column 1', 'row 1 column 2')
# ... ]
# >>> print_table(l)
# title 0        | title 1                      | title 2
# ---------------+------------------------------+---------------
# row 0 column 0 | row 0 column 1 which is long | row 0 column 2
# row 1 column 0 | row 1 column 1               | row 1 column 2
# >>>

def print_table(rows):
    """print_table(rows)

    Prints out a table using the data in `rows`, which is assumed to be a
    sequence of sequences with the 0th element being the header.
    """

    # - figure out column widths
    widths = [ len(max(columns, key=len)) for columns in zip(*rows) ]

    # - print the header
    header, data = rows[0], rows[1:]
    print(
        ' | '.join( format(title, "%ds" % width) for width, title in zip(widths, header) )
        )

    # - print the separator
    print( '-+-'.join( '-' * width for width in widths ) )

    # - print the data
    for row in data:
        print(
            " | ".join( format(cdata, "%ds" % width) for width, cdata in zip(widths, row) )
            )

