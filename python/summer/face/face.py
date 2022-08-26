from simlarnet import simlarnett
import numpy as np
import torchvision
import torch
import cv2
import torch.optim as optim
from torch.autograd import Variable
import torch.nn.functional as F
import numpy as np
from torchvision import transforms

def change(img):
    h,w=img.shape
    if h>w:
        img = cv2.copyMakeBorder(img,0,0,h-w,0,cv2.BORDER_CONSTANT,value=0)
    if w>h:   
        img = cv2.copyMakeBorder(img,w-h,0,0,0,cv2.BORDER_CONSTANT,value=0)
    img=cv2.resize(img,(100,100))
    return img
def recognize(pth1,pth2):
    net = torch.load("model.pth").cuda()
    net.eval()
    transform = transforms.Compose([transforms.ToTensor(),transforms.Resize ((100,100))])
    img1=cv2.imread(pth1,cv2.IMREAD_GRAYSCALE)
    img2=cv2.imread(pth2,cv2.IMREAD_GRAYSCALE)
    img1=change(img1)
    igm2=change(img2)
    img1=np.array(img1)
    img2=np.array(img2)
    img1 = img1.astype(np.float32)
    img2 = img2.astype(np.float32)
    img1=transform(img1)
    img2=transform(img2)
    img1= Variable(img1.unsqueeze(0)).cuda()
    img2= Variable(img2.unsqueeze(0)).cuda()
    output1, output2 = net(img1, img2)
    euclidean_distance = F.pairwise_distance(output1, output2)
    diff=euclidean_distance.cpu().detach().numpy()[0]
    if diff<=0.5:
        return True
    else :
        return False