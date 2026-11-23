import sys; sys.path.insert(0,'/tmp/L48a')
from lib import *
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFilter
img=Image.open('w1.png').convert('RGB'); pre=np.array(img)
X0,Y0,X1,Y1=180,800,450,960
c=pre[Y0:Y1,X0:X1].copy(); hsv=cv2.cvtColor(c,cv2.COLOR_RGB2HSV).astype(int)
ball=((hsv[...,0]>=120)&(hsv[...,0]<=165)&(hsv[...,1]>50)).astype(np.uint8)*255
n,lab,st,_=cv2.connectedComponentsWithStats(ball); big=1+np.argmax(st[1:,4]); ball=(lab==big).astype(np.uint8)*255
core=ball.copy(); ring=cv2.dilate(ball,np.ones((3,3),np.uint8),iterations=3); V=hsv[...,2]
ball=np.where((core>0)|((ring>0)&(V<50)),255,0).astype(np.uint8)
ff=ball.copy(); h,w=ball.shape; m=np.zeros((h+2,w+2),np.uint8); cv2.floodFill(ff,m,(0,0),255); ball=ball|cv2.bitwise_not(ff)
bs=np.dstack([c,ball]); bspr=Image.fromarray(bs.astype(np.uint8))
# erase ball (inpaint)
hole=cv2.dilate(ball,np.ones((3,3),np.uint8),iterations=3)
fill=cv2.inpaint(cv2.cvtColor(c,cv2.COLOR_RGB2BGR),hole,9,cv2.INPAINT_TELEA)
a=np.array(img); a[Y0:Y1,X0:X1]=cv2.cvtColor(fill,cv2.COLOR_BGR2RGB); img=Image.fromarray(a)
T=162; S=round(T*0.6); WS=0.56; BOT=934
lay=[('navy_c',T,False,229),('sky_c',T,True,307),('navy_c',S,False,359),('sky_c',S,True,404)]
# contact shadows
sh=Image.new('RGBA',img.size,(0,0,0,0)); ds=ImageDraw.Draw(sh)
for n_,h_,f,cx in lay:
    ww=h_*0.36; ds.ellipse([cx-ww,BOT-5,cx+ww,BOT+7],fill=(20,14,10,110))
sh=sh.filter(ImageFilter.GaussianBlur(3)); o=img.convert('RGBA'); o.alpha_composite(sh); img=o.convert('RGB')
for n_,h_,f,cx in lay:
    sp=sprite(n_,h_,flip=f,wscale=WS); img=place(img,sp,cx,BOT-h_/2)
    wy,xl,xr=waist(sp,cx,BOT-h_/2)
    s_=0.8 if h_==T else 0.65
    img,_=plate(img,xl-5,wy,-1,s_); img,_=plate(img,xr+5,wy,1,s_)
# ball back in front, shifted left
bb=bspr.crop(bspr.getbbox()); bx,by=bspr.getbbox()[:2]
o=img.convert('RGBA'); o.alpha_composite(bb,(X0+bx-46,Y0+by+4)); img=o.convert('RGB')
img.save('w1c.png')
