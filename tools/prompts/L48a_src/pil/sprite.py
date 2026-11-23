import numpy as np, cv2, sys
from PIL import Image
def extract(src,box,out):
    g=np.array(Image.open(src).convert('RGB')).astype(int)
    x0,y0,x1,y1=box; c=g[y0:y1,x0:x1]
    hsv=cv2.cvtColor(c.astype(np.uint8),cv2.COLOR_RGB2HSV).astype(int)
    H,S,V=hsv[...,0],hsv[...,1],hsv[...,2]
    blue=(H>=90)&(H<=135)&(S>40)
    dark=V<75
    metal=(S<40)&(V>100)
    wood=(H>=4)&(H<=28)&(S>55)
    fg=((blue|dark|metal)&~wood).astype(np.uint8)*255
    fg=cv2.morphologyEx(fg,cv2.MORPH_CLOSE,np.ones((3,3),np.uint8),iterations=1)
    n,lab,st,_=cv2.connectedComponentsWithStats(fg)
    big=1+np.argmax(st[1:,cv2.CC_STAT_AREA]); m=(lab==big).astype(np.uint8)*255
    inv=255-m; n2,lab2,st2,_=cv2.connectedComponentsWithStats(inv)
    for i in range(1,n2):
        if st2[i,cv2.CC_STAT_AREA]<120:
            sel=lab2==i
            if wood[sel].mean()<0.5: m[sel]=255
    m=cv2.GaussianBlur(m,(3,3),0)
    rgba=np.dstack([c,m]).astype(np.uint8); Image.fromarray(rgba).save(out)
    h,w=m.shape; v=Image.new('RGBA',(w,h),(255,0,255,255)); v.alpha_composite(Image.fromarray(rgba)); v.convert('RGB').resize((w*2,h*2)).save(out.replace('.png','_view.png'))
extract('z/gem_a3_v1.png',(235,62,405,322),'sp/navy.png')
