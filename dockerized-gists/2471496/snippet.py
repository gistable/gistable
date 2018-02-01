def countLinesOfCode(path):
    """Procedure to count total lines of code in each file
    """
    total = 0
    listing = os.listdir(path)
    for fname in listing:
        if fname[-2:] == "py":
            with open(fname) as f:
                for i, l in enumerate(f):
                    if len(l) > 80:
                        print "line " + str(i) + " of " \
                            + fname + " is too long."
            subtotal = i + 1
            print string.rjust(fname, 25) + "\t" + str(subtotal)
            total += subtotal
    print total

if __name__ == "__main__":
    countLinesOfCode()