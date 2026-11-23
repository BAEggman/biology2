import sys; sys.path.insert(0,'/tmp/L48a')
from lib import *
from PIL import Image
img=Image.open('w3.png').convert('RGB')
CX=1024; T=140; S=round(T*0.6)
order=[('navy_c',T,False),('sky_c',S,False),('sky_c',T,True),('navy_c',S,True)]
gap=14; tot=T*2+S*2+gap*3; y=318
LR=(880,568); RR=(1170,568)
sprs=[]
for n,h,f in order:
    sp=sprite(n,h,flip=f); cy=y+h/2; sprs.append((sp,cy)); y+=h+gap
# ropes behind bundles first? ropes attach to hooks at plates; draw bundles first then ropes over? ropes tie to hook outside straw -> draw ropes after bundles
for sp,cy in sprs: img=place(img,sp,CX,cy)
specs=[]; hooks=[]
for sp,cy in sprs:
    wy,xl,xr=waist(sp,CX,cy)
    hooks+= [((xl-3,wy),-1),((xr+3,wy),1)]
ties=[]
for (x,y_),sd in hooks:
    img,t=plate(img,x,y_,sd,1.0); ties.append((t,sd))
specs=[(LR if sd<0 else RR,t,0) for t,sd in ties]
img=ropes(img,specs,w=7)
img=dashes(img,1023.5,300,830)
img.save("w3c.png")
# dashed line redraw over waists: sample existing dash pattern x
