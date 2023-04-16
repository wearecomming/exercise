import os

import numpy
import numpy as np
import math

# testData为录入的数据信息
testData = np.array(
    [1628.1, 1745.6, 1901.3, 1926.5, 1976.2, 2187.5, 2265.2, 2392.6, 2503.1, 2588.3, 2696.4, 2868.1, 3046.6, 3313.1,
     3547.8, 3900.9,123,3444,56775,1232,778,338,2324,1123,4565,2342,5465])
a = 0
u = 0


# step2 搭建新序列
def add_all(testData):
    print("---------------")
    print("step2-->Xi")
    simulation = []
    len_data = len(testData)
    for i in range(len_data):
        temp = 0
        for j in range(i + 1):
            temp = temp + testData[j]
        simulation.append(temp)
    print(simulation)
    create_b_y(testData, simulation)


# step3 构成矩阵B,Y
def create_b_y(Xa, Xb):
    print("---------------")
    print("step3-->B")
    lenXb = len(Xb) - 1
    X0 = np.array(Xa)
    X1 = np.array(Xb)
    B = []
    for i in range(lenXb):
        B.append([])
        for j in range(2):
            if j == 0:
                temp = -1 * 0.5 * (X1[i] + X1[i + 1])
                B[i].append(temp)
            else:
                B[i].append(1)
    print(B)
    print("step3-->Y")
    Y = []
    lenX0 = len(Xb)
    z = 1
    for z in range(lenX0):
        Y.append([])
        for j in range(1):
            Y[z].append(X0[z])
    Y = Y[1:]
    print(Y)
    get_a_u(B, Y)


# step4 获得a和u
def get_a_u(B, Y):
    print("---------------")
    print("step4-->a,u")
    BT = np.transpose(B)
    a1 = np.dot(BT, B)
    inv_a1 = np.linalg.inv(a1)
    a2 = np.dot(BT, Y)
    af = np.dot(inv_a1, a2)
    global a
    a = af[0]
    global u
    u = af[1]
    print(a)
    print(u)


# step5 构建预测模型
def func(k):
    uf = u / a
    res = (testData[0] - uf) * math.exp(- a * k) + uf
    return res


def forecast(k):
    res = func(k) - func(k-1)
    print(res)
    return res


# step1
def fx(test):
    add_all(test)
    # 记录长度
    flen=len(test)
    print("---------------")
    print("Forecast result")
    # 预测下一个数据
    return forecast(flen)
