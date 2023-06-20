# -*- coding: utf-8 -*-
"""EfficientNet_b0.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1xPkH0jqAnxlCUrL1rNwrL2s51rluuYoT

Skeleton code is provided from the following tutorial: https://pytorch.org/tutorials/beginner/blitz/cifar10_tutorial.html
"""

import torch
import torchvision
import torchvision.transforms as transforms

from google.colab import drive
drive.mount('/content/drive')

# Write one custom transform: RandomHorizontalFlip

from PIL import Image
import random

class RandomHorizontalFlip(object):
    """Horizontally flip the given PIL Image randomly with a given probability.
    Args:
        p (float): probability of the image being flipped. Default value is 0.5
    """

    def __init__(self, p=0.5):
        self.p = p
    
    def __call__(self, img):
        """
        Args:
            img (PIL Image): Image to be flipped.
        Returns:
            PIL Image: Randomly flipped image.
        """
        if random.random() < self.p:
            img = img.transpose(Image.FLIP_LEFT_RIGHT)

        return img

"""Dataset: https://pytorch.org/docs/stable/_modules/torchvision/datasets/cifar.html#CIFAR100"""

batch_size = 256
input_size=32

data_transforms = {
    'train': transforms.Compose([
        RandomHorizontalFlip(0.5),
        transforms.RandomCrop(32, 4),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ]),
    'test': transforms.Compose([
        transforms.Resize(input_size),
        transforms.CenterCrop(input_size),
        transforms.ToTensor(),
        transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
    ]),
}

trainset = torchvision.datasets.CIFAR100(root='./data/CIFAR100', train=True,
                                        download=True, transform=data_transforms["train"])

trainloader = torch.utils.data.DataLoader(trainset, batch_size=batch_size,
                                          shuffle=True, num_workers=2)

testset = torchvision.datasets.CIFAR100(root='./data/CIFAR100', train=False,
                                       download=True, transform=data_transforms["test"])

valset, testset = torch.utils.data.random_split(testset, [5000, 5000])

testloader = torch.utils.data.DataLoader(testset, batch_size=batch_size,
                                         shuffle=False, num_workers=2)
validloader = torch.utils.data.DataLoader(valset, batch_size=batch_size,
                                         shuffle=False, num_workers=2)

classes = ('apples', 'aquarium fish', 'baby', 'bear', 'beaver', 'bed', 'bee', 'beetle', 'bicycle', 'bottles', 
           'bowls', 'boy', 'bridge', 'bus', 'butterfly', 'camel', 'cans', 'castle', 'caterpillar', 'cattle', 'chair', 
           'chimpanzee', 'clock', 'cloud', 'cockroach', 'computer keyboard', 'couch', 'crab', 'crocodile', 
           'cups', 'dinosaur', 'dolphin', 'elephant', 'flatfish', 'forest', 'fox', 'girl', 'hamster', 'house', 
           'kangaroo', 'lamp', 'lawn-mower', 'leopard', 'lion', 'lizard', 'lobster', 'man', 'maple', 'motorcycle', 
           'mountain', 'mouse', 'mushrooms', 'oak', 'oranges', 'orchids', 'otter', 'palm', 'pears', 'pickup truck', 
           'pine', 'plain', 'plates', 'poppies', 'porcupine', 'possum', 'rabbit', 'raccoon', 'ray', 'road', 'rocket', 
           'roses', 'sea', 'seal', 'shark', 'shrew', 'skunk', 'skyscraper', 'snail', 'snake', 'spider', 'squirrel', 
           'streetcar', 'sunflowers', 'sweet peppers', 'table', 'tank', 'telephone', 'television', 'tiger', 'tractor',
           'train', 'trout', 'tulips', 'turtle', 'wardrobe', 'whale', 'willow', 'wolf', 'woman', 'worm')

print(testset)
print(valset)

# let's visualize some examples
import matplotlib.pyplot as plt
import numpy as np

def imshow(img):
    img = img / 2 + 0.5     # unnormalize
    npimg = img.numpy()
    plt.imshow(np.transpose(npimg, (1, 2, 0)))
    plt.show()

