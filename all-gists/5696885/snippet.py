last = None

with open('index.txt') as f:
    for line in f:
        new = int(line.decode('utf-8').split('\t', 1)[0])
        if last is not None:
            if last - new > 1:
                if last - new == 2:
                    print new + 1
                else:
                    print '%d-%d' % (new + 1, last - 1)
                print 'http://www.gunnerkrigg.com/?p=' + str(new + 1)
        last = new
