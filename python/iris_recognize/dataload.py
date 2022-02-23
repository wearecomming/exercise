from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
import numpy as np

f = open("E:\exercise\python\iris_recognize\iris.data","r")
data = f.read().splitlines()
xray = []
yray = []
for item in data:
    l = item.split(",")
    xray.append([float(l[0]),float(l[1]),float(l[2]),float(l[3])])
    yray.append([l[4]])
xx = np.array(xray)
yy = np.array(yray)
yy = yy.ravel()

x_train,x_test,y_train,y_test = train_test_split(xx,yy)
