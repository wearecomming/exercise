import numpy as np
from PIL import Image
from torchvision import transforms
from torch.utils.data.dataset import Dataset
import torchvision
import pickle
import torch
import cv2
import random

def load_file(filename):
    with open(filename,'rb') as fo:data=pickle.load(fo,encoding='latin1')
    return data


datas = load_file("./train")
lens = len(datas["fine_labels"])
all_dic={"fine_labels":[],"data":[]}
for i in range(0,lens):
        item=datas["data"][i]
        rx=[]
        rx.append((np.asarray(item[0:1024]).reshape(32,32)))
        rx.append((np.asarray(item[1024:2048]).reshape(32,32)))
        rx.append((np.asarray(item[2048:3072]).reshape(32,32)))
        rx = np.array(rx).swapaxes(0,1).swapaxes(1,2).astype('uint8')
        flipped_img = np.fliplr(rx)
        all_dic["fine_labels"].append(datas["fine_labels"][i])
        all_dic["data"].append(flipped_img)
        flipped_img = np.power(rx,random.uniform(0.8, 1.2))
        all_dic["fine_labels"].append(datas["fine_labels"][i])
        all_dic["data"].append(flipped_img)

np.save('new_train.npy', all_dic)