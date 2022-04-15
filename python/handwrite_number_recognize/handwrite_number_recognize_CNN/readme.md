本项目为手写数字识别项目，采用cnn实现，模型为LeNet5

train.py训练模型，test.py测试，handwrite_number_recoginze.py生成答案文件，num.pt为模型参数

采用adam优化器和dropout(p=0.2)正则化

train_batchsize为54

学习速率在前5次学习时为0.002，后5次为0.0002,最后两次为0.00002

在kaggle上的准确度为97.503%