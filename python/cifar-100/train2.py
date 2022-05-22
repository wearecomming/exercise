import torch
import data2
import data
import torch.nn as nn
import torch.nn.functional as F
from Google_model import GoogLeNet
import os
from torch.utils.tensorboard import SummaryWriter

def get_accuracy(output, target, batch_size): 
    corrects = (torch.max(output, 1)[1].view(target.size()).data == target.data).sum()    
    accuracy = 100.0 * corrects/batch_size    
    return accuracy.item()

learning_rate = 0.0002 
num_epochs = 100 
gramma=0.5
cnt1=0
cnt2=0
network = GoogLeNet(num_classes=100,aux_logits=True,init_weights=True)
network.load_state_dict(torch.load("./num.pt"))
device = torch.device("cuda:0")
network = network.to(device)
criterion = nn.CrossEntropyLoss() 
optimizer = torch.optim.Adam(network.parameters(), lr=learning_rate)
writer = SummaryWriter("./tf-logs/")
step=0
best_acc=0.0
optimizer = torch.optim.Adam(network.parameters(), lr=learning_rate)
for epoch in range(num_epochs):
    train_running_loss = 0.0
    train_acc = 0.0
    network.train()
    for i, (images, labels) in enumerate(data2.train_loader):
        step=step+1
        images = images.to(device)
        labels = labels.to(device)
        logits,ax1,ax2= network(images)
        loss0=criterion(logits, labels)
        loss1=criterion(ax1, labels)
        loss2=criterion(ax2, labels)
        loss=loss0 + loss1 * 0.3 + loss2 * 0.3
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        train_running_loss += loss.detach().item()
        train_acc += get_accuracy(logits, labels, data.batch_size_train)
    writer.add_scalar(tag="loss", scalar_value=train_running_loss / i,global_step=step)
    writer.add_scalar(tag="accuracy", scalar_value=train_acc/i,global_step=step)
    print('Epoch: %d | Loss: %.4f | Train Accuracy: %.2f' %(epoch, train_running_loss / i, train_acc/i))
    network.eval()
    test_acc = 0.0
    lossx=0
    with torch.no_grad(): 
        for i, (images, labels) in enumerate(data.test_loader):
            images = images.to(device)
            labels = labels.to(device)
            predictions = network(images)
            loss=criterion(predictions, labels)
            lossx=lossx+loss
            test_acc +=get_accuracy(predictions, labels, data.batch_size_test)
        print(test_acc/(i+1))
        writer.add_scalar(tag="test-loss", scalar_value=lossx/(i+1),global_step=epoch)
        writer.add_scalar(tag="test-accuracy", scalar_value=test_acc/(i+1),global_step=epoch)
        if test_acc > best_acc:
            best_acc = test_acc
            torch.save(network.state_dict(),"./num2.pt")
writer.close()
os.system("shutdown")
