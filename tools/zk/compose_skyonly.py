"""compose_skyonly.py — 하늘(수평선 위)만 바꾼 Gemini 결과를 붙인다: 정합은 수평선 아래 띠(담장·바다)로, 가면은 바탕의 수평선(바다 위 검은 선) 위만.
python3 compose_skyonly.py base.png crop.json zone.png out.png [--band 0.32,0.62] [--x0 N --x1 N] [--fl 60] [--fr 0] [--top 42]
 --x0/--x1: 바꿀 x 범위(2배 전역) · --fl/--fr: 왼/오른 가장자리 깃털 폭(2배)"""
import argparse, json, numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter
ap=argparse.ArgumentParser(); ap.add_argument('base'); ap.add_argument('cj'); ap.add_argument('zone'); ap.add_argument('out')
ap.add_argument('--band',default='0.32,0.62'); ap.add_argument('--x0',type=int); ap.add_argument('--x1',type=int)
ap.add_argument('--fl',type=int,default=60); ap.add_argument('--fr',type=int,default=0); ap.add_argument('--top',type=int,default=42)
ap.add_argument('--search',type=int,default=16)
a=ap.parse_args()
B=np.asarray(Image.open(a.base).convert('RGB')).astype(float); H,W,_=B.shape
cj=json.load(open(a.cj)); S=cj['scale']; bx0,by0,bx1,by1=[v*S for v in cj['box']]; zw,zh=bx1-bx0,by1-by0
Z=np.asarray(Image.open(a.zone).convert('RGB').resize((zw,zh),Image.LANCZOS)).astype(float)
b0,b1=[float(v) for v in a.band.split(',')]; ya,yb=int(zh*b0),int(zh*b1); xa,xb=int(zw*.04),int(zw*.96)
best=None
for dy in range(-a.search,a.search+1):
    for dx in range(-a.search,a.search+1):
        ys,ye=by0+ya+dy,by0+yb+dy; xs,xe=bx0+xa+dx,bx0+xb+dx
        if ys<0 or xs<0 or ye>H or xe>W: continue
        e=np.mean((Z[ya:yb,xa:xb]-B[ys:ye,xs:xe])**2)
        if best is None or e<best[0]: best=(e,dx,dy)
e,dx,dy=best
L=B.copy(); cov=np.zeros((H,W))
ys=np.arange(zh)+by0+dy; xs=np.arange(zw)+bx0+dx
vy=(ys>=0)&(ys<H); vx=(xs>=0)&(xs<W)
L[np.ix_(ys[vy],xs[vx])]=Z[np.ix_(np.where(vy)[0],np.where(vx)[0])]; cov[np.ix_(ys[vy],xs[vx])]=1
lum=B.mean(2)
x0=a.x0 if a.x0 is not None else bx0; x1=a.x1 if a.x1 is not None else bx1
hz=np.zeros(W,int)
for x in range(x0,x1):
    col=lum[225:300,x]; idx=np.where(col<130)[0]
    hz[x]=225+idx[0] if len(idx) else 258
seg=hz[x0:x1].astype(float); seg=np.convolve(np.pad(seg,9,mode='edge'),np.ones(19)/19,mode='valid')
# 들쭉날쭉한 열(물보라 등)은 이웃 중앙값으로
from scipy.ndimage import median_filter
seg=median_filter(seg,size=31,mode='nearest')
M=np.zeros((H,W))
for i,x in enumerate(range(x0,x1)):
    M[a.top:int(seg[i])-2,x]=1
M=gaussian_filter(M,1.5)
for i,x in enumerate(range(x0,x1)):
    M[int(seg[i])-1:,x]=0
# 가장자리 깃털
for x in range(x0,x1):
    wl=1.0 if a.fl<=0 else min(1.0,(x-x0)/a.fl)
    wr=1.0 if a.fr<=0 else min(1.0,(x1-1-x)/a.fr)
    M[:,x]*=min(wl,wr)
M[:, :x0]=0; M[:, x1:]=0
M*=cov
C=B*(1-M[...,None])+L*M[...,None]
Image.fromarray(np.clip(C,0,255).astype('uint8')).save(a.out)
print(f'정합 dx={dx} dy={dy}(2배) mse={e:.1f} · 수평선 y {seg.min():.0f}~{seg.max():.0f}')
