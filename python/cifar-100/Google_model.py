import torch.nn as nn
import torch
import torch.nn.functional as F

class BasicConv2d(nn.Module):
    def __init__(self, in_channels, out_channels, **kwargs):
        # BasicConv2d传入3个参数：输入特征矩阵深度in_channels,卷积核个数(即输出特征矩阵个数)out_channels,及**kwargs:步距、padding等
        super(BasicConv2d, self).__init__()
        self.conv = nn.Conv2d(in_channels, out_channels, **kwargs)  # 输入特征矩阵深度=传入特征矩阵深度，卷积核个数=输出特征矩阵深度
        self.relu = nn.ReLU(inplace=True)

    def forward(self, x):  # 正向传播，先经过卷积层然后经过ReLu激活
        x = self.conv(x)
        x = self.relu(x)
        return x


class Inception(nn.Module):
    def __init__(self, in_channels, ch1x1, ch3x3red, ch3x3, ch5x5red, ch5x5, pool_proj):
        # in_channels为输入特征矩阵深度，ch1x1=#1x1,ch3x3red=#3x3reduce,ch3x3=#3x3,ch5x5red=#5x5reduce,ch5x5=#5x5,pool_proj=#pool_proj
        super(Inception, self).__init__()

        # 分支1，1*1*(#1*1)卷积
        # 采用最下面定义的BasicConv2d模板(Conv+ReLu)，输入特征矩阵深度为in_channels，卷积核个数为ch1x1，卷积核大小为1，步距为1
        self.branch1 = BasicConv2d(in_channels, ch1x1, kernel_size=1)

        # 分支2，包括两个基本卷积模板：1*1*(#3*3 reduce)卷积 和 3*3*(#3*3)卷积
        self.branch2 = nn.Sequential(
            BasicConv2d(in_channels, ch3x3red, kernel_size=1),
            BasicConv2d(ch3x3red, ch3x3, kernel_size=3, padding=1)   # padding=1保证输出大小等于输入大小
            # 输入特征矩阵深度为上一层卷积核个数(上一层卷积核个数即为上一层输出特征矩阵的深度，也即下一层输入特征矩阵的深度)
        )

        # 分支3与分支2类似，包含1*1*(#5*5 reduce)卷积 和 5*5*(#5*5)卷积
        self.branch3 = nn.Sequential(
            BasicConv2d(in_channels, ch5x5red, kernel_size=1),
            BasicConv2d(ch5x5red, ch5x5, kernel_size=5, padding=2)   # padding=2保证输出大小等于输入大小
        )

        # 分支4先3*3Max pooling，再1*1*(# pool proj)卷积
        self.branch4 = nn.Sequential(
            nn.MaxPool2d(kernel_size=3, stride=1, padding=1),
            BasicConv2d(in_channels, pool_proj, kernel_size=1)  # 因为池化不改变深度，因此输入特征矩阵深度仍为in_channels
        )

    def forward(self, x):  # 定义前向传播过程：将输入矩阵分别输入到分支1、2、3、4
        branch1 = self.branch1(x)
        branch2 = self.branch2(x)
        branch3 = self.branch3(x)
        branch4 = self.branch4(x)

        outputs = [branch1, branch2, branch3, branch4]  # 将输出放入到列表中
        return torch.cat(outputs, 1)  # 用torch.cat函数将四个输出合并
        # 传入第1个参数为四个输出特征矩阵的列表，第2个参数为所需要合并的维度，torchtensor排列顺序为[batch,c,h,w],则此处1表示在深度方向合并


class InceptionAux(nn.Module):
    def __init__(self, in_channels, num_classes):  # 在初始化函数中传入输入特征矩阵深度 和 要分类类别的个数
        super(InceptionAux, self).__init__()
        self.averagePool = nn.AvgPool2d(kernel_size=5, stride=3)  # 定义一个kernel_size=5, stride=3的平均池化下采样层，得4*4*c的特征矩阵
        self.conv = BasicConv2d(in_channels, 128, kernel_size=1)  # 卷积核个数固定为128，1*1卷积改变#c,则output[batch, 128, 4, 4]

        self.fc1 = nn.Linear(2048, 1024)  # 输入节点个数为128*4*4=2048，输出结点个数为1024
        self.fc2 = nn.Linear(1024, num_classes)  # 输入节点个数为上一层输出1024，输出节点个数为预测的类别个数

    def forward(self, x):  # 定义正向传播过程
        # aux1: N x 512 x 14 x 14, aux2: N x 528 x 14 x 14 两个分类器经平均池化前输入特征矩阵参数
        x = self.averagePool(x)
        # aux1: N x 512 x 4 x 4, aux2: N x 528 x 4 x 4 两个分类器经平均池化后输出特征矩阵参数
        x = self.conv(x)
        # N x 128 x 4 x 4 ，由于都固定采用128个卷积核，则无论辅助分类器1、2，输出特征矩阵shape都等于128*4*4
        x = torch.flatten(x, 1)  # 将输出特征矩阵展平，此处1代表从channel维度开始展平
        x = F.dropout(x, 0.5, training=self.training)  # 展平向量与FC1之间加入一个Dropout，并传入training参数
        # N x 2048
        # ######当实例化一个model后，可通过model.train()和model.eval()来控制模型的状态,控制Dropout是否有效######
        # ######model.train()下，self.training=True,model.eval()下，self.training=False######
        x = F.relu(self.fc1(x), inplace=True)  # inplace=True是一种节省内存的方法
        x = F.dropout(x, 0.5, training=self.training)
        # N x 1024
        x = self.fc2(x)
        # N x num_classes
        return x


