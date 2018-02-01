import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.nn.parameter import Parameter

def debug(debug_open, x, layername):
    if debug_open:
        print x.size(), 'after', layername

class PVANet(nn.Module):
    def __init__(self, backend=None, debug=False):
        super(PVANet, self).__init__()
        self.conv1 = nn.Conv2d(3, 16, kernel_size=7, bias=False, stride=2, padding=3)
        self.bn1 = nn.BatchNorm2d(16, affine=False)
        
        # self.scale1 = Parameter(torch.Tensor([1,0]))

        self.relu1 = nn.ReLU(inplace=True)
        self.pool1 = nn.MaxPool2d(3, stride=2, padding=1)

        self.mcrelu2_1 = MCRelu(32, 24, 64, 3, restype=1, first=True)
        self.mcrelu2_2 = MCRelu(64, 24, 64, 3)
        self.mcrelu2_3 = MCRelu(64, 24, 64, 3)

        self.mcrelu3_1_d = MCRelu(64, 48, 128, 3, stride=2, restype=1, dilation=2)
        self.mcrelu3_2_d = MCRelu(128, 48, 128, 3, dilation=3)
        self.mcrelu3_3_d = MCRelu(128, 48, 128, 3, dilation=2)
        self.mcrelu3_4_d = MCRelu(128, 48, 128, 3, dilation=5)

        self.incep4_1 = Inception(in_channels=128, out_channels=256, i3_out1=48, i3_out2=128, \
                                  i5_out1=24, i5_out2=48, i5_out3=48, stride=2, pool_features=128)
        self.incep4_2 = Inception(in_channels=256, out_channels=256, i3_out1=64, i3_out2=128, \
                                  i5_out1=24, i5_out2=48, i5_out3=48)
        self.incep4_3 = Inception(in_channels=256, out_channels=256, i3_out1=64, i3_out2=128, \
                                  i5_out1=24, i5_out2=48, i5_out3=48)
        self.incep4_4 = Inception(in_channels=256, out_channels=256, i3_out1=64, i3_out2=128, \
                                  i5_out1=24, i5_out2=48, i5_out3=48)

        self.incep5_1 = Inception(in_channels=256, out_channels=384, i3_out1=96, i3_out2=192, \
                                  i5_out1=32, i5_out2=64, i5_out3=64, stride=2, pool_features=128)
        self.incep5_2 = Inception(in_channels=384, out_channels=384, i3_out1=64, i3_out2=128, \
                                  i5_out1=32, i5_out2=64, i5_out3=64)
        self.incep5_3 = Inception(in_channels=384, out_channels=384, i3_out1=64, i3_out2=128, \
                                  i5_out1=32, i5_out2=64, i5_out3=64)
        self.incep5_4 = LastInception(in_channels=384, out_channels=384, i3_out1=64, i3_out2=128, \
                                  i5_out1=32, i5_out2=64, i5_out3=64)

        self.backend = backend
        self.debug_open = debug

    def forward(self, x):
        x1 = self.conv1(x)
        #debug(self.debug_open, x,'conv1')
        x1 = self.bn1(x1)
        x1 = torch.cat([x1, -x1],1)
        # x = self.scale1[0].expand_as(x)*x+self.scale1[1].expand_as(x)
        x1 = self.relu1(x1)
        #self.debug(x1,'relu1')
        x1 = self.pool1(x1)
        #self.debug(x1,'pool1')

        x1 = self.mcrelu2_1(x1)
        #self.debug(x1,'mcrelu2_1')
        x1 = self.mcrelu2_2(x1)
        x1 = self.mcrelu2_3(x1)
        #self.debug(x1,'mcrelu2_3')
        
        x2 = self.mcrelu3_1_d(x1)
        x2 = self.mcrelu3_2_d(x2)
        x2 = self.mcrelu3_3_d(x2)
        x2 = self.mcrelu3_4_d(x2)
        #self.debug(x2,'mcrelu3_3')

        x3 = self.incep4_1(x2)
        #self.debug(x3,'incep4_1')
        x3 = self.incep4_2(x3)
        x3 = self.incep4_3(x3)
        x3 = self.incep4_4(x3)
        #self.debug(x3,'incep4_4')

        x = self.incep5_1(x3)
        x = self.incep5_2(x)
        x = self.incep5_3(x)
        x = self.incep5_4(x)
        #self.debug(x,'incep5_4')

        if self.backend:
            x = self.backend(x)
            return x

        else:
            return [x, x1, x2, x3]


