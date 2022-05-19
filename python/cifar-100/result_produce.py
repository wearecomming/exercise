import numpy as np
from PIL import Image
from torchvision import transforms
from torch.utils.data.dataset import Dataset
import torchvision
import pickle
import torch
from Google_model import GoogLeNet
import data

def load_file(filename):
    with open(filename,'rb') as fo:data=pickle.load(fo,encoding='latin1')
    return data


datas = load_file("./test")
lab = load_file("./meta")
network = GoogLeNet(num_classes=100,aux_logits=True,init_weights=True) 
network.load_state_dict(torch.load("./num.pt"))
network = network.cuda()
network.eval()
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
with torch.no_grad(): 
    for i, (images, labels) in enumerate(data.test_loader):
        images = images.to(device)
        labels = labels.to(device)
        predictions = network(images)
        print(type(predictions))
        break