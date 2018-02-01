from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
from PySide.QtCore import QTime, QTimer
from collections import deque

t = QTime()
t.start()
data = deque(maxlen=20)

class TimeAxisItem(pg.AxisItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def tickStrings(self, values, scale, spacing):
        # PySide's QTime() initialiser fails miserably and dismisses args/kwargs
        return [QTime().addMSecs(value).toString('mm:ss') for value in values]




app = QtGui.QApplication([])

win = pg.GraphicsWindow(title="Basic plotting examples")
win.resize(1000,600)

plot = win.addPlot(title='Timed data', axisItems={'bottom': TimeAxisItem(orientation='bottom')})
curve = plot.plot()

def update():
    global plot, curve, data
    data.append({'x': t.elapsed(), 'y': np.random.randint(0, 100)})
    x = [item['x'] for item in data]
    y = [item['y'] for item in data]
    curve.setData(x=x, y=y)

tmr = QTimer()
tmr.timeout.connect(update)
tmr.start(800)

if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()