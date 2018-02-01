#!/usr/bin/env python
"""
A quick, partial implementation of ENet (https://arxiv.org/abs/1606.02147) using PyTorch.
The original Torch ENet implementation can process a 480x360 image in ~12 ms (on a P2 AWS
instance).  TensorFlow takes ~35 ms.  The PyTorch implementation takes ~25 ms, an improvement
over TensorFlow, but worse than the original Torch.
"""

from __future__ import absolute_import


import sys
import time


import torch
import torch.optim
import torch.nn as nn
import torch.nn.functional as F
from torch.autograd import Variable


ENCODER_PARAMS = [
        {
            'internal_scale': 4,
            'use_relu': True,
            'asymmetric': False,
            'dilated': False,
            'input_channels': 16,
            'output_channels': 64,
            'downsample': True,
            'dropout_prob': 0.01
        },
        {
            'internal_scale': 4,
            'use_relu': True,
            'asymmetric': False,
            'dilated': False,
            'input_channels': 64,
            'output_channels': 64,
            'downsample': False,
            'dropout_prob': 0.01
        },
        {
            'internal_scale': 4,
            'use_relu': True,
            'asymmetric': False,
            'dilated': False,
            'input_channels': 64,
            'output_channels': 64,
            'downsample': False,
            'dropout_prob': 0.01
        },
        {
            'internal_scale': 4,
            'use_relu': True,
            'asymmetric': False,
            'dilated': False,
            'input_channels': 64,
            'output_channels': 64,
            'downsample': False,
            'dropout_prob': 0.01
        },
        {
            'internal_scale': 4,
            'use_relu': True,
            'asymmetric': False,
            'dilated': False,
            'input_channels': 64,
            'output_channels': 64,
            'downsample': False,
            'dropout_prob': 0.01
        },
        {
            'internal_scale': 4,
            'use_relu': True,
            'asymmetric': False,
            'dilated': False,
            'input_channels': 64,
            'output_channels': 128,
            'downsample': True,
            'dropout_prob': 0.1
        },
        {
            'internal_scale': 4,
            'use_relu': True,
            'asymmetric': False,
            'dilated': False,
            'input_channels': 128,
            'output_channels': 128,
            'downsample': False,
            'dropout_prob': 0.1
        },
        {
            'internal_scale': 4,
            'use_relu': True,
            'asymmetric': False,
            'dilated': False,
            'input_channels': 128,
            'output_channels': 128,
            'downsample': False,
            'dropout_prob': 0.1
        },
        {
            'internal_scale': 4,
            'use_relu': True,
            'asymmetric': False,
            'dilated': False,
            'input_channels': 128,
            'output_channels': 128,
            'downsample': False,
            'dropout_prob': 0.1
        },
        {
            'internal_scale': 4,
            'use_relu': True,
            'asymmetric': False,
            'dilated': False,
            'input_channels': 128,
            'output_channels': 128,
            'downsample': False,
            'dropout_prob': 0.1
        },
        {
            'internal_scale': 4,
            'use_relu': True,
            'asymmetric': False,
            'dilated': False,
            'input_channels': 128,
            'output_channels': 128,
            'downsample': False,
            'dropout_prob': 0.1
        },
        {
            'internal_scale': 4,
            'use_relu': True,
            'asymmetric': False,
            'dilated': False,
            'input_channels': 128,
            'output_channels': 128,
            'downsample': False,
            'dropout_prob': 0.1
        },
        {
            'internal_scale': 4,
            'use_relu': True,
            'asymmetric': False,
            'dilated': False,
            'input_channels': 128,
            'output_channels': 128,
            'downsample': False,
            'dropout_prob': 0.1
        },
        {
            'internal_scale': 4,
            'use_relu': True,
            'asymmetric': False,
            'dilated': False,
            'input_channels': 128,
            'output_channels': 128,
            'downsample': False,
            'dropout_prob': 0.1
        },
        {
            'internal_scale': 4,
            'use_relu': True,
            'asymmetric': False,
            'dilated': False,
            'input_channels': 128,
            'output_channels': 128,
            'downsample': False,
            'dropout_prob': 0.1
        },
        {
            'internal_scale': 4,
            'use_relu': True,
            'asymmetric': False,
            'dilated': False,
            'input_channels': 128,
            'output_channels': 128,
            'downsample': False,
            'dropout_prob': 0.1
        },
        {
            'internal_scale': 4,
            'use_relu': True,
            'asymmetric': False,
            'dilated': False,
            'input_channels': 128,
            'output_channels': 128,
            'downsample': False,
            'dropout_prob': 0.1
        },
        {
            'internal_scale': 4,
            'use_relu': True,
            'asymmetric': False,
            'dilated': False,
            'input_channels': 128,
            'output_channels': 128,
            'downsample': False,
            'dropout_prob': 0.1
        },
        {
            'internal_scale': 4,
            'use_relu': True,
            'asymmetric': False,
            'dilated': False,
            'input_channels': 128,
            'output_channels': 128,
            'downsample': False,
            'dropout_prob': 0.1
        },
        {
            'internal_scale': 4,
            'use_relu': True,
            'asymmetric': False,
            'dilated': False,
            'input_channels': 128,
            'output_channels': 128,
            'downsample': False,
            'dropout_prob': 0.1
        },
        {
            'internal_scale': 4,
            'use_relu': True,
            'asymmetric': False,
            'dilated': False,
            'input_channels': 128,
            'output_channels': 128,
            'downsample': False,
            'dropout_prob': 0.1
        },
        {
            'internal_scale': 4,
            'use_relu': True,
            'asymmetric': False,
            'dilated': False,
            'input_channels': 128,
            'output_channels': 128,
            'downsample': False,
            'dropout_prob': 0.1
        },
        {
            'internal_scale': 4,
            'use_relu': True,
            'asymmetric': False,
            'dilated': False,
            'input_channels': 128,
            'output_channels': 128,
            'downsample': False,
            'dropout_prob': 0.1
        }
    ]


