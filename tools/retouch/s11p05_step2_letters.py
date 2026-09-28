import cv2, numpy as np, sys
from PIL import Image
out=cv2.imread('s11p05_step1.png')
g=cv2.cvtColor(out,cv2.COLOR_BGR2GRAY).astype(np.float32)
hsv=cv2.cvtColor(out,cv2.COLOR_BGR2HSV).astype(int)
H,S,V=hsv[...,0],hsv[...,1],hsv[...,2]
# face polygon (shrunk ~2px)
poly=np.array([[798,690],[838,690],[811,884],[773,884]],np.int32)
# refine polygon from traced edges: left x_L(y)=796-(y-690)*0.131, right x_R(y)=836-(y-690)*0.128
ys=np.arange(700,882)
left=[(int(796-(y-690)*0.131)+2,y) for y in ys]
right=[(int(837.5-(y-690)*0.130)-2,y) for y in ys[::-1]]
poly=np.array(left+right,np.int32)
face=np.zeros(g.shape,np.uint8); cv2.fillPoly(face,[poly],1)
wood=((H>=17)&(H<=27)&(V>=185)).astype(np.uint8)
wood=cv2.morphologyEx(wood,cv2.MORPH_CLOSE,np.ones((5,5),np.uint8))
hand=((H<=16)&(S>=30)).astype(np.uint8)
hand=cv2.dilate(hand,np.ones((5,5),np.uint8))
mask=(face&wood&(1-hand)).astype(np.float32)
# letters sprite
sx0,sx1,sy0,sy1=651,688,728,848
spr=out[sy0:sy1,sx0:sx1].copy().astype(np.float32)
sg=g[sy0:sy1,sx0:sx1]
woodv=np.median(sg[sg>180]); ink=np.percentile(sg,3)
alpha=np.clip((woodv-sg)/(woodv-ink),0,1); alpha[alpha<0.12]=0; alpha=np.clip(alpha*1.25,0,1)
ang=float(sys.argv[1]); cx=float(sys.argv[2]); cy=float(sys.argv[3]); sc=float(sys.argv[4]) if len(sys.argv)>4 else 1.0
pad=24
A=cv2.copyMakeBorder(alpha,pad,pad,pad,pad,cv2.BORDER_CONSTANT,value=0)
Sp=cv2.copyMakeBorder(spr,pad,pad,pad,pad,cv2.BORDER_REPLICATE)
c=(A.shape[1]/2,A.shape[0]/2)
M=cv2.getRotationMatrix2D(c,ang,sc)
Ar=cv2.warpAffine(A,M,(A.shape[1],A.shape[0]),flags=cv2.INTER_LINEAR)
Sr=cv2.warpAffine(Sp,M,(Sp.shape[1],Sp.shape[0]),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE)
ox,oy=int(round(cx-c[0])),int(round(cy-c[1]))
H_,W_=Ar.shape
roi=out[oy:oy+H_,ox:ox+W_].astype(np.float32)
f=(Ar*mask[oy:oy+H_,ox:ox+W_])[...,None]
out[oy:oy+H_,ox:ox+W_]=(roi*(1-f)+Sr*f).astype(np.uint8)
cv2.imwrite('s11p05_rt.png',out)
I=Image.fromarray(cv2.cvtColor(out,cv2.COLOR_BGR2RGB))
I.crop((640,650,1000,920)).resize((1080,810),Image.LANCZOS).save('s11p05_rt_man.jpg',quality=92)
I.resize((768,768),Image.LANCZOS).save('s11p05_rt.jpg',quality=90)
print('mask px in face', int(mask.sum()), 'face px', int(face.sum()))
