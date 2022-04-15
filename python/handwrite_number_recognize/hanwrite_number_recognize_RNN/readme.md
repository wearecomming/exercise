本项目为手写数字识别项目，采用Rnn实现，模型为LSTM

train.py训练模型，test.py测试，handwrite_number_recoginze.py生成答案文件，num.pt为模型参数

采用adam优化器和dropout(p=0.2)正则化

train_batchsize为96

学习速率在前5次学习时为0.002，后2次为0.0002

在kaggle上的准确度为98.817%

值得一提的是，RNN的准确度居然比CNN高

或许可以再提升一下CNN（笑）

还有一个比较重要的点是，在生成答案文件时读入数据千万不要随机化（因为这个卡了一周）