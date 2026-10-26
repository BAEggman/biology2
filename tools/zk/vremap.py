#!/usr/bin/env python3
"""vremap.py — Gemini 가 세로로 늘인(비등방 리프레임) 결과를, 가로줄 랜드마크 짝으로 조각별 선형 되맞춤.
사용: vremap.py out.png crop.png fit.png "crop_y1:out_y1,crop_y2:out_y2,..."  (좌표는 각 그림 자체 px · 가로는 전체 비율)"""
import sys, numpy as np, cv2
from PIL import Image
o=np.asarray(Image.open(sys.argv[1]).convert('RGB')); c=Image.open(sys.argv[2]).convert('RGB'); W,H=c.size; Ho,Wo=o.shape[:2]
pairs=sorted([tuple(float(v) for v in p.split(':')) for p in sys.argv[4].split(',')])
dst=np.array([p[0] for p in pairs]); src=np.array([p[1] for p in pairs])
ys=np.arange(H).astype(float); sy=np.interp(ys,dst,src)
k0=(src[1]-src[0])/(dst[1]-dst[0]); sy[ys<dst[0]]=src[0]+(ys[ys<dst[0]]-dst[0])*k0
k1=(src[-1]-src[-2])/(dst[-1]-dst[-2]); sy[ys>dst[-1]]=src[-1]+(ys[ys>dst[-1]]-dst[-1])*k1
sx=np.arange(W).astype(float)*Wo/W
mapx=np.tile(sx[None,:],(H,1)).astype(np.float32); mapy=np.tile(sy[:,None],(1,W)).astype(np.float32)
f=cv2.remap(o,mapx,mapy,cv2.INTER_LANCZOS4); Image.fromarray(f).save(sys.argv[3])
d=np.abs(f.astype(float)-np.asarray(c).astype(float)).mean(axis=2); print('vremap diff mean %.1f'%d.mean())
