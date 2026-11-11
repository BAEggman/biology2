import numpy as np, cv2
from PIL import Image, ImageDraw
SP='/tmp/claude-0/-home-claude/adba3dea-fd2a-5075-a226-d8c1b6963879/scratchpad'
A=np.array(Image.open(SP+'/L48c/r1/final_v1.png').convert('RGB'))
out=A.copy()
BG=np.array([180,207,125],float)
S=8
# ---------- 1. lump right edge: close with a round outline ----------
x0,y0,x1,y1=1884,868,1920,922
reg=A[y0:y1,x0:x1].astype(float).copy()
new=reg.copy()
CT=[(1905.8,878.2),(1907.8,882),(1909.0,887),(1909.2,892),(1908.4,897),(1906.0,900.8),(1902.0,903.0),(1898.0,904.4)]
cx=lambda y: np.interp(y,[c[1] for c in CT[:6]],[c[0] for c in CT[:6]])
for y in range(877,906):
    # contour x at this row (right limit of the lump)
    if y<=900: xc=cx(y)
    else: xc=np.interp(y,[900.8,903,904.4],[1906.0,1902.0,1898.0])
    base=np.median(A[y,1891:1897].astype(float),axis=0)
    for x in range(1900,1914):
        ii=(y-y0,x-x0)
        if x<xc: new[ii]=base if y<903 else np.median(A[y,1891:1897].astype(float),axis=0)
        else: new[ii]=BG
# shadow below: extend the shadow colour of x<=1896 and taper it out to the right
for y in range(904,918):
    for x in range(1897,1914):
        s=A[y,1895].astype(float)
        t=np.clip((1911.0-x)/12.0,0,1); t=t*t*(3-2*t)
        new[y-y0,x-x0]=BG+(s-BG)*t
# supersampled outline
big=Image.fromarray(np.round(new).astype(np.uint8)).resize(((x1-x0)*S,(y1-y0)*S),Image.NEAREST)
d=ImageDraw.Draw(big)
q=[((x-x0)*S,(y-y0)*S) for x,y in CT]
w=3.2*S
d.line(q,fill=(0,0,0),width=int(w),joint='curve')
for (px,py) in (q[0],q[-1]):
    r=w/2; d.ellipse([px-r,py-r,px+r,py+r],fill=(0,0,0))
patch=np.array(big.resize((x1-x0,y1-y0),Image.BOX))
out[y0:y1,x0:x1]=patch
# ---------- 2. black doodle in the grass ----------
bx0,by0,bx1,by1=1955,890,2000,925
sub=np.ascontiguousarray(out[by0:by1,bx0:bx1])
m=(sub.astype(int).sum(2)<470)
m=cv2.dilate(m.astype(np.uint8),np.ones((7,7),np.uint8))
sub2=cv2.inpaint(sub,m*255,5,cv2.INPAINT_TELEA)
out[by0:by1,bx0:bx1]=sub2
Image.fromarray(out).save(SP+'/picfix/L48c/final_new.png')