DECODER_PARAMS = [
        {
            'input_channels': 128,
            'output_channels': 128,
            'upsample': False,
            'pooling_module': None
        },
        {
            'input_channels': 128,
            'output_channels': 64,
            'upsample': True,
            'pooling_module': None
        },
        {
            'input_channels': 64,
            'output_channels': 64,
            'upsample': False,
            'pooling_module': None
        },
        {
            'input_channels': 64,
            'output_channels': 64,
            'upsample': False,
            'pooling_module': None
        },
        {
            'input_channels': 64,
            'output_channels': 16,
            'upsample': True,
            'pooling_module': None
        },
        {
            'input_channels': 16,
            'output_channels': 16,
            'upsample': False,
            'pooling_module': None
        }
    ]


class InitialBlock(nn.Module):
    def __init__(self):
        super().__init__()

        self.conv = nn.Conv2d(
            3, 13, (3, 3),
            stride=2, padding=1, bias=True)
        self.pool = nn.MaxPool2d(2, stride=2)
        self.batch_norm = nn.BatchNorm2d(16, eps=1e-3)

    def forward(self, input):
        output = torch.cat([self.conv(input), self.pool(input)], 1)
        output = self.batch_norm(output)
        return F.relu(output)


class EncoderMainPath(nn.Module):
    def __init__(self, internal_scale=None, use_relu=None, asymmetric=None, dilated=None, input_channels=None, output_channels=None, downsample=None, dropout_prob=None):
        super().__init__()

        internal_channels = output_channels // internal_scale
        input_stride = downsample and 2 or 1

        self.__dict__.update(locals())
        del self.self

        self.input_conv = nn.Conv2d(
            input_channels, internal_channels, input_stride,
            stride=input_stride, padding=0, bias=False)

        self.input_batch_norm = nn.BatchNorm2d(internal_channels, eps=1e-03)

        # TODO: use dilated and asymmetric convolutions, as in the
        # original implementation.  For now just add a 3x3 convolution.
        self.middle_conv = nn.Conv2d(
            internal_channels, internal_channels, 3,
            stride=1, padding=1, bias=True)

        self.middle_batch_norm = nn.BatchNorm2d(internal_channels, eps=1e-03)

        self.output_conv = nn.Conv2d(
            internal_channels, output_channels, 1,
            stride=1, padding=0, bias=False)

        self.output_batch_norm = nn.BatchNorm2d(output_channels, eps=1e-03)

        self.dropout = nn.Dropout2d(dropout_prob)


    def forward(self, input):
        output = self.input_conv(input)

        output = self.input_batch_norm(output)

        output = F.relu(output)

        output = self.middle_conv(output)

        output = self.middle_batch_norm(output)

        output = F.relu(output)

        output = self.output_conv(output)

        output = self.output_batch_norm(output)

        output = self.dropout(output)
        
        return output


