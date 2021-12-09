import matplotlib.pyplot as plt
import numpy as np
from colour import Color

# Set color scheme
red = Color("red")
colors = list(red.range_to(Color("purple"), 14))
colors = [color.rgb for color in colors]

ax=plt.gca()
[ax.spines[i].set_visible(False) for i in ["top","right"]]

def gatt(m,t):
    """甘特图
    m机器集
    t时间集
    """
    for j in range(len(m)):#工序j
        i=m[j]-1#机器编号i
        if j==0:
            plt.barh(i,t[j])
            plt.text(np.sum(t[:j+1])/8,i,'J%s\nT%s'%((j+1),t[j]),color="white",size=8)
        else:
            plt.barh(i,t[j],left=(np.sum(t[:j])))
            plt.text(np.sum(t[:j])+t[j]/8,i,'J%s\nT%s'%((j+1),t[j]),color="white",size=8)

if __name__=="__main__":
    """测试代码"""
    m=np.random.randint(1,7,35)
    t=np.random.randint(15,25,35)
    gatt(m,t)
    plt.yticks(np.arange(max(m)),np.arange(1,max(m)+1))
    plt.show()