class MCRelu(nn.Module):

    def __init__(self, inchannel, midchannel, outchannel, ksize, stride=1, restype=0, first=False, dilation=1):
        super(MCRelu, self).__init__()

        self.bn = nn.BatchNorm2d(inchannel, affine=True)
        self.relu = nn.ReLU(inplace=True)

        self.conv1 = nn.Conv2d(inchannel, midchannel, kernel_size=1, stride=stride, bias=True)
        self.bn1 = nn.BatchNorm2d(midchannel, affine=True)
        self.relu1 = nn.ReLU(inplace=True)

        self.conv2 = nn.Conv2d(midchannel, midchannel, kernel_size=ksize, \
                               padding = dilation*(ksize-1)/2, bias=True, dilation=dilation)
        self.bn2 = nn.BatchNorm2d(midchannel, affine=False)
        self.scale2 = Parameter(torch.Tensor([1,0]))
        self.relu2 = nn.ReLU(inplace=True)

        self.conv3 = nn.Conv2d(midchannel*2, outchannel, kernel_size=1)

        self.first = first
        #restype : 1-proj(conv) 2-input(identi)
        self.restype = restype
        if restype == 1:
            self.proj = nn.Conv2d(inchannel, outchannel, kernel_size=1, stride=stride)


    def forward(self, x):
        if self.restype == 1 and not self.first:
            x = self.bn(x)
            x = self.relu(x)
            out = x
        elif not self.first:
            out = self.bn(x)
            out = self.relu(out)
        else:
            out = x

        out = self.conv1(out)
        out = self.bn1(out)
        out = self.relu1(out)

        out = self.conv2(out)
        out = self.bn2(out)
        out = torch.cat([out, out*-1],1)
        out = self.scale2[0].expand_as(out)*out+self.scale2[1].expand_as(out)
        out = self.relu2(out)

        out = self.conv3(out)
        
        if self.restype == 1:
            out = out+self.proj(x)
        else:
            out = out+x

        return out


class InceptionBlock(nn.Module):

    def __init__(self, in_channels, out_channels, i3_out1, i3_out2, \
                 i5_out1, i5_out2, i5_out3, stride=1, pool_features=0):
        super(InceptionBlock, self).__init__()

        self.bn = nn.BatchNorm2d(in_channels, affine=True)
        self.relu = nn.ReLU(inplace=True)

        self.branch1x1 = BasicConv2d(in_channels, 64, kernel_size=1, stride=stride)

        self.branch3x3_1 = BasicConv2d(in_channels, i3_out1, kernel_size=1)
        self.branch3x3_2 = BasicConv2d(i3_out1, i3_out2, kernel_size=3, padding=1, stride=stride)

        self.branch5x5_1 = BasicConv2d(in_channels, i5_out1, kernel_size=1)
        self.branch5x5_2 = BasicConv2d(i5_out1, i5_out2, kernel_size=3, padding=1)
        self.branch5x5_3 = BasicConv2d(i5_out2, i5_out3, kernel_size=3, padding=1, stride=stride)

        self.pool = pool_features 
        if self.pool > 0:
            self.branch_pool = nn.MaxPool2d(3, stride=2, padding=1)
            self.branch_pool_conv = BasicConv2d(in_channels, pool_features, kernel_size=1)

            self.proj = nn.Conv2d(in_channels, out_channels, kernel_size=1, stride=stride)

        self.out_conv = nn.Conv2d(64+i3_out2+i5_out3+pool_features, out_channels, kernel_size=1)
        

    def forward(self, x):
        pre = self.bn(x)
        pre = self.relu(pre)

        branch1x1 = self.branch1x1(pre)

        branch3x3 = self.branch3x3_1(pre)
        branch3x3 = self.branch3x3_2(branch3x3)

        branch5x5 = self.branch5x5_1(pre)
        branch5x5 = self.branch5x5_2(branch5x5)
        branch5x5 = self.branch5x5_3(branch5x5)

        if self.pool > 0:
            branch_pool = self.branch_pool(pre)
            branch_pool = self.branch_pool_conv(branch_pool)
            outputs = [branch1x1, branch3x3, branch5x5, branch_pool]
        else:
            outputs = [branch1x1, branch3x3, branch5x5]
        outputs = torch.cat(outputs, 1)
        outputs = self.out_conv(outputs)
        
        if self.pool > 0:
            return [outputs, self.proj(x)]
        else:
            return [outputs, x]

