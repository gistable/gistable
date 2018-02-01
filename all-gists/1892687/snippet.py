# usage: spark_matrix([[0.1, 0.5, 0.3],
#                     [0.0, 1.0, 0.8],
#                     [0.1, 0.2, 0.1]])
# ▁▅▃
# ▁█▇
# ▁▂▁
#
# If you get encoding errors, uncomment and add next 5 lines to the start of file.
# #!/usr/bin/env python
# # -*- coding: utf-8 -*-
# import sys 
# reload(sys) 
# sys.setdefaultencoding('utf8')

def spark_matrix(data):
    ticks = u'▁▂▃▄▅▆▇█'
    # If the last symbol in ticks does not look good, uncomment the next line.
    #ticks = u'▁▂▃▄▅▆▇'
    maxV = max(max(l) for l in data)
    minV = min(min(l) for l in data)
    step = float(maxV - minV) / len(ticks)
    for row in data:
        heights = []
        for n in row:
            height = 0
            if step != 0:
                height = int((n - minV)/step)
                if height == len(ticks):
                    height = len(ticks) - 1
            heights.append(height)
        print ''.join(ticks[i] for i in heights)