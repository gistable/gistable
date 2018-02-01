# 何らかの理由でbatchレンダリングがうまくいかない、Maya HWだと何故かレンダリングが遅い、みたいなときに便利なスクリプト
# 連番をRender View上でレンダリングします
# Progress window付きでキャンセルすることが可能ですが、なぜかRender Viewの下に隠れてしまうので上手いことやらないとキャンセル出来ないので要注意

from pymel.core import *
from maya import mel
import math
preroll_start = None
s = int(playbackOptions(q=True, min=True)) # start frame 
e = int(playbackOptions(q=True, max=True)) # end frame
nframes = e - s + 1
amount = 0
progressWindow(title='Rendering ...', progress=amount, status='Processing: 0%', isInterruptable=True)
counter = 0
start_frame = preroll_start if preroll_start != None else s
for i in range(start_frame, e+1):
    if progressWindow(q=True, isCancelled=True):
        print('[INFO] Rendering stopped.')
        break
    currentTime(i)
    if i < s:
        continue
    mel.eval('renderWindowRender redoPreviousRender renderView;')
    counter += 1
    amount = int(math.floor(counter / nframes))
    progressWindow(e=True, progress=amount, status='Processing: %d%% (%d/%d)' % (amount, counter, nframes))
progressWindow(endProgress=True)
print('# Done')

