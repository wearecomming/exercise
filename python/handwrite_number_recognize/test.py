import torch
import dataload

import torch.nn as nn
import torch.nn.functional as F


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


def get_accuracy(output, target, batch_size): 
    corrects = (torch.max(output, 1)[1].view(target.size()).data == target.data).sum()    
    accuracy = 100.0 * corrects/batch_size    
    return accuracy.item()


network = torch.load("E:\exercise\python\handwrite_number_recognize/num.pt", map_location=torch.device('cpu'))
test_acc=0.0
for i, (images, labels) in enumerate(dataload.test_loader, 0):    
    images = images.to(torch.device("cpu"))    
    labels = labels.to(torch.device("cpu"))    
    outputs = network(images)    
    test_acc += get_accuracy(outputs, labels, dataload.batch_size_test)    

print('Test Accuracy: %.2f'%( test_acc/i))