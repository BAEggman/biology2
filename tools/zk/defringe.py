"""defringe.py — 오려 붙인 인물·물건 둘레의 흰 테두리(헤일로)를 둘레 배경색으로 메운다.
python3 defringe.py in.png out.png x0,y0,x1,y1 [--white 232] [--near 5] [--dark 95]
윤곽선(어두운 화소) 바깥쪽(영역 테두리에서 윤곽선을 넘지 않고 닿는 곳)에서, 윤곽선 근처의 희고 채도 낮은 화소만 바꾼다."""
import sys, argparse, numpy as np
from PIL import Image
from scipy import ndimage
ap=argparse.ArgumentParser(); ap.add_argument('inp'); ap.add_argument('out'); ap.add_argument('box')
ap.add_argument('--white',type=float,default=232); ap.add_argument('--near',type=int,default=5); ap.add_argument('--dark',type=float,default=95)
a=ap.parse_args()
im=np.asarray(Image.open(a.inp).convert('RGB')).astype(float)
x0,y0,x1,y1=[int(v) for v in a.box.split(',')]
R=im[y0:y1,x0:x1].copy()
lum=R.mean(2); sat=R.max(2)-R.min(2)
dark=lum<a.dark
dark=ndimage.binary_closing(dark,iterations=1)
# outside = reachable from region border without crossing dark
free=~dark
lab,n=ndimage.label(free)
border=set(np.unique(np.concatenate([lab[0,:],lab[-1,:],lab[:,0],lab[:,-1]])))-{0}
outside=np.isin(lab,list(border))
near=ndimage.binary_dilation(dark,iterations=a.near)
white=(lum>a.white)&(sat<28)
cand=outside&near&white
# background = outside pixels not candidates and not near outline
bgm=outside&~cand&~ndimage.binary_dilation(dark,iterations=2)
out=R.copy()
w=ndimage.gaussian_filter(bgm.astype(float),4)
for c in range(3):
    num=ndimage.gaussian_filter(R[...,c]*bgm,4)
    est=num/np.maximum(w,1e-3)
    out[...,c][cand]=est[cand]
im2=im.copy(); im2[y0:y1,x0:x1]=out
Image.fromarray(np.clip(im2,0,255).astype('uint8')).save(a.out)
print('changed px',int(cand.sum()))
