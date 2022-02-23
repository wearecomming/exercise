from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
import numpy as np
import train


x = []
x=input().split( )
xx = []
xx.append(x)
xx = np.array( xx,dtype=float )
print(train.knn.predict(xx))

