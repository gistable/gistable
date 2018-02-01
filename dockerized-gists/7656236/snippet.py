def eq(first, *rest):
    for r in rest:
        assert type(first) is type(r), "Different types %s, %s for inputs (%s,%s)" % (type(first), type(r), first, r)
        if first != r:
            return False
    return True

# eq(1) - True
# eq(1, 1) - True
# eq(1, 1, 1) - True
# eq(1, 1, 2) - False
# eq(1, '1') - AssertionError
# eq(1, 1, '1') - AssertionError