"""zdiff.py crop.png out.png [thr] — Gemini 결과와 조각의 차이 덩어리(조각 2배 좌표 · 1배 전역 좌표)를 찍는다"""
import sys, json, numpy as np
from PIL import Image
from scipy import ndimage
c=Image.open(sys.argv[1]).convert('RGB'); z=Image.open(sys.argv[2]).convert('RGB').resize(c.size,Image.LANCZOS)
thr=float(sys.argv[3]) if len(sys.argv)>3 else 40
cj=json.load(open(sys.argv[1].replace('.png','.json'))) if sys.argv[1].endswith('.png') else None
C=np.asarray(c).astype(float); Z=np.asarray(z).astype(float)
d=np.sqrt(((ndimage.gaussian_filter(C,(3,3,0))-ndimage.gaussian_filter(Z,(3,3,0)))**2).sum(2)); m=d>thr
lab,n=ndimage.label(ndimage.binary_dilation(m,iterations=4))
big=sorted([(o[1].start,o[0].start,o[1].stop,o[0].stop,int(m[o].sum())) for o in ndimage.find_objects(lab) if m[o].sum()>60],key=lambda t:-t[4])
print('diff mean %.1f'%d.mean())
bx=cj['box'][0] if cj else 0; by=cj['box'][1] if cj else 0
for b in big[:12]:
    x0,y0,x1,y1,n=b
    print(f'조각2x ({x0},{y0})-({x1},{y1}) n={n}  → 1배 전역 own {bx+x0//2},{by+y0//2},{bx+(x1+1)//2},{by+(y1+1)//2}')