class Inception(nn.Module):
    def __init__(self, in_channels, out_channels, i3_out1, i3_out2, \
                 i5_out1, i5_out2, i5_out3, stride=1, pool_features=0):
        super(Inception, self).__init__()
        
        self.inceptionblock = InceptionBlock(in_channels, out_channels, i3_out1, i3_out2, \
                                             i5_out1, i5_out2, i5_out3, stride, pool_features)

    def forward(self, x):
        out1, out2 = self.inceptionblock(x)
        out1 = out1+out2
        return out1

class LastInception(nn.Module):
    def __init__(self, in_channels, out_channels, i3_out1, i3_out2, \
                 i5_out1, i5_out2, i5_out3, stride=1, pool_features=0):
        super(LastInception, self).__init__()
        self.inceptionblock = InceptionBlock(in_channels, out_channels, i3_out1, i3_out2, \
                                             i5_out1, i5_out2, i5_out3, stride, pool_features)
        self.bn1 = nn.BatchNorm2d(out_channels, affine=True)

        self.bn2 = nn.BatchNorm2d(out_channels, affine=True)
        self.relu = nn.ReLU(inplace=True)
    
    def forward(self, x):
        out1, out2 = self.inceptionblock(x)
        out1 = self.bn1(out1)

        out1 = out1+out2
        out1 = self.bn2(out1)
        out1 = self.relu(out1)

        return out1 

class BasicConv2d(nn.Module):

    def __init__(self, in_channels, out_channels, **kwargs):
        super(BasicConv2d, self).__init__()
        self.conv = nn.Conv2d(in_channels, out_channels, bias=False, **kwargs)
        self.bn = nn.BatchNorm2d(out_channels, eps=0.001)

    def forward(self, x):
        x = self.conv(x)
        x = self.bn(x)
        return F.relu(x, inplace=True)


class clsBackend(nn.Module):

    def __init__(self, in_channels, mid_channels, out_channels):
        super(clsBackend, self).__init__()
        self.fc4 = nn.Linear(in_channels, mid_channels)
        self.bn4 = nn.BatchNorm1d(mid_channels)
        self.dropout4 = nn.Dropout()

        self.fc5 = nn.Linear(mid_channels, out_channels)
        #self.bn2 = nn.BatchNorm1d(mid_channels)
        #self.dropout2 = nn.Dropout()

        #self.fc3 = nn.Linear(mid_channels, out_channels)
        #self.directfc = nn.Linear(in_channels, out_channels)


    def forward(self, x):  
        out = x.view(x.size(0), -1)
        out = self.fc4(out)
        out = self.bn4(out)
        out = self.dropout4(out)
        out = self.fc5(out)
        #out = self.bn2(out)
        #out = self.dropout2(out)
        #out = self.fc3(out)
        #out = self.directfc(out)

        return out




