import torch
import torch.nn as nn
import torch.nn.functional as F
import numpy
import cv2


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


network = net_work()
network.load_state_dict(torch.load("E:\exercise\python\handwrite_number_recognize/num.pt"))
img = cv2.imread("E:\exercise\python\handwrite_number_recognize/1111.jpg",cv2.IMREAD_GRAYSCALE)
img = cv2.resize(img,(28,28))
ret, img = cv2.threshold(img, 0, 255, cv2.THRESH_OTSU)
white =0
black=0
for i in range(0,28):
    for j in range(0,28):
        if img[i][j]==255:
            white += 1
        else:
            black+=1
if white>black:
    img = cv2.bitwise_not(img)
cv2.imshow("111,",img)
cv2.waitKey(0)
network.eval()
x = []
x.append(img)
xx = []
xx.append(x)
xx = numpy.array(xx)
y=network(torch.Tensor(xx)).cpu( )
cnt = 0
y = y.detach().numpy().tolist()
mina = 9999999
ans = 0
for i in y[0]:
    if abs(i)<mina:
        mina = abs(i)
        ans = cnt
    cnt+=1
print(ans)