import sys; sys.path.insert(0,'/tmp/L48a')
from lib import *
from PIL import Image
import numpy as np
img=Image.open('w2.png').convert('RGB'); A=np.array(img); B=np.array(Image.open('base.png').convert('RGB'))
A[590:840,545:795]=B[290:540,545:795]
img=Image.fromarray(A)
T=132; S=round(T*0.6)
L=(516,608); R=(806,612)
H={}
# tall navy, tall sky behind (lying), short ones in front
img,H['tn']=place_rot(img,sprite('navy_c',T),592,826,-28)
img,H['ts']=place_rot(img,sprite('sky_c',T,flip=True),752,846,-80)
img,H['ss']=place_rot(img,sprite('sky_c',S),628,926,-14)
img,H['sn']=place_rot(img,sprite('navy_c',S,flip=True),720,928,18)
near=lambda P,hs: min(hs,key=lambda q:(q[0]-P[0])**2+(q[1]-P[1])**2)
far=lambda P,hs: max(hs,key=lambda q:(q[0]-P[0])**2+(q[1]-P[1])**2)
tie={}
for k,(p,q) in H.items():
    sp=-1 if p[0]<=q[0] else 1
    img,tp=plate(img,p[0],p[1],sp,0.9 if k[0]=='t' else 0.75); img,tq=plate(img,q[0],q[1],-sp,0.9 if k[0]=='t' else 0.75)
    tie[k]=[tp,tq]
specs=[(L,near(L,tie['tn']),10),(R,far(L,tie['tn']),25),(R,near(R,tie['ts']),10)]
img=ropes(img,specs,w=7)
img.save('w2c.png')
print(tie)
