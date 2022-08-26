import numpy as np
from torchvision import transforms
from torch.utils.data.dataset import Dataset
import torchvision
import torch
import cv2
import random
import linecache
import os

class DatasetFromCSV(Dataset):
    def __init__(self,path,path2,transforms=None):
 
        self.data = open(path,"r").readlines()
       # self.num = open(path2,"r").readlines()
        self.transforms = transforms
    
    def __getitem__(self, index):
        tag=random.randint(0,1)
        if tag==1:
            now=random.randint(1,self.__len__()-2)
            img1 = self.data[now].strip("\n").split(",")
            while self.data[now-1].strip("\n").split(",")[0]!=img1[0] and self.data[now+1].strip("\n").split(",")[0]!=img1[0]:
                now=random.randint(1,self.__len__()-2)
                img1 = self.data[now].strip("\n").split(",")
            if self.data[now-1].strip("\n").split(",")[0]==img1[0]:
                img0=self.data[now-1].strip("\n").split(",")
            if self.data[now+1].strip("\n").split(",")[0]==img1[0]:
                img0=self.data[now+1].strip("\n").split(",")
        if tag==0:
            img1 = self.data[random.randint(0,self.__len__()-1)].strip("\n").split(",")
            img0 = self.data[random.randint(0,self.__len__()-1)].strip("\n").split(",")
            while img1[0]==img0[0]:
                img1 = self.data[random.randint(0,self.__len__()-1)].strip("\n").split(",")
                img0 = self.data[random.randint(0,self.__len__()-1)].strip("\n").split(",")
        img1= np.array(np.reshape(np.array(img1[1:]),(100,100)))
        img0= np.array(np.reshape(np.array(img0[1:]),(100,100)))
        img0 = img0.astype(np.float32)
        img1 = img1.astype(np.float32)
        if self.transforms is not None:
            img0 = self.transforms(img0)
            img1 = self.transforms(img1)
        return img0, img1, torch.from_numpy(np.array([tag], dtype=np.float32))

    def __len__(self):
        num = len(self.data)
        return num

batch_size_train = 1
batch_size_test = 128
transform = transforms.Compose([transforms.ToTensor()])
                                #transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225))])
#transform2 = transforms.Compose([transforms.ToTensor(),
#                                transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225))])
 
train_data= DatasetFromCSV(path="./data.csv",path2="./raw.csv",transforms=transform)
#test_data = DatasetFromCSV("./test",transform2)

train_loader = torch.utils.data.DataLoader(train_data,batch_size=batch_size_train,num_workers=15,pin_memory=True,shuffle=True)
#test_loader = torch.utils.data.DataLoader(test_data,batch_size=batch_size_test,num_workers=8,pin_memory=True)