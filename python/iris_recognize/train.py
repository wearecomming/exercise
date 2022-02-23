from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
import joblib
import numpy as np
import dataload


knn = KNeighborsClassifier(n_neighbors=3)
knn.fit(dataload.x_train,dataload.y_train)
joblib.dump(knn,"E:\exercise\python\iris_recognize\knn.pkl")