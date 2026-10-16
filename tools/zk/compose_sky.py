"""compose_sky.py — 담장 위(하늘·바다)만 붙인다: 아래 경계는 담장 꼭대기 선을 따라 딱 자른다(앞 담장은 바탕 그대로).
python3 compose_sky.py base.png crop.json zone.png out.png --ox N --dy N --zw2 N --x0 A --x1 B --y0 C"""
import numpy as np, json, argparse
from PIL import Image
from scipy.ndimage import gaussian_filter
ap=argparse.ArgumentParser(); ap.add_argument('base'); ap.add_argument('cj'); ap.add_argument('zone'); ap.add_argument('out')
ap.add_argument('--ox',type=int,default=0); ap.add_argument('--dy',type=int,default=0); ap.add_argument('--zw2',type=int,default=0)
ap.add_argument('--x0',type=int); ap.add_argument('--x1',type=int); ap.add_argument('--y0',type=int,default=40); ap.add_argument('--lift',type=int,default=13)
a=ap.parse_args()
B=np.asarray(Image.open(a.base).convert('RGB')).astype(float)
cj=json.load(open(a.cj)); S=2; bx0,by0,bx1,by1=[v*S for v in cj['box']]; zw,zh=bx1-bx0,by1-by0
Zi=Image.open(a.zone).convert('RGB'); zw2=a.zw2 or zw
Z0=np.asarray(Zi.resize((zw2,zh),Image.LANCZOS)).astype(float)
C=B[by0:by1,bx0:bx1]; Z=C.copy(); ox,dy=a.ox,a.dy
xs=max(0,ox); xe=min(zw,ox+zw2); ys=max(0,dy); ye=min(zh,zh+dy)
Z[ys:ye,xs:xe]=Z0[ys-dy:ye-dy, xs-ox:xe-ox]
top=np.full(zw,-1)
for x in range(zw):
    col=C[200:330,x]; r,g,b=col[:,0],col[:,1],col[:,2]
    idx=np.where((r>g+35)&(r>b+35)&(r>110))[0]
    if len(idx): top[x]=200+idx[0]
cut=np.where(top>0, top-a.lift, 262).astype(float)
cut=np.convolve(np.pad(cut,7,mode='edge'),np.ones(15)/15,mode='valid')
M=np.zeros((zh,zw))
for x in range(a.x0,a.x1): M[a.y0:int(cut[x]),x]=1
soft=gaussian_filter(M,5)
for x in range(zw):
    c=int(cut[x]); soft[c:,x]=0
    if a.x0+10<=x<a.x1-10: soft[max(a.y0+10,c-12):c,x]=1
L=B.copy(); L[by0:by1,bx0:bx1]=C*(1-soft[...,None])+Z*soft[...,None]
Image.fromarray(np.clip(L,0,255).astype('uint8')).save(a.out)
d=np.sqrt(((L-B)**2).sum(2)); w=np.argwhere(d>30)
print('changed px>30',len(w), 'bbox(2x)', w.min(0) if len(w) else None, w.max(0) if len(w) else None)
