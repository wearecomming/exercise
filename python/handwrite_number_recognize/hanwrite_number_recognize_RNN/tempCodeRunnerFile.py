class net_work(nn.Module):
    def __init__(self):
        super(net_work, self).__init__()
        self.rnn = nn.LSTM(input_size=28,hidden_size=128,num_layers=2,batch_first=True)
        self.out = nn.Linear(128,10)
        
    def forward(self,x):
        r,xx = self.rnn(x)
        out = self.out(r[:,-1,:])
        return out