from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
import numpy as np
import joblib


x = []
x=input().split( )
xx = []
xx.append(x)
xx = np.array( xx,dtype=float )
knn = joblib.load("E:\exercise\python\iris_recognize\knn.pkl")
print(knn.predict(xx))

