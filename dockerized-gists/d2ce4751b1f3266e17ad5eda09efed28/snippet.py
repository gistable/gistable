def iterctr(items, n):
    ctr = 0
    for item in items:
        ctr += 1
        if ctr % n == 0:
            print ctr

        yield item