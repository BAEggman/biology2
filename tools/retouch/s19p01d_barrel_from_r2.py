import cv2, numpy as np
from PIL import Image
from scipy import ndimage as ndi
r1=cv2.imread('/mnt/user-data/uploads/Downloads/s19p01d_v1_1790606587390.png')
r2=cv2.imread('/mnt/user-data/uploads/Downloads/s19p01d_v2_1790606762770.png')
x0,y0,x1,y1=268,336,440,462
sub=r2[y0:y1,x0:x1].astype(int)
bg=np.array([222,236,245])  # BGR cream approx
# estimate bg from r1 same box (no barrel there except record)
bgm=np.median(r1[y0:y1,x0+60:x1-40].reshape(-1,3),axis=0)
d=np.abs(sub-bgm).sum(-1)
m=(d>45).astype(np.uint8)
m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
m=ndi.binary_fill_holes(m).astype(np.uint8)
n,lab,st,_=cv2.connectedComponentsWithStats(m,8)
k=1+int(np.argmax(st[1:,cv2.CC_STAT_AREA])); m=(lab==k).astype(np.uint8)
ys,xs=np.where(m); print('barrel bbox',xs.min()+x0,ys.min()+y0,xs.max()+x0,ys.max()+y0)
bx0,by0,bx1,by1=xs.min(),ys.min(),xs.max()+1,ys.max()+1
spr=r2[y0+by0:y0+by1,x0+bx0:x0+bx1].copy(); sm=m[by0:by1,bx0:bx1].astype(np.float32)
import sys
sc=float(sys.argv[1]) if len(sys.argv)>1 else 0.8
W=int(round(spr.shape[1]*sc)); H=int(round(spr.shape[0]*sc))
spr2=cv2.resize(spr,(W,H),interpolation=cv2.INTER_AREA); sm2=cv2.resize(sm,(W,H),interpolation=cv2.INTER_AREA)
# anchor: right edge at original right edge (door), bottom at original bottom
R=x0+bx1-2; B=y0+by1   # -2 px shift for r1/r2 offset
X=R-W; Y=B-H
out=r1.copy().astype(np.float32)
f=cv2.GaussianBlur(sm2,(3,3),0)[...,None]
out[Y:Y+H,X:X+W]=out[Y:Y+H,X:X+W]*(1-f)+spr2.astype(np.float32)*f
out=np.clip(out,0,255).astype(np.uint8)
cv2.imwrite('s19p01d_comp.png',out)
I=Image.fromarray(cv2.cvtColor(out,cv2.COLOR_BGR2RGB))
I.crop((0,0,560,506)).resize((840,759),Image.LANCZOS).save('s19d_comp_left.jpg',quality=92)
I.resize((768,380),Image.LANCZOS).save('s19d_comp_full.jpg',quality=90)
print('placed at',X,Y,W,H)
