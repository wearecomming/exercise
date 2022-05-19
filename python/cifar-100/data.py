import numpy as np
from PIL import Image
from torchvision import transforms
from torch.utils.data.dataset import Dataset
import torchvision
import pickle
import torch

def load_file(filename):
    with open(filename,'rb') as fo:data=pickle.load(fo,encoding='latin1')
    return data

class DatasetFromCSV(Dataset):
    def __init__(self,path,transforms=None):
 
        self.data = load_file(path)
        self.labels = self.data["fine_labels"]
        self.transforms = transforms
        
    
    def __getitem__(self, index):
        single_image_label = self.labels[index]
        item=self.data["data"][index]
        rx=[]
        rx.append((np.asarray(item[0:1024]).reshape(32,32)))
        rx.append((np.asarray(item[1024:2048]).reshape(32,32)))
        rx.append((np.asarray(item[2048:3072]).reshape(32,32)))
        im=Image.fromarray(np.array(rx).swapaxes(0,1).swapaxes(1,2).astype('uint8')).convert('RGB').resize((224,224))
        im=np.array(im)
        # 将图像转换成 tensor
        if self.transforms is not None:
            img_as_tensor = self.transforms(im)
            # 返回图像及其 label
        return (img_as_tensor, single_image_label)
    
    
    def __len__(self):
        return len(self.data["data"])
    

#dataset = torchvision.datasets.CIFAR100(root='./python/craft100/cifar_data_test',download=True)
batch_size_train = 128
batch_size_test = 128
transform = transforms.Compose([transforms.ToTensor(),
                                transforms.RandomHorizontalFlip(p=0.5),
                                transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225))])
transform2 = transforms.Compose([transforms.ToTensor(),
                                transforms.Normalize((0.485, 0.456, 0.406), (0.229, 0.224, 0.225))])
 
train_data= DatasetFromCSV("./train",transform)
test_data = DatasetFromCSV("./test",transform2)

train_loader = torch.utils.data.DataLoader(train_data,batch_size=batch_size_train,num_workers=8,pin_memory=True,shuffle=True)
test_loader = torch.utils.data.DataLoader(test_data,batch_size=batch_size_test,num_workers=8,pin_memory=True)
