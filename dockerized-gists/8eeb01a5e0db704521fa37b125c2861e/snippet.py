from __future__ import print_function

import sys

import chainer
from chainer.utils import conv


class ComputationalCostHook(chainer.function.FunctionHook):
    name = 'ComputationalCostHook'

    def __init__(self, sep='', end='\n', file=sys.stdout, flush=True):
        self.sep = sep
        self.end = end
        self.file = file
        self.flush = flush
        self._print(
            'function\tbatch_size\tin_width\tin_height\tin_channels\tout_width'
            '\tout_height\tout_channels\t' +
            'kernel_width\tkernel_height\tpadding\tstride\tGOPs')
        self.total_ops = 0

    def _print(self, msg):
        print(msg, sep=self.sep, end=self.end, file=self.file)

    def _process(self, function, inputs, out_grad=None):
        if function.label == 'Convolution2DFunction':
            self._process_conv2d(function, inputs)
        elif function.label == 'Deconvolution2DFunction':
            self._process_deconv2d(function, inputs)
        elif function.label == 'LinearFunction':
            self._process_linear(function, inputs)

        if self.flush:
            self.file.flush()

    def _process_linear(self, function, inputs):
        x, W = inputs[:2]
        b = inputs[2] if len(inputs) == 3 else None

        batch_size, in_c = x.shape
        out_c, _ = W.shape

        ops = 2 * batch_size * in_c * out_c  # twice because of multiply-and-add
        if b is not None:
            ops += batch_size * out_c
        self._print('%s\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%f' % (
            function.label,
            batch_size,
            1, 1, in_c,
            1, 1, out_c,
            1, 1, 0, 1, ops / 1e9))
        self.total_ops += ops

    def _process_conv2d(self, function, inputs):
        x, W = inputs[:2]
        b = inputs[2] if len(inputs) == 3 else None

        batch_size, in_c, in_h, in_w = x.shape
        out_c, _, kh, kw = W.shape

        out_h = conv.get_conv_outsize(in_h, kh, function.sy, function.ph,
                                      cover_all=function.cover_all)
        out_w = conv.get_conv_outsize(in_w, kw, function.sx, function.pw,
                                      cover_all=function.cover_all)
        ops = 2 * batch_size * in_c * out_c * kw * kh * out_w * out_h  # twice because of multiply-and-add
        if b is not None:
            ops += batch_size * out_c * out_w * out_h  # bias
        self._print('%s\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%f' % (
            function.label,
            batch_size,
            in_w, in_h, in_c,
            out_w, out_h, out_c,
            kw, kh, function.pw, function.sx, ops / 1e9))
        self.total_ops += ops

    def _process_deconv2d(self, function, inputs):
        x, W = inputs[:2]
        b = inputs[2] if len(inputs) == 3 else None
        kh, kw = W.shape[2:]
        batch_size, in_c, in_h, in_w = x.shape
        out_c = W.shape[1]  # out_c
        out_h = conv.get_deconv_outsize(in_h, kh, function.sy, function.ph)
        out_w = conv.get_deconv_outsize(in_w, kw, function.sx, function.pw)

        ops = 2 * batch_size * in_c * out_c * kw * kh * in_w * in_h  # twice because of multiply-and-add
        if b is not None:
            ops += batch_size * out_c * out_w * out_h  # bias
        self._print('%s\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%d\t%f' % (
            function.label,
            batch_size,
            in_w, in_h, in_c,
            out_w, out_h, out_c,
            kw, kh, function.pw, function.sx, ops / 1e9))
        self.total_ops += ops

    def forward_preprocess(self, function, in_data):
        self._process(function, in_data)
