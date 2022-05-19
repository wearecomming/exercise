import torch
import torch.nn as nn
import torch.nn.functional as F
from Google_model import GoogLeNet
import data
import os
from torch.utils.tensorboard import SummaryWriter

def get_accuracy(output, target, batch_size): 
    corrects = (torch.max(output, 1)[1].view(target.size()).data == target.data).sum()    
    accuracy = 100.0 * corrects/batch_size    
    return accuracy.item()

test_acc = 0.0
network = GoogLeNet(num_classes=100,aux_logits=True,init_weights=True) 
network.load_state_dict(torch.load("./num.pt"))
network = network.cuda()
network.eval()
device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
writer = SummaryWriter("./tf-logs/")
criterion = nn.CrossEntropyLoss() 
step=0
with torch.no_grad(): 
    for i, (images, labels) in enumerate(data.test_loader):
        step=step+1
        images = images.to(device)
        labels = labels.to(device)
        predictions = network(images)
        loss=criterion(predictions, labels)
        writer.add_scalar(tag="test-loss", scalar_value=loss,global_step=step)
        x=get_accuracy(predictions, labels, data.batch_size_test)
        test_acc += x
        writer.add_scalar(tag="test-accuracy", scalar_value=x,global_step=step)
print(test_acc/(i+1))
f = open('ans.txt','w')
f.write(str(test_acc/(i+1)))
f.close()
writer.close()
os.system("shutdown")