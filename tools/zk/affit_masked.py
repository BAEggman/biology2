#!/usr/bin/env python3
"""affit_masked.py gem out crop fit "x0,y0,x1,y1;..."(gem 좌표 — 바뀌지 않은 곳만) [partial]
바뀌지 않은 영역의 특징점만으로 정합(partial = 회전 + 등방 배율 + 이동만)."""
import sys, cv2, numpy as np
gem,out,crop,fit,regs=sys.argv[1:6]; partial=len(sys.argv)>6
up=cv2.imread(gem); o=cv2.imread(out); c=cv2.imread(crop)
o2=cv2.resize(o,(up.shape[1],up.shape[0]),interpolation=cv2.INTER_AREA)
g1=cv2.cvtColor(up,cv2.COLOR_BGR2GRAY); g2=cv2.cvtColor(o2,cv2.COLOR_BGR2GRAY)
mask=np.zeros(g1.shape,np.uint8)
for r in regs.split(';'):
    x0,y0,x1,y1=map(int,r.split(',')); mask[y0:y1,x0:x1]=255
orb=cv2.ORB_create(8000)
k1,d1=orb.detectAndCompute(g1,mask); k2,d2=orb.detectAndCompute(g2,mask)
bf=cv2.BFMatcher(cv2.NORM_HAMMING,crossCheck=True); m=sorted(bf.match(d2,d1),key=lambda x:x.distance)[:600]
src=np.float32([k2[x.queryIdx].pt for x in m]); dst=np.float32([k1[x.trainIdx].pt for x in m])
if partial: M,inl=cv2.estimateAffinePartial2D(src,dst,method=cv2.RANSAC,ransacReprojThreshold=2)
else: M,inl=cv2.estimateAffine2D(src,dst,method=cv2.RANSAC,ransacReprojThreshold=2)
warp=cv2.warpAffine(o2,M,(up.shape[1],up.shape[0]),borderMode=cv2.BORDER_REFLECT)
w=cv2.resize(warp,(c.shape[1],c.shape[0]),interpolation=cv2.INTER_AREA); cv2.imwrite(fit,w)
print('M',M.round(4).tolist(),'inliers',int(inl.sum()),'/',len(m))
