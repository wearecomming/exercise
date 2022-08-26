import os
import cv2
import csv
def findAllFile():
    x=0
    f1 = open("./data.csv", 'w')
    #col=["label"]
    #col.extend(["pixel%d"%i for i in range(100*100)])
    writer=csv.writer(f1)
    #writer.writerow(col)
    for fs in os.listdir("./lfw_funneled"):
        filename = os.path.join("./lfw_funneled", fs)
        if os.path.isdir(filename):
            x+=1
            for f in os.listdir(filename):
                if f.endswith('.jpg'):
                    fullname = os.path.join(filename, f)
                    img = cv2.imread(fullname,cv2.IMREAD_GRAYSCALE)
                    h,w=img.shape
                    if h>w:
                        img = cv2.copyMakeBorder(img,0,0,h-w,0,cv2.BORDER_CONSTANT,value=0)
                    if w>h:   
                        img = cv2.copyMakeBorder(img,w-h,0,0,0,cv2.BORDER_CONSTANT,value=0)
                    img = cv2.resize(img,(100,100))
                    row=[x]
                    row.extend(img.flatten())
                    writer.writerow(row)
findAllFile()                    
