"""
Dynamic Routing Between Capsules
https://arxiv.org/abs/1710.09829
"""

import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import torchvision.transforms as transforms

import numpy as np

from torch.autograd import Variable
from torchvision.datasets.mnist import MNIST
from tqdm import tqdm


def index_to_one_hot(index_tensor, num_classes=10):
    """
    Converts index value to one hot vector.

    e.g. [2, 5] (with 10 classes) becomes:
        [
            [0 0 1 0 0 0 0 0 0 0]
            [0 0 0 0 1 0 0 0 0 0]
        ]
    """
    index_tensor = index_tensor.long()
    return torch.eye(num_classes).index_select(dim=0, index=index_tensor)


def squash_vector(tensor, dim=-1):
    """
    Non-linear 'squashing' to ensure short vectors get shrunk
    to almost zero length and long vectors get shrunk to a
    length slightly below 1.
    """
    squared_norm = (tensor**2).sum(dim=dim, keepdim=True)
    scale = squared_norm / (1 + squared_norm)
    return scale * tensor / torch.sqrt(squared_norm)


def softmax(input, dim=1):
    """
    Apply softmax to specific dimensions. Not released on PyTorch stable yet
    as of November 6th 2017
    https://github.com/pytorch/pytorch/issues/3235
    """
    transposed_input = input.transpose(dim, len(input.size()) - 1)
    softmaxed_output = F.softmax(
        transposed_input.contiguous().view(-1, transposed_input.size(-1)))
    return softmaxed_output.view(*transposed_input.size()).transpose(dim, len(input.size()) - 1)


class CapsuleLayer(nn.Module):
    def __init__(self, num_capsules, num_routes, in_channels, out_channels,
                 kernel_size=None, stride=None, num_iterations=3):
        super().__init__()

        self.num_routes = num_routes
        self.num_iterations = num_iterations

        self.num_capsules = num_capsules

        if num_routes != -1:
            self.route_weights = nn.Parameter(
                torch.randn(num_capsules, num_routes,
                            in_channels, out_channels)
            )

        else:
            self.capsules = nn.ModuleList(
                [nn.Conv2d(in_channels,
                           out_channels,
                           kernel_size=kernel_size,
                           stride=stride,
                           padding=0)
                 for _ in range(num_capsules)
                 ]
            )

    def forward(self, x):
        # If routing is defined
        if self.num_routes != -1:
            priors = x[None, :, :, None, :] @ self.route_weights[:, None, :, :, :]

            logits = Variable(torch.zeros(priors.size())).cuda()

            # Routing algorithm
            for i in range(self.num_iterations):
                probs = softmax(logits, dim=2)
                outputs = squash_vector(
                    probs * priors).sum(dim=2, keepdim=True)

                if i != self.num_iterations - 1:
                    delta_logits = (priors * outputs).sum(dim=-1, keepdim=True)
                    logits = logits + delta_logits

        else:
            outputs = [capsule(x).view(x.size(0), -1, 1)
                       for capsule in self.capsules]
            outputs = torch.cat(outputs, dim=-1)
            outputs = squash_vector(outputs)

        return outputs


class MarginLoss(nn.Module):
    def __init__(self):
        super().__init__()
        # Reconstruction as regularization
        self.reconstruction_loss = nn.MSELoss(size_average=False)

    def forward(self, images, labels, classes, reconstructions):
        left = F.relu(0.9 - classes, inplace=True) ** 2
        right = F.relu(classes - 0.1, inplace=True) ** 2
        margin_loss = labels * left + 0.5 * (1. - labels) * right
        margin_loss = margin_loss.sum()
        reconstruction_loss = self.reconstruction_loss(reconstructions, images)

        return (margin_loss + 0.0005 * reconstruction_loss) / images.size(0)


class CapsuleNet(nn.Module):
    def __init__(self):
        super().__init__()

        self.conv1 = nn.Conv2d(
            in_channels=1, out_channels=256, kernel_size=9, stride=1)
        self.primary_capsules = CapsuleLayer(
            8, -1, 256, 32, kernel_size=9, stride=2)

        # 10 is the number of classes
        self.digit_capsules = CapsuleLayer(10, 32 * 6 * 6, 8, 16)

        self.decoder = nn.Sequential(
            nn.Linear(16 * 10, 512),
            nn.ReLU(inplace=True),
            nn.Linear(512, 1024),
            nn.ReLU(inplace=True),
            nn.Linear(1024, 784),
            nn.Sigmoid()
        )

    def forward(self, x, y=None):
        x = F.relu(self.conv1(x), inplace=True)
        x = self.primary_capsules(x)
        x = self.digit_capsules(x).squeeze().transpose(0, 1)

        classes = (x ** 2).sum(dim=-1) ** 0.5
        classes = F.softmax(classes)

        if y is None:
            # In all batches, get the most active capsule
            _, max_length_indices = classes.max(dim=1)
            y = Variable(torch.eye(10)).cuda().index_select(
                dim=0, index=max_length_indices.data)

        reconstructions = self.decoder((x * y[:, :, None]).view(x.size(0), -1))
        return classes, reconstructions


if __name__ == '__main__':
    # Globals
    CUDA = True
    EPOCH = 10

    # Model
    model = CapsuleNet()

    if CUDA:
        model.cuda()

    optimizer = optim.Adam(model.parameters())

    margin_loss = MarginLoss()

    train_loader = torch.utils.data.DataLoader(
        MNIST(root='/tmp', download=True, train=True,
              transform=transforms.ToTensor()),
        batch_size=8, shuffle=True)

    test_loader = torch.utils.data.DataLoader(
        MNIST(root='/tmp', download=True, train=False,
              transform=transforms.ToTensor()),
        batch_size=8, shuffle=True)

    for e in range(10):
        # Training
        train_loss = 0

        model.train()
        for idx, (img, target) in enumerate(tqdm(train_loader, desc='Training')):
            img = Variable(img)
            target = Variable(index_to_one_hot(target))

            if CUDA:
                img = img.cuda()
                target = target.cuda()

            optimizer.zero_grad()

            classes, reconstructions = model(img, target)

            loss = margin_loss(img, target, classes, reconstructions)
            loss.backward()

            train_loss += loss.data.cpu()[0]

            optimizer.step()


        print('Training:, Avg Loss: {:.4f}'.format(train_loss))

        # # Testing
        correct = 0
        test_loss = 0

        model.eval()
        for idx, (img, target) in enumerate(tqdm(test_loader, desc='test set')):
            img = Variable(img)
            target_index = target
            target = Variable(index_to_one_hot(target))

            if CUDA:
                img = img.cuda()
                target = target.cuda()

            classes, reconstructions = model(img, target)

            test_loss += margin_loss(img, target, classes, reconstructions).data.cpu()

            # Get index of the max log-probability
            pred = classes.data.max(1, keepdim=True)[1].cpu()
            correct += pred.eq(target_index.view_as(pred)).cpu().sum()

        test_loss /= len(test_loader.dataset)
        correct = 100. * correct / len(test_loader.dataset)
        print('Test Set: Avg Loss: {:.4f}, Accuracy: {:.4f}'.format(
            test_loss[0], correct))