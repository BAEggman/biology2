"""zone_kit finish 의 ✦ 메우기만 떼어 PNG 로 (언샤프·webp 없이). usage: wm_fill.py in.png out.png x0,y0,x1,y1 [...]"""
import sys, numpy as np
from PIL import Image
from scipy.ndimage import median_filter, binary_dilation, label
im=np.asarray(Image.open(sys.argv[1]).convert('RGB')).astype(float); out=sys.argv[2]
for box in sys.argv[3:]:
    x0,y0,x1,y1=map(int,box.split(',')); sub=im[y0:y1,x0:x1].copy(); lum=sub.mean(2)
    h,w=lum.shape; yy,xx=np.mgrid[0:h,0:w]
    ell=(((xx-w/2)/(w/2))**2+((yy-h/2)/(h/2))**2)<=1
    m=((lum-median_filter(lum,size=31))>6)&ell; lab,n=label(m)
    cand=[i for i in range(1,n+1) if (lab==i).sum()>=30]
    if not cand: print('wm',box,'밝은 덩어리 없음'); continue
    def dist(i):
        ys,xs=np.where(lab==i); return (ys.mean()-h/2)**2+(xs.mean()-w/2)**2
    best=min(cand,key=dist); mm=binary_dilation(lab==best,iterations=2)
    Image.fromarray(np.clip(np.concatenate([sub,np.where(mm[...,None],[255,0,255],sub)],1),0,255).astype('uint8')).resize((4*w,2*h)).save(out+f'.wm_{x0}_{y0}.png')
    o1=sub.copy(); o2=sub.copy()
    for y in range(mm.shape[0]):
        if mm[y].any():
            k=np.where(~mm[y])[0]
            for c in range(3): o1[y,:,c]=np.interp(np.arange(mm.shape[1]),k,sub[y,k,c])
    for x in range(mm.shape[1]):
        if mm[:,x].any():
            k=np.where(~mm[:,x])[0]
            for c in range(3): o2[:,x,c]=np.interp(np.arange(mm.shape[0]),k,sub[k,x,c])
    f=(o1+o2)/2+np.random.default_rng(1).normal(0,1.2,sub.shape); sub[mm]=f[mm]; im[y0:y1,x0:x1]=sub
    print('wm',box,'메움',int(mm.sum()),'px')
Image.fromarray(np.clip(im,0,255).astype('uint8')).save(out); print('saved',out)