class PVA_FCN(nn.Module):
    def __init__(self, pvamodel, debug=False):
        super(PVA_FCN, self).__init__()
        self.debug_open = debug

        self.pvamodel = pvamodel
        self.up7_14 = UpBlocks(384, 192)
        self.up14_28 = UpBlocks(192, 96)
        self.up28_56 = UpBlocks(96, 48)
        self.up56_112 = UpBlocks(48, 24)
        self.up112_224 = UpBlocks(24, 12)

        # with conv4_4
        self.reduceconv4 = nn.Conv2d(256, 192, kernel_size=1)
        # with conv3_4
        self.reduceconv3 = nn.Conv2d(128, 96, kernel_size=1)
        # with conv2_3
        self.reduceconv2 = nn.Conv2d(64, 48, kernel_size=1)

        #output layers -- fcn
        self.out224 = nn.Conv2d(12, 2, kernel_size=1)

        self.conv112 = nn.Conv2d(24, 2, kernel_size=1)
        self.out112 = nn.UpsamplingNearest2d(scale_factor=2)

        #output layers -- parameter
        self.pconv56_224 = nn.ConvTranspose2d(48, 32, 3, stride=(1, 4), padding=1, output_padding=(0, 3))
        self.pconv7_224 = nn.Conv2d(32, 24, kernel_size=(15, 3), stride=(8, 1), padding=(7, 1))
        self.pbn7_224 = nn.BatchNorm2d(24)
        self.prelu7_224 = nn.ReLU(inplace=True)
        self.pout56 = nn.Conv2d(24, 1, kernel_size=(7, 3), padding=(0,1))

        self.pconv112_224 = nn.ConvTranspose2d(24, 24, 3, stride=(1, 2), padding=1, output_padding=(0, 1))
        self.pconv14_224 = nn.Conv2d(24, 16, kernel_size=(15, 3), stride=(8, 1), padding=(7, 1))
        self.pbn14_224 = nn.BatchNorm2d(16)
        self.prelu14_224 = nn.ReLU(inplace=True)
        self.pout224 = nn.Conv2d(16, 1, kernel_size=(14, 3), padding=(0,1))

    def forward(self, x):
        out, conv2_3, conv3_4, conv4_4 = self.pvamodel(x)
        debug(self.debug_open, out, 'after pva model')
        out = self.up7_14(out)
        conv4_4 = self.reduceconv4(conv4_4)
        out = out + conv4_4
        out = self.up14_28(out)
        conv3_4 = self.reduceconv3(conv3_4)
        out = out + conv3_4
        out = self.up28_56(out)
        debug(self.debug_open, out, '28_to_56')
        ##out 56 param branch
        # pout56 = self.pconv56_224(out)
        # pout56 = self.pconv7_224(pout56)
        # pout56 = self.pbn7_224(pout56)
        # pout56 = self.prelu7_224(pout56)
        # pout56 = self.pout56(pout56)

        conv2_3 = self.reduceconv2(conv2_3)
        out = out + conv2_3
        out = self.up56_112(out)
        debug(self.debug_open, out, '56_to_112')
        ##out 112 branch
        # out112 = self.conv112(out)
        # out112 = self.out112(out112)

        ##out 224 branch
        out224 = self.up112_224(out)
        out224 = self.out224(out224)
        debug(self.debug_open, out224, 'final out 224')
        ##out 224 param branch
        # pout224 = self.pconv112_224(out)
        # pout224 = self.pconv14_224(pout224)
        # pout224 = self.pbn14_224(pout224)
        # pout224 = self.prelu14_224(pout224)
        # pout224 = self.pout224(pout224)

        #return [out112, out224, pout56, pout224]
        return out224


#fcn backend
class UpBlocks(nn.Module):
    def __init__(self, in_channels, out_channels, scale=2):
        super(UpBlocks, self).__init__()

        self.upsample = nn.ConvTranspose2d(in_channels, out_channels, 3, stride=scale, padding=1, output_padding=scale-1)
        self.bn = nn.BatchNorm2d(out_channels)
        self.relu = nn.ReLU(inplace=True)

    def forward(self, x):
        out = self.upsample(x)
        out = self.bn(out)
        out = self.relu(out)
        return out 



def PVA_Imagenet1k():
    #input size = 224*224
    backend = clsBackend(384*(224/32)**2, 2048, 1000)
    model = PVANet(backend, False)
    return model
