import torch.nn as nn
import torch.nn.functional as F

class simlarnett(nn.Module):
    
    def __init__(self):
        super(simlarnett, self).__init__()
        self.cnn1 = nn.Sequential(
            nn.Conv2d(1, 4, kernel_size=5), 
            nn.ReLU(inplace=True),
            nn.BatchNorm2d(4),
            nn.Dropout2d(p=.2),
 
            nn.Conv2d(4, 8, kernel_size=5),
            nn.ReLU(inplace=True),
            nn.BatchNorm2d(8),
            nn.Dropout2d(p=.2),
 
            nn.Conv2d(8, 8, kernel_size=5),
            nn.ReLU(inplace=True),
            nn.BatchNorm2d(8),
            nn.Dropout2d(p=.2),
        )
        self.fc1 = nn.Sequential(
            nn.Linear(8 * 88 * 88, 500),
            nn.ReLU(inplace=True),
 
            nn.Linear(500, 500),
            nn.ReLU(inplace=True),
 
            nn.Linear(500, 3)
        )
    def forward_once(self, x):
        output = self.cnn1(x)
        output = output.view(output.size()[0], -1)
        output = self.fc1(output)
        return output
 
    def forward(self, input1, input2):
        output1 = self.forward_once(input1)
        output2 = self.forward_once(input2)
        return output1, output2
    
    
    