# get some random training images
dataiter = iter(testloader)
images, labels = dataiter.next()

print(len(trainloader))
print(images.shape)
print(labels.shape)
print(labels)
# show images
imshow(torchvision.utils.make_grid(images))
# print labels
print(' '.join('%5s' % classes[labels[j]] for j in range(batch_size)))

# if you want to train on GPU:
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")

print(device)

# code source : 
# https://github.com/aladdinpersson/Machine-Learning-Collection/blob/master/ML/Pytorch/CNN_architectures/pytorch_efficientnet.py
# article : https://arxiv.org/pdf/1905.11946.pdf

import torch
import torch.nn as nn
from math import ceil

base_model = [
    # expand_ratio, channels, repeats, stride, kernel_size
    [1, 16, 1, 1, 3],
    [6, 24, 2, 2, 3],
    [6, 40, 2, 2, 5],
    [6, 80, 3, 2, 3],
    [6, 112, 3, 1, 5],
    [6, 192, 4, 2, 5],
    [6, 320, 1, 1, 3],
]

phi_values = {
    # tuple of: (phi_value, resolution, drop_rate)
    "b0": (0, 224, 0.2),  # alpha, beta, gamma, depth = alpha ** phi
    "b1": (0.5, 240, 0.2),
    "b2": (1, 260, 0.3),
    "b3": (2, 300, 0.3),
    "b4": (3, 380, 0.4),
    "b5": (4, 456, 0.4),
    "b6": (5, 528, 0.5),
    "b7": (6, 600, 0.5),
}

class CNNBlock(nn.Module):
    def __init__(
            self, in_channels, out_channels, kernel_size, stride, padding, groups=1
    ):
        super(CNNBlock, self).__init__()
        self.cnn = nn.Conv2d(
            in_channels,
            out_channels,
            kernel_size,
            stride,
            padding,
            groups=groups,
            bias=False,
        )
        self.bn = nn.BatchNorm2d(out_channels)
        self.silu = nn.SiLU() # SiLU <-> Swish

    def forward(self, x):
        return self.silu(self.bn(self.cnn(x)))

class SqueezeExcitation(nn.Module):
    def __init__(self, in_channels, reduced_dim):
        super(SqueezeExcitation, self).__init__()
        self.se = nn.Sequential(
            nn.AdaptiveAvgPool2d(1), # C x H x W -> C x 1 x 1
            nn.Conv2d(in_channels, reduced_dim, 1),
            nn.SiLU(),
            nn.Conv2d(reduced_dim, in_channels, 1),
            nn.Sigmoid(),
        )

    def forward(self, x):
        return x * self.se(x)

class InvertedResidualBlock(nn.Module):
    def __init__(
            self,
            in_channels,
            out_channels,
            kernel_size,
            stride,
            padding,
            expand_ratio,
            reduction=4, # squeeze excitation
            survival_prob=0.8, # for stochastic depth
    ):
        super(InvertedResidualBlock, self).__init__()
        self.survival_prob = 0.8
        self.use_residual = in_channels == out_channels and stride == 1
        hidden_dim = in_channels * expand_ratio
        self.expand = in_channels != hidden_dim
        reduced_dim = int(in_channels / reduction)

        if self.expand:
            self.expand_conv = CNNBlock(
                in_channels, hidden_dim, kernel_size=3, stride=1, padding=1,
            )

        self.conv = nn.Sequential(
            CNNBlock(
                hidden_dim, hidden_dim, kernel_size, stride, padding, groups=hidden_dim,
            ),
            SqueezeExcitation(hidden_dim, reduced_dim),
            nn.Conv2d(hidden_dim, out_channels, 1, bias=False),
            nn.BatchNorm2d(out_channels),
        )

    def stochastic_depth(self, x):
        if not self.training:
            return x

        binary_tensor = torch.rand(x.shape[0], 1, 1, 1, device=x.device) < self.survival_prob
        return torch.div(x, self.survival_prob) * binary_tensor

    def forward(self, inputs):
        x = self.expand_conv(inputs) if self.expand else inputs

        if self.use_residual:
            return self.stochastic_depth(self.conv(x)) + inputs
        else:
            return self.conv(x)


