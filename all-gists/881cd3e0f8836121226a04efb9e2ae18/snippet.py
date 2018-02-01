import torch
from torch.autograd import Variable
import torch.nn as nn


class Bottleneck(nn.Module):
    cardinality = 32  # the size of the set of transformations

    def __init__(self, nb_channels_in, nb_channels, nb_channels_out, stride=1):
        super().__init__()

        self.conv1 = nn.Conv2d(nb_channels_in, nb_channels, kernel_size=1)
        self.bn1 = nn.BatchNorm2d(nb_channels)
        self.relu = nn.ReLU(inplace=True)

        self.conv2 = nn.Conv2d(nb_channels, nb_channels, kernel_size=3, stride=stride, padding=1, groups=self.cardinality)
        self.bn2 = nn.BatchNorm2d(nb_channels)

        self.conv3 = nn.Conv2d(nb_channels, nb_channels_out, kernel_size=1)
        self.bn3 = nn.BatchNorm2d(nb_channels_out)

        if nb_channels_in != nb_channels_out or stride != 1:
            self.project = nn.Conv2d(nb_channels_in, nb_channels_out, kernel_size=1, stride=stride)
        else:
            self.project = None

    def forward(self, x):
        residual = x

        out = self.conv1(x)
        out = self.bn1(out)
        out = self.relu(out)

        out = self.conv2(out)
        out = self.bn2(out)
        out = self.relu(out)

        out = self.conv3(out)
        out = self.bn3(out)

        if callable(self.project):
            residual = self.project(residual)

        out += residual
        out = self.relu(out)

        return out


class ResNeXt(nn.Module):
    def __init__(self):
        super().__init__()

        # conv1
        self.conv1 = nn.Conv2d(3, 64, kernel_size=7, stride=2, padding=3)
        self.bn1 = nn.BatchNorm2d(64)
        self.relu = nn.ReLU(inplace=True)

        # conv2
        self.max_pool = nn.MaxPool2d(kernel_size=3, stride=2, padding=1)

        conv2 = []
        for i in range(2):
            nb_channels_in = 64 if i == 0 else 256
            conv2.append(Bottleneck(nb_channels_in, 128, 256))

        self.conv2 = nn.Sequential(*conv2)

        # conv3
        conv3 = []
        for i in range(2):
            if i == 0:
                nb_channels_in = 256
                stride = 2
            else:
                nb_channels_in = 512
                stride = 1

            conv3.append(Bottleneck(nb_channels_in, 256, 512, stride=stride))

        self.conv3 = nn.Sequential(*conv3)

        # conv4
        conv4 = []
        for i in range(2):
            if i == 0:
                nb_channels_in = 512
                stride = 2
            else:
                nb_channels_in = 1024
                stride = 1

            conv4.append(Bottleneck(nb_channels_in, 512, 1024, stride=stride))

        self.conv4 = nn.Sequential(*conv4)

        # conv5
        conv5 = []
        for i in range(2):
            if i == 0:
                nb_channels_in = 1024
                stride = 2
            else:
                nb_channels_in = 2048
                stride = 1

            conv5.append(Bottleneck(nb_channels_in, 1024, 2048, stride=stride))

        self.conv5 = nn.Sequential(*conv5)

        self.avg_pool = nn.AvgPool2d(7)
        self.fc = nn.Linear(2048, 10)

    def forward(self, x):
        # conv1
        x = self.conv1(x)
        x = self.bn1(x)
        x = self.relu(x)

        # conv2
        x = self.max_pool(x)
        for block in self.conv2:
            x = block(x)

        # conv3
        for block in self.conv3:
            x = block(x)

        # conv4
        for block in self.conv4:
            x = block(x)

        # conv5
        for block in self.conv5:
            x = block(x)

        x = self.avg_pool(x)
        x = x.view(x.size(0), -1)
        x = self.fc(x)

        return x


def main():
    model = ResNeXt()
    print(model)

    inputs = torch.randn(1, 3, 224, 224)
    y = model.forward(Variable(inputs))
    print(y)


if __name__ == '__main__':
    main()
