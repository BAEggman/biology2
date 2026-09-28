import cv2, numpy as np, sys
from PIL import Image
src='/mnt/user-data/uploads/Downloads/s11p02_v4_1790593455594.png'
a=cv2.imread(src); A=a.astype(int)
bg=np.median(A[100:118,790:815].reshape(-1,3),axis=0)
d=np.abs(A-bg).sum(-1)
# sprite: nail from face
x0,x1,y0,y1=782,807,118,142
spr=a[y0:y1,x0:x1].copy()
m=(d[y0:y1,x0:x1]>40).astype(np.uint8)
m=cv2.morphologyEx(m,cv2.MORPH_CLOSE,np.ones((3,3),np.uint8))
h,w=m.shape
for xx in range(0,6):
    half=int(round((xx/6.0)*4))
    for yy in range(h):
        if abs((yy+y0)-129)>half: m[yy,xx]=0
m=m.astype(np.float32)
# remove nail outside face: rows 118..142, x>=782
rm=np.zeros(a.shape[:2],np.uint8)
blk=(d[116:144,782:810]>25).astype(np.uint8)*255
rm[116:144,782:810]=blk
rm=cv2.dilate(rm,np.ones((3,3),np.uint8)); rm[:,:782]=0
b=cv2.inpaint(a,rm,2,cv2.INPAINT_NS)
B=b.astype(int); reg=rm>0
dark=(np.abs(B-bg).sum(-1)>45)&reg
b[dark]=bg.astype(np.uint8)
# claw outline pixels (to overlay later): dark pixels in claw tip box
cx0,cy0,cx1,cy1=714,128,742,150
claw=np.zeros(a.shape[:2],bool)
g=cv2.cvtColor(a,cv2.COLOR_BGR2GRAY)
claw[cy0:cy1,cx0:cx1]=g[cy0:cy1,cx0:cx1]<110
ang=float(sys.argv[1]); scale=float(sys.argv[2]); hx=float(sys.argv[3]); hy=float(sys.argv[4]); over=int(sys.argv[5]) if len(sys.argv)>5 else 1
pad=20
S=cv2.copyMakeBorder(spr,pad,pad,pad,pad,cv2.BORDER_REPLICATE)
M_=cv2.copyMakeBorder(m,pad,pad,pad,pad,cv2.BORDER_CONSTANT,value=0)
hcx,hcy=(801-x0)+pad,(129-y0)+pad
R=cv2.getRotationMatrix2D((hcx,hcy),ang,scale)
Sr=cv2.warpAffine(S,R,(S.shape[1],S.shape[0]),flags=cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE)
Mr=np.clip(cv2.warpAffine(M_,R,(S.shape[1],S.shape[0]),flags=cv2.INTER_LINEAR),0,1)
ox,oy=int(round(hx-hcx)),int(round(hy-hcy))
H_,W_=Sr.shape[:2]
roi=b[oy:oy+H_,ox:ox+W_].astype(np.float32)
f=Mr[...,None]
b[oy:oy+H_,ox:ox+W_]=(roi*(1-f)+Sr.astype(np.float32)*f).astype(np.uint8)
if over:
    b[claw]=a[claw]
cv2.imwrite('s11p02_rt.png',b)
I=Image.fromarray(cv2.cvtColor(b,cv2.COLOR_BGR2RGB))
I.crop((690,95,830,190)).resize((1120,760),Image.LANCZOS).save('s11_rt_z.jpg',quality=92)
I.crop((560,40,900,330)).save('s11_rt_mid.jpg',quality=92)
# --- face cleanup ---
b=cv2.imread('s11p02_rt.png').astype(np.float32)
bgc=bg.astype(np.float32)
# 1) stub outside outline
for yy in range(124,134):
    for xx in range(780,783):
        b[yy,xx]=bgc
# 2) interior: vertical interpolation between row 125/126 and 132/133
for xx in range(774,778):
    top=(b[125,xx]+b[126,xx])/2; bot=(b[132,xx]+b[133,xx])/2
    for yy in range(127,132):
        t=(yy-126)/(132-126)
        b[yy,xx]=top*(1-t)+bot*t
# 3) outline continuity at cols 778..779 rows 127..131: copy darkest color of outline from rows 125/133
dk=(b[126,778]+b[132,778])/2
for yy in range(127,132):
    b[yy,778]=dk; b[yy,779]=(b[126,779]+b[132,779])/2
# 4) faint smudge right of face: pixels in box whose color deviates from bg -> bg
box=b[112:146,780:815]
dev=np.abs(box-bgc).sum(-1)
box[(dev>6)&(dev<60)]=bgc
b[112:146,780:815]=box
b=np.clip(b,0,255).astype(np.uint8)
cv2.imwrite('s11p02_rt.png',b)
I=Image.fromarray(cv2.cvtColor(b,cv2.COLOR_BGR2RGB))
I.crop((690,95,830,190)).resize((1120,760),Image.LANCZOS).save('s11_rt_z.jpg',quality=92)
I.crop((560,40,900,330)).save('s11_rt_mid.jpg',quality=92)
