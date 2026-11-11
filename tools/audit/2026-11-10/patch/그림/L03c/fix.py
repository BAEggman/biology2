import numpy as np, cv2
from PIL import Image
SP='/tmp/claude-0/-home-claude/adba3dea-fd2a-5075-a226-d8c1b6963879/scratchpad'
a=np.array(Image.open(SP+'/L03c/r1/final_v1.png').convert('RGB')).astype(np.float32)
o=a.copy()
X0,X1,Y0,Y1=1440,1477,450,582   # work window (pole starts at x=1478)
SH=27
D=np.array([154,114,82],np.float32)
# ---- 1. synthesize clean background in window (dark above diagonal shade edge, light below)
Lrow={y:a[y,1436:1442].mean(axis=(0)) for y in range(Y0,Y1)}
bg=np.zeros((Y1-Y0,X1-X0,3),np.float32)
for y in range(Y0,Y1):
    for x in range(X0,X1):
        yb=482+1.5*(x-1440)
        t=np.clip((y-yb)/1.5+0.5,0,1)   # 0 dark .. 1 light
        bg[y-Y0,x-X0]=(1-t)*D+t*Lrow[max(y,490)]
# ---- 2. sausage layer: stretch body of upper sausage by SH rows
def rowmap(y):
    if y<=450: return y
    if y<=478+SH: return 450+(y-450)*(28.0/(28+SH))
    return y-SH
H=Y1-Y0
mapy=np.array([[rowmap(y)] for y in range(Y0,Y1)],np.float32)
src=a[Y0:Y1,X0:X1]
mx,my=np.meshgrid(np.arange(X1-X0,dtype=np.float32),np.zeros(1))
MX=np.tile(np.arange(X1-X0,dtype=np.float32),(H,1)); MY=np.tile(mapy-Y0,(1,X1-X0)).astype(np.float32)
lay=cv2.remap(src,MX,MY,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE)
# alpha from ORIGINAL: non-bg core (outline/pink/knot) of the upper sausage only (orig rows <= 493), dilated for halo
core=np.zeros((Y1-Y0,X1-X0),np.uint8)
for y in range(Y0,494):
    for x in range(X0,X1):
        p=a[y,x]
        dd=np.abs(p-D).sum(); dl=np.abs(p-Lrow[max(y,490)]).sum()
        if min(dd,dl)>70: core[y-Y0,x-X0]=1
core=cv2.morphologyEx(core,cv2.MORPH_OPEN,np.ones((2,2),np.uint8))
core[494-Y0:,:]=0
# close the upper sausage's bottom so the interior can be flood-filled, then fill holes
core[494-Y0:496-Y0,:]=0
ff=(1-core).astype(np.uint8)*255
ffm=np.zeros((H+2,X1-X0+2),np.uint8)
inv=ff.copy()
# seed flood from left/right columns and from rows at y>=494 (outside)
for yy in range(0,494-Y0):
    for xx in (0,X1-X0-1):
        if inv[yy,xx]==255: cv2.floodFill(inv,ffm,(xx,yy),128)
reach=(inv==128)
core=(~reach).astype(np.uint8); core[494-Y0:,:]=0
core=cv2.dilate(core,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(5,5)))
core[494-Y0:,:]=0
corer=cv2.remap(core.astype(np.float32),MX,MY,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE)
al=cv2.GaussianBlur((corer>0.5).astype(np.float32),(0,0),0.7)[...,None]
comp=bg*(1-al)+lay*al
o[Y0:Y1,X0:X1]=comp
# ---- 3. end nub copied from the middle sausage (same shape, same bg tone), shifted to this hook
NX,NY,NW,NH=1500,521,30,14
dx=-52
patch=a[NY:NY+NH,NX:NX+NW]
Lp=a[538,1500:1530].mean(axis=0)
dist=np.abs(patch-a[538,1512]).sum(axis=2)
pm=cv2.dilate((dist>95).astype(np.uint8),np.ones((3,3),np.uint8)).astype(np.float32)
pm=cv2.GaussianBlur(pm,(0,0),0.6)[...,None]; pm=np.clip(pm,0,1)
ty,tx=NY,NX+dx
reg=o[ty:ty+NH,tx:tx+NW]
o[ty:ty+NH,tx:tx+NW]=reg*(1-pm)+patch*pm
Image.fromarray(np.clip(o+0.5,0,255).astype(np.uint8)).save(SP+'/picfix/L03c/final_new.png')
