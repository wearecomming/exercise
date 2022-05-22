import numpy as np
from PIL import Image
from torchvision import transforms
from torch.utils.data.dataset import Dataset
import torchvision
import pickle
import torch

class DatasetFromCSV(Dataset):
    def __init__(self,transforms=None):
 
        self.data = np.load('new_train.npy',allow_pickle=True)
        self.labels = self.data.item()["fine_labels"]
        self.transforms = transforms
        
    
    def __getitem__(self, index):
        single_image_label = self.labels[index]
        item=self.data.item()["data"][index]
        im=Image.fromarray(item.astype('uint8')).convert('RGB').resize((224,224))
        im=np.array(im)
        # 将图像转换成 tensor
        if self.transforms is not None:
            img_as_tensor = self.transforms(im)
            # 返回图像及其 label
        return (img_as_tensor, single_image_label)
    
    
    def __len__(self):
        return len(self.data.item()["data"])
    

#dataset = torchvision.datasets.CIFAR100(root='./python/craft100/cifar_data_test',download=True)
batch_size_train = 128
batch_size_test = 128
transform = transforms.Compose([transforms.ToTensor(),
                                transforms.RandomHorizontalFlip(p=0.5),
                                transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225))])
 
train_data= DatasetFromCSV(transform)

train_loader = torch.utils.data.DataLoader(train_data,batch_size=batch_size_train,num_workers=8,pin_memory=True,shuffle=True)
