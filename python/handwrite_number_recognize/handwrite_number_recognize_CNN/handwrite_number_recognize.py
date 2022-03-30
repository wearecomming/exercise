import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy
import dataload
import csv


class net_work(nn.Module):
    def __init__(self):
        super(net_work, self).__init__()
        self.conv1 = nn.Conv2d(1,10,5)
        self.pool1 = nn.MaxPool2d(2,2)
        self.conv2 = nn.Conv2d(10,20,5)
        self.pool2 = nn.MaxPool2d(2,2)
        self.conv2_drop = nn.Dropout2d(p=0.2)
        self.fc1 = nn.Linear(320,50)
        self.fc2 = nn.Linear(50,10)
    def forward(self,input):
        x = self.pool1(F.relu(self.conv1(input)))
        x = self.pool2(F.relu(self.conv2_drop(self.conv2(x))))
        x = x.view(-1,320)
        x = F.relu(self.fc1(x))
        x = F.dropout(x, training=self.training)
        x = self.fc2(x)
        return F.log_softmax(x)


csvFile = open("E:\exercise\python\handwrite_number_recognize\handwrite_number_recognize_CNN/test_submit.csv", "w")
writer = csv.writer(csvFile)
writer.writerow(["ImageId","Label"])
network = net_work()

network.load_state_dict(torch.load("E:\exercise\python\handwrite_number_recognize\handwrite_number_recognize_CNN/num.pt"))
cnt=0
for i,(images,labels) in enumerate(dataload.test_loader):
    images = images.to(torch.device("cpu"))
    predictions = network(images)
    max_value,index = torch.max(predictions,1)
    for dex in index.tolist():
        cnt+=1
        writer.writerow([cnt,dex])
csvFile.close()