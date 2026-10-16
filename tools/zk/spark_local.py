"""spark_local.py IMG x0,y0,x1,y1 — 지정 구역에서 제미나이 별(p 0.69) 자리·R 을 찾는다(안 2px − 밖 2px 대비, 고역 밝기)."""
import sys, numpy as np, cv2
from PIL import Image
from scipy import ndimage as ndi
P=0.69; S=8
def star(R,n,fx,fy):
    c=n/2.0; ys=(np.arange(n*S)+0.5)/S-0.5; XX,YY=np.meshgrid(ys,ys)
    m=((np.abs(XX-(c+fx))/R)**P+(np.abs(YY-(c+fy))/R)**P<=1).astype(float)
    return m.reshape(n,S,n,S).mean(axis=(1,3))
A=np.asarray(Image.open(sys.argv[1]).convert('RGB')).astype(np.float32); L=A.mean(axis=2)
x0,y0,x1,y1=map(int,sys.argv[2].split(','))
sub=L[y0:y1,x0:x1]; hp=(sub-ndi.median_filter(sub,size=31)).astype(np.float32)
res=[]
for R in np.arange(9,24,0.5):
    n=int(2*R+12)
    for fx in (0,0.5):
        for fy in (0,0.5):
            m=star(R,n,fx,fy); inn=(m>0.5)&(ndi.binary_erosion(m>0.5,iterations=2)==0); out=(ndi.binary_dilation(m>0.5,iterations=2))&~(m>0.5)
            k=inn/inn.sum()-out/out.sum(); k=k.astype(np.float32)
            r=cv2.filter2D(hp,-1,k,borderType=cv2.BORDER_REFLECT)
            iy,ix=np.unravel_index(np.argmax(r),r.shape)
            # filter2D anchor = kernel center n//2; star center = n/2 + f
            cx=x0+ix-n//2+n/2.0+fx; cy=y0+iy-n//2+n/2.0+fy
            res.append((float(r[iy,ix]),R,cx-0.5,cy-0.5))
res.sort(reverse=True)
for v in res[:8]: print('대비 %.1f R %.1f cx %.1f cy %.1f'%v)