class GoogLeNet(nn.Module):
    def __init__(self, num_classes=1000, aux_logits=True, init_weights=False):
        # 初始化函数中传入3个参数：分类类别个数、是否使用辅助分类器和是否初始化权重
        super(GoogLeNet, self).__init__()
        self.aux_logits = aux_logits  # 将是否使用辅助分类器的布尔变量传入到类变量中

        # 下面根据GoogLeNet简图来搭建网络，每一层数据都由网络详解表格中数据得出
        self.conv1 = BasicConv2d(3, 64, kernel_size=7, stride=2, padding=3)
        self.maxpool1 = nn.MaxPool2d(3, stride=2, ceil_mode=True)  # 最大池化结果为小数时，ceil_mode=True，向上取整；ceil_mode=False,向下取整

        self.conv2 = BasicConv2d(64, 64, kernel_size=1)
        self.conv3 = BasicConv2d(64, 192, kernel_size=3, padding=1)
        self.maxpool2 = nn.MaxPool2d(3, stride=2, ceil_mode=True)

        self.inception3a = Inception(192, 64, 96, 128, 16, 32, 32)
        self.inception3b = Inception(256, 128, 128, 192, 32, 96, 64)
        self.maxpool3 = nn.MaxPool2d(3, stride=2, ceil_mode=True)

        # Inception层的输入矩阵深度可由表格上一层的output size得到，也可由上一层四个分支的特征矩阵的深度加和得到
        self.inception4a = Inception(480, 192, 96, 208, 16, 48, 64)
        self.inception4b = Inception(512, 160, 112, 224, 24, 64, 64)
        self.inception4c = Inception(512, 128, 128, 256, 24, 64, 64)
        self.inception4d = Inception(512, 112, 144, 288, 32, 64, 64)
        self.inception4e = Inception(528, 256, 160, 320, 32, 128, 128)
        self.maxpool4 = nn.MaxPool2d(3, stride=2, ceil_mode=True)

        self.inception5a = Inception(832, 256, 160, 320, 32, 128, 128)
        self.inception5b = Inception(832, 384, 192, 384, 48, 128, 128)

        if self.aux_logits:  # 如果传入参数aux_logits=True，则生成两个辅助分类器。辅助分类器需要2个参数：输入特征深度和分类类别个数
            self.aux1 = InceptionAux(512, num_classes)  # 第1个辅助分类器的输入矩阵深度是Inception4a的输出特征矩阵深度
            self.aux2 = InceptionAux(528, num_classes)  # 第2个辅助分类器的输入矩阵深度是Inception4d的输出特征矩阵深度

        self.avgpool = nn.AdaptiveAvgPool2d((1, 1))  # 自适应平均池化下采样，将输入数据自适应地变为高为1，宽为1的特征矩阵
        self.dropout = nn.Dropout(0.4)  # 在展平特征矩阵和输出结点之间加1个Dropout层
        self.fc = nn.Linear(1024, num_classes)  # 输出层，num_class为预测类别的个数
        if init_weights:  # 如果传入参数init_weights=True,则进行参数初始化
            self._initialize_weights()

    def forward(self, x):  # 根据GoogLeNet网络结构图进行正向传播
        # N x 3 x 224 x 224
        x = self.conv1(x)
        # N x 64 x 112 x 112
        x = self.maxpool1(x)
        # N x 64 x 56 x 56
        x = self.conv2(x)
        # N x 64 x 56 x 56
        x = self.conv3(x)
        # N x 192 x 56 x 56
        x = self.maxpool2(x)

        # N x 192 x 28 x 28
        x = self.inception3a(x)
        # N x 256 x 28 x 28
        x = self.inception3b(x)
        # N x 480 x 28 x 28
        x = self.maxpool3(x)
        # N x 480 x 14 x 14
        x = self.inception4a(x)
        # N x 512 x 14 x 14
        if self.training and self.aux_logits:    # eval model lose this layer
            aux1 = self.aux1(x)  # 满足条件时，将结果输入到辅助分类器1中得到结果。
        # ####训练过程中self.training=True;验证过程中，self.training=False。self.aux_logits为是否调用辅助分类器####

        x = self.inception4b(x)
        # N x 512 x 14 x 14
        x = self.inception4c(x)
        # N x 512 x 14 x 14
        x = self.inception4d(x)
        # N x 528 x 14 x 14
        if self.training and self.aux_logits:    # eval model lose this layer
            aux2 = self.aux2(x)

        x = self.inception4e(x)
        # N x 832 x 14 x 14
        x = self.maxpool4(x)
        # N x 832 x 7 x 7
        x = self.inception5a(x)
        # N x 832 x 7 x 7
        x = self.inception5b(x)
        # N x 1024 x 7 x 7

        x = self.avgpool(x)
        # N x 1024 x 1 x 1
        x = torch.flatten(x, 1)  # 将所得特征矩阵进行展平处理
        # N x 1024
        x = self.dropout(x)
        x = self.fc(x)
        # N x 1000 (num_classes)
        if self.training and self.aux_logits:   # eval model lose this layer
            return x, aux2, aux1
        # 如果是训练模式(self.training=True)且使用辅助分类器(self.aux_logits=True)的话，则返回3个值:主分类器输出,辅助分类器2输出,辅助分类器1输出
        return x  # 如果条件不满足，则只返回主分类器输出结果

    def _initialize_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Conv2d):  # 对卷积层进行初始化
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.Linear):  # 对全连接层进行初始化
                nn.init.normal_(m.weight, 0, 0.01)
                nn.init.constant_(m.bias, 0)
