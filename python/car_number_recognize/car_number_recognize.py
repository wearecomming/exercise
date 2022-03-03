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
import train

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


if __name__ == '__main__':
    img = cv2.imread("E:\exercise\python\car_number_recognize/0.png")
    img2 = fin(img)
    img4 = get_GreenPlate_bin(img2)
    #整块车牌结果储存在img4
    img3 = cut(img4)
    print(type(img3))
    img3 = np.array(img3)
    #img3是分割好的单个字符
    #以下是通过cnn识别车牌号码
    network = net_work()
    network.load_state_dict(torch.load("E:\exercise\python\handwrite_number_recognize/num.pt"))
    white =0
    black=0
    for img in img3:
        for i in range(0,28):
            for j in range(0,28):
                if img[0][i][j]==255:
                    white += 1
                else:
                    black+=1
        if white>black:
            img = cv2.bitwise_not(img)
    network.eval()
    y=network(torch.Tensor(img3)).cpu( )
    y = y.detach().numpy().tolist()
    minaaa=0
    for j in y:
        cnt = 0
        minaaa = 9999999
        ans = 0
        for i in j:
            if abs(i)<minaaa:
                minaaa = abs(i)
                ans = cnt
            cnt+=1
        print(ans)

