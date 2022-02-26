import torch
import downloaddata
import torch.nn as nn
import torch.nn.functional as F


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

def get_accuracy(output, target, batch_size): 
    corrects = (torch.max(output, 1)[1].view(target.size()).data == target.data).sum()    
    accuracy = 100.0 * corrects/batch_size    
    return accuracy.item()

learning_rate = 0.001    
num_epochs = 5 
network = net_work()
network = network.to(torch.device("cpu"))
criterion = nn.CrossEntropyLoss()    
optimizer = torch.optim.Adam(network.parameters(), lr=learning_rate)
for epoch in range(num_epochs):
    train_running_loss = 0.0
    train_acc = 0.0
    network = network.train()
    for i, (images, labels) in enumerate(downloaddata.train_loader):
        images = images.to(torch.device("cpu"))
        labels = labels.to(torch.device("cpu"))
        predictions = network(images)
        loss = criterion(predictions,labels)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        train_running_loss += loss.detach().item()
        train_acc += get_accuracy(predictions, labels, downloaddata.batch_size_train)
    network.eval()
    print('Epoch: %d | Loss: %.4f | Train Accuracy: %.2f' %(epoch, train_running_loss / i, train_acc/i))
test_acc=0.0
for i, (images, labels) in enumerate(downloaddata.test_loader, 0):    
    images = images.to(torch.device("cpu"))    
    labels = labels.to(torch.device("cpu"))    
    outputs = network(images)    
    test_acc += get_accuracy(outputs, labels, downloaddata.batch_size_test)
print('Test Accuracy: %.2f'%( test_acc/(i+1)))
torch.save(network.state_dict(),"E:\exercise\python\handwrite_number_recognize/num.pt")