class EncoderOtherPath(nn.Module):
    def __init__(self, internal_scale=None, use_relu=None, asymmetric=None, dilated=None, input_channels=None, output_channels=None, downsample=None, **kwargs):
        super().__init__()

        self.__dict__.update(locals())
        del self.self

        if downsample:
            self.pool = nn.MaxPool2d(2, stride=2, return_indices=True)

    def forward(self, input):
        output = input

        if self.downsample:
            output, self.indices = self.pool(input)

        if self.output_channels != self.input_channels:
            new_size = [1, 1, 1, 1]
            new_size[1] = self.output_channels // self.input_channels
            output = output.repeat(*new_size)

        return output


class EncoderModule(nn.Module):
    def __init__(self, **kwargs):
        super().__init__()
        self.main = EncoderMainPath(**kwargs)
        self.other = EncoderOtherPath(**kwargs)

    def forward(self, input):
        main = self.main(input)
        other = self.other(input)
        return F.relu(main + other)


class Encoder(nn.Module):
    def __init__(self, params, nclasses):
        super().__init__()
        self.initial_block = InitialBlock()

        self.layers = []
        for i, params in enumerate(params):
            layer_name = 'encoder_{:02d}'.format(i)
            layer = EncoderModule(**params)
            super().__setattr__(layer_name, layer)
            self.layers.append(layer)

        self.output_conv = nn.Conv2d(
            128, nclasses, 1,
            stride=1, padding=0, bias=True)

    def forward(self, input, predict=False):
        output = self.initial_block(input)

        for layer in self.layers:
            output = layer(output)

        if predict:
            output = self.output_conv(output)

        return output


class DecoderMainPath(nn.Module):
    def __init__(self, input_channels=None, output_channels=None, upsample=None, pooling_module=None):
        super().__init__()

        internal_channels = output_channels // 4
        input_stride = 2 if upsample is True else 1

        self.__dict__.update(locals())
        del self.self

        self.input_conv = nn.Conv2d(
            input_channels, internal_channels, 1,
            stride=1, padding=0, bias=False)

        self.input_batch_norm = nn.BatchNorm2d(internal_channels, eps=1e-03)

        if not upsample:
            self.middle_conv = nn.Conv2d(
                internal_channels, internal_channels, 3,
                stride=1, padding=1, bias=True)
        else:
            self.middle_conv = nn.ConvTranspose2d(
                internal_channels, internal_channels, 3,
                stride=2, padding=1, output_padding=1,
                bias=True)

        self.middle_batch_norm = nn.BatchNorm2d(internal_channels, eps=1e-03)

        self.output_conv = nn.Conv2d(
            internal_channels, output_channels, 1,
            stride=1, padding=0, bias=False)

        self.output_batch_norm = nn.BatchNorm2d(output_channels, eps=1e-03)

    def forward(self, input):
        output = self.input_conv(input)

        output = self.input_batch_norm(output)

        output = F.relu(output)

        output = self.middle_conv(output)

        output = self.middle_batch_norm(output)

        output = F.relu(output)

        output = self.output_conv(output)

        output = self.output_batch_norm(output)

        return output


