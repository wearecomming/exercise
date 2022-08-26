from simlarnet import simlarnett
import numpy as np
import torchvision
import torch
import cv2
import data
import torch.optim as optim
from torch.autograd import Variable
import os
import torch.nn.functional as F



class ContrastiveLoss(torch.nn.Module):
    def __init__(self, margin=2.0):
        super(ContrastiveLoss, self).__init__()
        self.margin = margin
 
    def forward(self, output1, output2, label):
        euclidean_distance = F.pairwise_distance(output1, output2)
        loss_contrastive = torch.mean((label) * torch.pow(euclidean_distance, 2) +
                                      (1-label) * torch.pow(torch.clamp(self.margin - euclidean_distance, min=0.0), 2))
        return loss_contrastive*0.5

    
net = simlarnett().cuda()
criterion = ContrastiveLoss()
optimizer = optim.Adam(net.parameters(), lr=0.0005)
 
counter = []
loss_history = []
iteration_number = 0
def get_accuracy(output1,output2, target, batch_size): 
    euclidean_distance = F.pairwise_distance(output1, output2)
    accuracy = 100.0 * corrects/batch_size    
    return accuracy.item()

train_acc=0
for epoch in range(0, 100):
    for i, datas in enumerate(data.train_loader):
        img0, img1, label = datas
        img0, img1, label = Variable(img0).cuda(), Variable(img1).cuda(), Variable(label).cuda()
        output1, output2 = net(img0, img1)
        optimizer.zero_grad()
        loss_contrastive = criterion(output1, output2, label)
        loss_contrastive.backward()
        optimizer.step()
       #train_acc += get_accuracy(output1,output2, label, data.batch_size_train)
    print("Epoch:{},  Current loss {}\n".format(epoch, loss_contrastive.item()))
        #iteration_number += 10
        #counter.append(iteration_number)
        #loss_history.append(loss_contrastive.item())
torch.save(net,'./model.pth')
os.system("shutdown")