class EfficientNet(nn.Module):
    def __init__(self, version, num_classes):
        super(EfficientNet, self).__init__()
        width_factor, depth_factor, dropout_rate = self.calculate_factors(version)
        last_channels = ceil(1280 * width_factor)
        self.pool = nn.AdaptiveAvgPool2d(1)
        self.features = self.create_features(width_factor, depth_factor, last_channels)
        self.classifier = nn.Sequential(
            nn.Dropout(dropout_rate),
            nn.Linear(last_channels, num_classes),
        )

    def calculate_factors(self, version, alpha=1.2, beta=1.1):
        phi, res, drop_rate = phi_values[version]
        depth_factor = alpha ** phi
        width_factor = beta ** phi
        return width_factor, depth_factor, drop_rate

    def create_features(self, width_factor, depth_factor, last_channels):
        channels = int(32 * width_factor)
        features = [CNNBlock(3, channels, 3, stride=2, padding=1)]
        in_channels = channels

        for expand_ratio, channels, repeats, stride, kernel_size in base_model:
            out_channels = 4*ceil(int(channels*width_factor) / 4)
            layers_repeats = ceil(repeats * depth_factor)

            for layer in range(layers_repeats):
                features.append(
                    InvertedResidualBlock(
                        in_channels,
                        out_channels,
                        expand_ratio=expand_ratio,
                        stride = stride if layer == 0 else 1,
                        kernel_size=kernel_size,
                        padding=kernel_size//2, # if k=1:pad=0, k=3:pad=1, k=5:pad=2
                    )
                )
                in_channels = out_channels

        features.append(
            CNNBlock(in_channels, last_channels, kernel_size=1, stride=1, padding=0)
        )

        return nn.Sequential(*features)

    def forward(self, x):
        x = self.pool(self.features(x))
        return self.classifier(x.view(x.shape[0], -1))


def effnetb0(num_classes=100):
    version = "b0"
    return EfficientNet(
        version=version,
        num_classes=num_classes,
    ).to(device)


def effnetb1(num_classes=100):
    version = "b1"
    return EfficientNet(
        version=version,
        num_classes=num_classes,
    ).to(device)

learning_rate = 0.01
weight_decay = 5e-5

model = effnetb0(num_classes=100)

model.to(device)

model.train()

# base optimizer with following parameters:
import torch.optim as optim

criterion = nn.CrossEntropyLoss()
optimizer = optim.SGD(model.parameters(), lr=learning_rate, momentum=0.9, weight_decay=weight_decay)
lr_scheduler = torch.optim.lr_scheduler.MultiStepLR(
    optimizer,
    milestones=[100, 150],
    last_epoch=-1)

import os

def create_dir(_dir):
    """
    Creates given directory if it is not present.
    """
    if not os.path.exists(_dir):
        os.makedirs(_dir)

def save_checkpoint(state, filename):
    """
    Save the training model
    """
    create_dir(os.path.dirname(filename))
    torch.save(state, filename)
    
def train_one_epoch(trainloader, optimizer, criterion, model, epoch):
    """
    Train model for one epoch
    """
    running_loss = 0.0
    for i, data in enumerate(trainloader, 0):
        # get the inputs; data is a list of [inputs, labels]
        inputs, labels = data[0].to(device), data[1].to(device)

        # zero the parameter gradients
        optimizer.zero_grad()

        # forward + backward + optimize
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item()

    # print statistics
    if epoch % 5 == 0:
      print('[%d, %5d] loss: %.3f' %
            (epoch+1, i+1, running_loss/len(trainloader)))
      running_loss = 0.0

SAVE_DIR = '/content/drive/MyDrive/Data/SoupTrainedModels/EfficientNet'

