#!/usr/bin/env python3
"""affit.py — 되돌아온 조각을 올린 조각(gem)에 ORB 전체 아핀(비등방 배율 포함)으로 정합해 crop 크기로 되돌린다.
사용: affit.py gem_upload.png out.png crop.png fitted.png"""
import sys, cv2, numpy as np
gem,out,crop,fit=sys.argv[1:5]
up=cv2.imread(gem); o=cv2.imread(out); c=cv2.imread(crop)
# 먼저 출력 그림을 gem 크기로 비등방 리사이즈(틀이 같은 경우 대부분 이걸로 끝)
o2=cv2.resize(o,(up.shape[1],up.shape[0]),interpolation=cv2.INTER_AREA)
g1=cv2.cvtColor(up,cv2.COLOR_BGR2GRAY); g2=cv2.cvtColor(o2,cv2.COLOR_BGR2GRAY)
orb=cv2.ORB_create(8000); k1,d1=orb.detectAndCompute(g1,None); k2,d2=orb.detectAndCompute(g2,None)
bf=cv2.BFMatcher(cv2.NORM_HAMMING,crossCheck=True); m=sorted(bf.match(d2,d1),key=lambda x:x.distance)[:800]
src=np.float32([k2[x.queryIdx].pt for x in m]); dst=np.float32([k1[x.trainIdx].pt for x in m])
M,inl=cv2.estimateAffine2D(src,dst,method=cv2.RANSAC,ransacReprojThreshold=3)
warp=cv2.warpAffine(o2,M,(up.shape[1],up.shape[0]),borderMode=cv2.BORDER_REFLECT)
w=cv2.resize(warp,(c.shape[1],c.shape[0]),interpolation=cv2.INTER_AREA); cv2.imwrite(fit,w)
print('M',M.round(4).tolist(),'inliers',int(inl.sum()),'/',len(m))
