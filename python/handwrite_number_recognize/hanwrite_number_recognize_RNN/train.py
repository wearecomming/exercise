import torch
import torch.nn as nn
import dataload

class net_work(nn.Module):
    def __init__(self):
        super(net_work, self).__init__()
        self.rnn = nn.LSTM(input_size=28,hidden_size=128,num_layers=2,batch_first=True)
        self.out = nn.Linear(128,10)
        
    def forward(self,x):
        r,xx = self.rnn(x)
        out = self.out(r[:,-1,:])
        return out
    
def get_accuracy(output, target, batch_size): 
    corrects = (torch.max(output, 1)[1].view(target.size()).data == target.data).sum()    
    accuracy = 100.0 * corrects/batch_size    
    return accuracy.item()

learning_rate = 0.002
gramma = 0.1
cnt1=0
cnt2=0
num_epochs = 7
network = net_work()
network = network.to(torch.device("cpu"))
criterion = nn.CrossEntropyLoss()    
optimizer = torch.optim.Adam(network.parameters(), lr=learning_rate)
for epoch in range(num_epochs):
    train_running_loss = 0.0
    train_acc = 0.0
    network = network.train()
    if epoch > 4 and cnt1==0:
        cnt1=1
        learning_rate*=gramma
        optimizer = torch.optim.Adam(network.parameters(), lr=learning_rate)
    if epoch > 9 and cnt2==0:
        cnt2=1
        learning_rate*=gramma
        optimizer = torch.optim.Adam(network.parameters(), lr=learning_rate)
    for i, (images, labels) in enumerate(dataload.train_loader):
        images = images.to(torch.device("cpu"))
        labels = labels.to(torch.device("cpu"))
        images = images.view(-1,28,28)
        predictions = network(images)
        loss = criterion(predictions,labels)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        train_running_loss += loss.detach().item()
        train_acc += get_accuracy(predictions, labels, dataload.batch_size_train)
    print('Epoch: %d | Loss: %.4f | Train Accuracy: %.2f' %(epoch, train_running_loss / i, train_acc/i))
network.eval()
torch.save(network.state_dict(),"E:\exercise\python\handwrite_number_recognize\hanwrite_number_recognize_RNN/num.pt")