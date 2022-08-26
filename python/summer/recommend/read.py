import random
import copy
import math 
def change(pth,pth2):
    f=open(pth,"r")
    f2=open(pth2,"w")
    use=[]
    for line in f:
        x=[int(i) for i in line.strip("\n").split(",")]
        use.append(copy.deepcopy(x))
    for user in use:
        tj={}
        x=0
        for user2 in use:
            if user==user2:
                x+=1
                continue
            now=0
            up=0
            for i in user:
                up+=user[now]*user2[now]
                now+=1
            down1=0
            for i in user:
                down1+=i*i
            down2=0
            for i in user2:
                down2+=i*i
            down=math.sqrt(float(down1*down2))
            tj[x]=up/down
            x+=1
        new_tj=sorted(tj.items(),key=lambda d: d[1],reverse=True)
        x1=[]
        dd={}
        for xx,ba in new_tj:
            now=0
            for y in use[xx]:
                dd[now]=y
                now+=1
            new_dd=sorted(dd.items(),key=lambda d: d[1],reverse=True)
            for yy,bb in new_dd:
                if user[yy]==0 and bb>0 and yy not in x1:    
                    x1.append(copy.deepcopy(yy))
        f2.write(str(x1)+"\n")