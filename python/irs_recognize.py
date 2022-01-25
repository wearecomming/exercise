from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier


irs = load_iris()
x_train,x_test,y_train,y_test = train_test_split(irs["data"],irs["target"])

knn = KNeighborsClassifier(n_neighbors=3)
knn.fit(x_train,y_train)
print("Accuracy:",knn.score(x_test,y_test)*100,"%")
