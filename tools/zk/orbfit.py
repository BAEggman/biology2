#!/usr/bin/env python3
"""orbfit.py — 되돌아온 조각(틀이 달라진 것)을 올린 조각(gem)에 ORB 유사변환으로 정합해 crop 크기로 되돌린다.
사용: orbfit.py gem_upload.png out.png crop.png fitted.png   → fitted.png (crop 크기)"""
import sys, cv2, numpy as np
gem,out,crop,fit=sys.argv[1:5]
up=cv2.imread(gem); o=cv2.imread(out); c=cv2.imread(crop)
g1=cv2.cvtColor(up,cv2.COLOR_BGR2GRAY); g2=cv2.cvtColor(o,cv2.COLOR_BGR2GRAY)
orb=cv2.ORB_create(6000); k1,d1=orb.detectAndCompute(g1,None); k2,d2=orb.detectAndCompute(g2,None)
bf=cv2.BFMatcher(cv2.NORM_HAMMING,crossCheck=True); m=sorted(bf.match(d2,d1),key=lambda x:x.distance)[:600]
src=np.float32([k2[x.queryIdx].pt for x in m]); dst=np.float32([k1[x.trainIdx].pt for x in m])
M,inl=cv2.estimateAffinePartial2D(src,dst,method=cv2.RANSAC,ransacReprojThreshold=4)
warp=cv2.warpAffine(o,M,(up.shape[1],up.shape[0]),borderMode=cv2.BORDER_REFLECT)
w=cv2.resize(warp,(c.shape[1],c.shape[0]),interpolation=cv2.INTER_AREA); cv2.imwrite(fit,w)
print('M',M.round(3).tolist(),'inliers',int(inl.sum()))
