import pandas
import numpy as np
import pandas as pd
from PIL import Image
from torch import optim,nn
import torch.nn.functional as F
from torchvision import transforms
from torch.utils.data.dataset import Dataset
import torch


class DatasetFromCSV(Dataset):
    def __init__(self, csv_path, height, width, transforms=None):
 
        self.data = pd.read_csv(csv_path)
        self.labels = np.asarray(self.data.iloc[:, 0])
        self.height = height
        self.width = width
        self.transforms = transforms
        
    
    def __getitem__(self, index):
        single_image_label = self.labels[index]
        # 读取所有像素值，并将 1D array ([784]) reshape 成为 2D array ([28,28])
        img_as_np = np.asarray(self.data.iloc[index][0:]).reshape(28, 28).astype(float)
        # 把 numpy array 格式的图像转换成灰度 PIL image
        img_as_img = Image.fromarray(img_as_np)
        img_as_img = img_as_img.convert('L')
        # 将图像转换成 tensor
        if self.transforms is not None:
            img_as_tensor = self.transforms(img_as_img)
            # 返回图像及其 label
        return (img_as_tensor, single_image_label)
    
    def __len__(self):
        return len(self.data.index)
    
    
batch_size_train = 96
batch_size_test = 96
transform = transforms.Compose([transforms.ToTensor(),
                                transforms.Normalize((0.5,),(0.5,))])
 
train_data= DatasetFromCSV('E:\exercise\python\handwrite_number_recognize\handwrite_number_recognize_CNN/train.csv', 28,28,transform)
test_data = DatasetFromCSV("E:\exercise\python\handwrite_number_recognize\handwrite_number_recognize_CNN/test.csv",28,28,transform)

train_loader = torch.utils.data.DataLoader(train_data,batch_size=batch_size_train)
test_loader = torch.utils.data.DataLoader(test_data,batch_size=batch_size_test)
 
