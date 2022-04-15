import torch
import torch.nn as nn
import csv
import torch.nn.functional as F
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
    
    
csvFile = open("E:\exercise\python\handwrite_number_recognize\hanwrite_number_recognize_RNN/test_submit.csv", "w")
writer = csv.writer(csvFile)
writer.writerow(["ImageId","Label"])
network = net_work()

network.load_state_dict(torch.load("E:\exercise\python\handwrite_number_recognize\hanwrite_number_recognize_RNN/num.pt"))
cnt=0
for i,(images,labels) in enumerate(dataload.test_loader):
    images = images.to(torch.device("cpu"))
    images = images.view(-1,28,28)
    predictions = network(images)
    pred_y = torch.max(predictions, 1)[1].data.numpy()
    for dex in pred_y.tolist():
        cnt+=1
        writer.writerow([cnt,dex])
csvFile.close()