class DecoderOtherPath(nn.Module):
    def __init__(self, input_channels=None, output_channels=None, upsample=None, pooling_module=None):
        super().__init__()

        self.__dict__.update(locals())
        del self.self

        if output_channels != input_channels or upsample:
            self.conv = nn.Conv2d(
                input_channels, output_channels, 1,
                stride=1, padding=0, bias=False)
            self.batch_norm = nn.BatchNorm2d(output_channels, eps=1e-03)
            if upsample and pooling_module:
                self.unpool = nn.MaxUnpool2d(2, stride=2, padding=0)

    def forward(self, input):
        output = input

        if self.output_channels != self.input_channels or self.upsample:
            output = self.conv(output)
            output = self.batch_norm(output)
            if self.upsample and self.pooling_module:
                output_size = list(output.size())
                output_size[2] *= 2
                output_size[3] *= 2
                output = self.unpool(
                    output, self.pooling_module.indices,
                    output_size=output_size)

        return output


class DecoderModule(nn.Module):
    def __init__(self, **kwargs):
        super().__init__()

        self.main = DecoderMainPath(**kwargs)
        self.other = DecoderOtherPath(**kwargs)
                                                    
    def forward(self, input):
        main = self.main(input)
        other = self.other(input)
        return F.relu(main + other)


class Decoder(nn.Module):
    def __init__(self, params, nclasses, encoder):
        super().__init__()

        self.encoder = encoder

        self.pooling_modules = []

        for mod in self.encoder.modules():
            try:
                if mod.other.downsample:
                    self.pooling_modules.append(mod.other)
            except AttributeError:
                pass

        self.layers = []
        for i, params in enumerate(params):
            if params['upsample']:
                params['pooling_module'] = self.pooling_modules.pop(-1)
            layer = DecoderModule(**params)
            self.layers.append(layer)
            layer_name = 'decoder{:02d}'.format(i)
            super().__setattr__(layer_name, layer)

        self.output_conv = nn.ConvTranspose2d(
                16, nclasses, 2,
                stride=2, padding=0, output_padding=0, bias=True)

    def forward(self, input):
        output = self.encoder(input, predict=False)

        for layer in self.layers:
            output = layer(output)

        output = self.output_conv(output)

        return output


class ENet(nn.Module):
    def __init__(self, nclasses):
        super().__init__()

        self.encoder = Encoder(ENCODER_PARAMS, nclasses)
        self.decoder = Decoder(DECODER_PARAMS, nclasses, self.encoder)

    def forward(self, input, only_encode=False, predict=True):
        if only_encode:
            return self.encoder.forward(input, predict=predict)
        else:
            return self.decoder.forward(input)


if __name__ == '__main__':
    nclasses = 15
    train = True
    niter = 100
    times = torch.FloatTensor(niter)

    batch_size = 1
    nchannels = 3
    height = 360
    width = 480

    model = ENet(nclasses)
    loss = nn.NLLLoss2d()
    softmax = nn.Softmax()

    model.cuda()
    loss.cuda()
    softmax.cuda()

    optimizer = torch.optim.Adam(model.parameters())

    for i in range(niter):
        x = torch.FloatTensor(
            torch.randn(batch_size, nchannels, height, width))
        y = torch.LongTensor(batch_size, height, width)
        y.random_(nclasses)

        x.pin_memory()
        y.pin_memory()

        input = Variable(x.cuda(async=True))
        target = Variable(y.cuda(async=True))

        sys.stdout.write('\r{}/{}'.format(i, niter))

        start = time.time()

        if train:
            optimizer.zero_grad()
            model.train()
        else:
            model.eval()

        output = model(input)

        if train:
            loss_ = loss.forward(output, target)
            loss_.backward()
            optimizer.step()
        else:
            output_2d = output.view(height * width, nclasses)
            pred = softmax(output_2d).view(output.size())

        times[i] = time.time() - start
    sys.stdout.write('\n')

    print('average time per image {:04f} sec'.format(
        times.mean()))
