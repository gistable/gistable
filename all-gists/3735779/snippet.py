#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: filetype=pyopencl.python

import sys
import time
from PyQt4 import QtCore
from PyQt4 import QtGui
import pyopencl as cl
import numpy

CL_SOURCE = '''//CL//
__kernel void convert(
    read_only image2d_t src,
    write_only image2d_t dest,
    const int width,
    const int height
)
{
    const sampler_t sampler =  CLK_NORMALIZED_COORDS_FALSE | CLK_ADDRESS_CLAMP_TO_EDGE | CLK_FILTER_NEAREST;
    int2 pos = (int2)(get_global_id(0), get_global_id(1));

    uint4 pix = 4 * read_imageui(src, sampler, pos);
    pix += read_imageui(src, sampler, (int2)(pos.x - 1, pos.y - 1));
    pix += read_imageui(src, sampler, (int2)(pos.x - 1, pos.y)) * 2;
    pix += read_imageui(src, sampler, (int2)(pos.x - 1, pos.y + 1));
    pix += read_imageui(src, sampler, (int2)(pos.x , pos.y - 1)) * 2;
    pix += read_imageui(src, sampler, (int2)(pos.x , pos.y + 1)) * 2;
    pix += read_imageui(src, sampler, (int2)(pos.x + 1, pos.y - 1));
    pix += read_imageui(src, sampler, (int2)(pos.x + 1, pos.y)) * 2;
    pix += read_imageui(src, sampler, (int2)(pos.x + 1, pos.y + 1));
    //pix /= (uint4)(16, 16, 16, 16);
    pix.x /= 16;
    pix.y /= 16;
    pix.z /= 16;
    pix.w /= 16;
    write_imageui(dest, pos, pix);
}
'''

class Widget(QtGui.QWidget):
    def __init__(self, parent=None):
        self.ctx = cl.create_some_context()
        self.queue = cl.CommandQueue(self.ctx)
        self.prg = cl.Program(self.ctx, CL_SOURCE).build()

        super(Widget, self).__init__(parent)

        self.setWindowTitle('Gaussian Filter')
        self.resize(300, 300)
        self.setAcceptDrops(True)

        self.image_label = QtGui.QLabel('Drag & drop image here')

        layout = QtGui.QHBoxLayout()
        layout.addWidget(self.image_label)
        self.setLayout(layout)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        filename = event.mimeData().urls()[0].path()
        img = QtGui.QImage(filename)

        start = time.time()
        image = self.convert(img)
        stop = time.time()
        #print 'processing time', stop - start

        pixmap = QtGui.QPixmap()
        pixmap.convertFromImage(image)
        self.image_label.setPixmap(pixmap)

    def convert(self, img):
        src = numpy.fromstring(img.bits().asstring(img.byteCount()), dtype=numpy.uint8)
        src.shape = h, w, _ = img.height(), img.width(), 4

        mf = cl.mem_flags
        src_buf = cl.image_from_array(self.ctx, src, 4)
        fmt = cl.ImageFormat(cl.channel_order.RGBA, cl.channel_type.UNSIGNED_INT8)
        dest_buf = cl.Image(self.ctx, mf.WRITE_ONLY, fmt, shape=(w, h))

        self.prg.convert(self.queue, (w, h), None, src_buf, dest_buf, numpy.int32(w), numpy.int32(h))

        dest = numpy.empty_like(src)
        cl.enqueue_copy(self.queue, dest, dest_buf, origin=(0, 0), region=(w, h))
        return QtGui.QImage(str(dest.data), w, h, QtGui.QImage.Format_RGB32)

if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    window = Widget()
    window.show()
    sys.exit(app.exec_())