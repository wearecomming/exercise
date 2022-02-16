from tkinter import Variable
import cv2
import numpy as np
from matplotlib import pyplot as plt
import torch
import torchvision
from torch.utils.data import DataLoader
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim

def fin(image):
    img = image
    image = cv2.GaussianBlur(image, (3, 3), 0)
    image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    Sobel_x = cv2.Sobel(image, cv2.CV_16S, 1, 0)
    absX = cv2.convertScaleAbs(Sobel_x)
    image = absX
    ret, image = cv2.threshold(image, 0, 255, cv2.THRESH_OTSU)
    kernelX = cv2.getStructuringElement(cv2.MORPH_RECT, (17, 5))
    image = cv2.morphologyEx(image, cv2.MORPH_CLOSE, kernelX)
    kernelX = cv2.getStructuringElement(cv2.MORPH_RECT, (20, 1))
    kernelY = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 19))
    image = cv2.dilate(image, kernelX)
    image = cv2.erode(image, kernelX)
    image = cv2.erode(image, kernelY)
    image = cv2.dilate(image, kernelY)
    image = cv2.medianBlur(image, 15)
    contours, tmp = cv2.findContours(
        image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    for item in contours:
        rect = cv2.boundingRect(item)
        x = rect[0]
        y = rect[1]
        weight = rect[2]
        height = rect[3]
        if weight > (height * 2):
            chepai = img[y:y + height, x:x + weight]
            return chepai


def cut(img):
    white = []
    black = []
    h, w = img.shape
    max_w = 0
    max_b = 0
    for i in range(w):
        num_w = 0
        num_b = 0
        for j in range(h):
            if img[j][i] == 255:
                num_w += 1
            else:
                num_b += 1
        white.append(num_w)
        black.append(num_b)
        max_w = max(num_w, max_w)
        max_b = max(num_b, max_b)
    ty = False
    if max_b > max_w:
        ty = True
    now = 1
    end = 2
    word = []
    while white[now]<black[now]:
        now+=1
    while now < w-2:
        start=now
        end = start+1
        while (white[end-1]<=white[end] or white[end+1]<=white[end] or white[end]>max_w*0.05) and end<w-2 and black[end]<max_b*0.95:
            end+=1
        if end-start>5:
            p = img[1:h,start:end]
            p = cv2.resize(p,(28,28))
            word1 = []
            word1.append(p)
            word.append(word1)
        now=end
        while white[now+1]<white[now] and now<w-2:
            now+=1
    return word

def get_GreenPlate_bin(pai_src):
    b, g, r = cv2.split(pai_src)   #分离B、G、R通道
    _, bin = cv2.threshold(g, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU) #大津法二值化
    return bin


def get_accuracy(output, target, batch_size): 
    corrects = (torch.max(output, 1)[1].view(target.size()).data == target.data).sum()    
    accuracy = 100.0 * corrects/batch_size    
    return accuracy.item()


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


if __name__ == '__main__':
    img = cv2.imread("E:\\exercise\\python\\0.png")
    img2 = fin(img)
    img4 = get_GreenPlate_bin(img2)
    #整块车牌结果储存在img4
    img3 = cut(img4)
    print(type(img3))
    img3 = np.array(img3)
    #img3是分割好的单个字符
    #以下是通过cnn识别车牌号码

  
    batch_size_train = 64
    batch_size_test = 1000
    train_loader = torch.utils.data.DataLoader(
    torchvision.datasets.MNIST('./data/', train=True, download=True,
                             transform=torchvision.transforms.Compose([
                               torchvision.transforms.ToTensor(),
                               torchvision.transforms.Normalize(
                                 (0.1307,), (0.3081,))
                             ])),
    batch_size=batch_size_train, shuffle=True)
    test_loader = torch.utils.data.DataLoader(
    torchvision.datasets.MNIST('./data/', train=False, download=True,
                             transform=torchvision.transforms.Compose([
                               torchvision.transforms.ToTensor(),
                               torchvision.transforms.Normalize(
                                 (0.1307,), (0.3081,))
                             ])),
    batch_size=batch_size_test, shuffle=True)
    
    learning_rate = 0.001    
    num_epochs = 5 
    network = net_work()
    network = network.to(torch.device("cpu"))
    criterion = nn.CrossEntropyLoss()    
    optimizer = torch.optim.Adam(network.parameters(), lr=learning_rate)
    for epoch in range(num_epochs):
        train_running_loss = 0.0
        train_acc = 0.0
        network = network.train()
        for i, (images, labels) in enumerate(train_loader):
            images = images.to(torch.device("cpu"))
            labels = labels.to(torch.device("cpu"))
            predictions = network(images)
            loss = criterion(predictions,labels)
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            train_running_loss += loss.detach().item()    
            train_acc += get_accuracy(predictions, labels, batch_size_train)
        network.eval()    
        print('Epoch: %d | Loss: %.4f | Train Accuracy: %.2f' %(epoch, train_running_loss / i, train_acc/i))
    
    y_pred = network(torch.Tensor(img3)).cpu( )
    y = y_pred.detach().numpy().tolist()
    for i in y:
        cnt=0
        for j in i:
            if j == 0:
                print(cnt)
                break
            cnt+=1

    ##test_acc=0.0
    #for i, (images, labels) in enumerate(test_loader, 0):    
    ##    images = images.to(torch.device("cpu"))    
   #     labels = labels.to(torch.device("cpu"))    
  #      outputs = network(images)    
 #       test_acc += get_accuracy(outputs, labels, batch_size_test)    

 #   print('Test Accuracy: %.2f'%( test_acc/i))

