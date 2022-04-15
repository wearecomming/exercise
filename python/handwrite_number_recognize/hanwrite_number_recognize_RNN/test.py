import downloaddata
import dataload
import torch
import torch.nn as nn

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

test_acc = 0.0
network = net_work()
network.load_state_dict(torch.load("E:\exercise\python\handwrite_number_recognize\hanwrite_number_recognize_RNN/num.pt"))
for i, (images, labels) in enumerate(downloaddata.train_loader):
    images = images.to(torch.device("cpu"))
    images = images.view(-1,28,28)
    labels = labels.to(torch.device("cpu"))
    predictions = network(images)
    test_acc += get_accuracy(predictions, labels, downloaddata.batch_size_train)
print(test_acc/(i+1))