#hyperparameter configuration. the paper searched over learning rate, weight-decay,
#iterations, data augmentation, mixup, and label smoothing
#0.001
lr = [0.01]
wd = [5e-5] 
#starting training for: effnetb0_std_lr0.01_wd5e-05
filenames = []
save_every = 60
num_epoch = 10
for j in range(len(wd)):
    for i in range(len(lr)):

        model = effnetb0(num_classes=100)
        model.to(device)
        model.train()
        
        save_dir = "checkpoints/"
        save_name = "effnetb0_std" + "_lr" + str(lr[i]) + "_wd" + str(wd[j])
        filenames.append(save_name)
        print("starting training for: " + save_name)
        
        criterion = nn.CrossEntropyLoss()
        optimizer = optim.SGD(model.parameters(), lr=lr[i], momentum=0.9, weight_decay=wd[j])

        #optimizer = optim.Adam(model.parameters(), lr=learning_rate, betas=(0.9,0.999), weight_decay=weight_decay)
        lr_scheduler = torch.optim.lr_scheduler.MultiStepLR(
            optimizer,
            milestones=[40, 80],
            last_epoch=-1)

        # Training loop
        for epoch in range(num_epoch):  # loop over the dataset multiple times

            # train
            train_one_epoch(
                trainloader=trainloader,
                optimizer=optimizer,
                criterion=criterion,
                model=model,
                epoch=epoch
            )

            # save checkpoint every save_every epochs
            if epoch > 0 and epoch % save_every == 0:
                save_checkpoint(
                    state={
                        'epoch': epoch + 1,
                        'state_dict': model.state_dict(),
                    },
                    filename=os.path.join(save_dir, save_name+'_checkpoint.th')
                )
            
            lr_scheduler.step()

        # save final model
        save_checkpoint(
            state={
                'state_dict': model.state_dict(),
            },
            filename=os.path.join(save_dir, save_name+'_final.th')
        )



print('Finished Training')

"""# New Section"""

# test on all test data
lr = [0.01] 
wd = [5e-5]
#starting training for: effnetb0_std_lr0.02_wd2e-05
accuracies = torch.zeros((len(lr),len(wd)))
for j in range(len(wd)):
    for i in range(len(lr)):
        filename = "effnetb0_std" +  "_lr" + str(lr[i]) + "_wd" + str(wd[j]) + "_final.th"
        PATH="checkpoints/" + filename
        model.load_state_dict(torch.load(PATH)["state_dict"])
        model.eval()
        correct = 0
        total = 0
        with torch.no_grad():
            for data in testloader:
                images, labels = data[0].to(device), data[1].to(device)
                outputs = model(images)
                _, predicted = torch.max(outputs.data, 1)
                total += labels.size(0)
                correct += (predicted == labels).sum().item()

        print(correct)
        print(total)
        accuracies[i,j] = ((100 * correct / total))
        print('Accuracy of %s on the 10000 test images: %d %%' % (filename, (100 * correct / total)))
print(accuracies)

dataiter = iter(testloader)
images, labels = dataiter.next()

outputs = model(images.cuda())
_, predicted = torch.max(outputs.data, 1)
# print images
imshow(torchvision.utils.make_grid(images))
print('GroundTruth: ', ' '.join('%5s' % classes[labels[j]] for j in range(batch_size)))
print('Predicted: ', ' '.join('%5s' % classes[predicted[j]]for j in range(batch_size)))

#dowloading the file from pickled models
!zip -r /content/checkpoints.zip /content/checkpoints
from google.colab import files
files.download("/content/checkpoints.zip")

filename = filename = "effnetb0_std" +  "_lr" + str(lr[0]) + "_wd" + str(wd[0]) + "_final.th"
PATH = "/content/checkpoints/"+  filename
model.load_state_dict(torch.load(PATH)["state_dict"])
model.eval()
correct = 0
total = 0
with torch.no_grad():
    for data in validloader:
        images, labels = data[0].to(device), data[1].to(device)
        outputs = model(images)
        _, predicted = torch.max(outputs.data, 1)
        total += labels.size(0)
        correct += (predicted == labels).sum().item()

print(correct)
print(total)
# accuracies[i,j] = ((100 * correct / total))
print('Accuracy of %s on the 10000 test images: %d %%' % (filename, (100 * correct / total)))

weights = [param.data for param in model.parameters()]
print(weights)