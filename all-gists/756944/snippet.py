#My implementation:
for i in xrange(0, 480, 3):
     for j in xrange(0, 640, 3):
             if depth[i,j] > 900:
                     final[i,j] = depth[i,j]