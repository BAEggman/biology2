import numpy as np, cv2
from PIL import Image
img=np.array(Image.open('w4c.png').convert('RGB'))
x0,y0,x1,y1=1590,760,2048,1144
c=img[y0:y1,x0:x1].copy(); hsv=cv2.cvtColor(c,cv2.COLOR_RGB2HSV).astype(int); H,S,V=hsv[...,0],hsv[...,1],hsv[...,2]
box=np.zeros(H.shape,bool); box[80:170,30:150]=True; box[170:384,200:420]=True
gold=(H>=19)&(H<=34)&(S>120)&(V>110)&box
near=cv2.dilate(gold.astype(np.uint8),np.ones((5,5),np.uint8),iterations=2)>0
gold=gold|((H>=6)&(H<=34)&(S>70)&(V>60)&near&box)
green=(H>=35)&(H<=85)&(S>80)&(V>60)&box
def lut(V,m,dark,light):
    v=V[m].astype(float); lo,hi=np.percentile(v,3),np.percentile(v,98); t=np.clip((v-lo)/(hi-lo+1e-6),0,1)[:,None]
    return (np.array(dark)+(np.array(light)-np.array(dark))*t)
c[gold]=lut(V,gold,[22,30,78],[88,108,182]).astype(np.uint8)
c[green]=lut(V,green,[96,150,205],[205,232,250]).astype(np.uint8)
img[y0:y1,x0:x1]=c
Image.fromarray(img).save('w10.png')
print(gold.sum(),green.sum())
Image.fromarray(np.hstack([np.array(Image.open('w4c.png').convert('RGB'))[y0:y1,x0:x1],c])).save('v10.png')
