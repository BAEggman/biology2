import numpy as np, cv2
from PIL import Image, ImageDraw
SP='/tmp/claude-0/-home-claude/adba3dea-fd2a-5075-a226-d8c1b6963879/scratchpad'
A=np.array(Image.open(SP+'/L16a/r1/final_v1.png').convert('RGB'))
out=A.copy()
# crop frame used for measuring: origin (1340,400), 9.09x
OX,OY,K=1340,400,1000/110.0
c2p=lambda pts:[(OX+x/K,OY+y/K) for x,y in pts]
x0,y0,x1,y1=1360,410,1420,470
poly=c2p([(255,490),(270,400),(350,300),(440,225),(520,180),(578,172),(640,225),(662,255),(662,548),(600,505),(545,460),(500,500),(440,540),(380,505),(320,470)])
m=Image.new('L',(x1-x0,y1-y0),0)
ImageDraw.Draw(m).polygon([(x-x0,y-y0) for x,y in poly],fill=255)
m=np.array(m)>0
# keep the head outline (below the line) intact
ln=c2p([(200,470),(290,500),(350,520),(430,552),(470,600)])
lx=[p[0] for p in ln]; ly=[p[1] for p in ln]
yy,xx=np.mgrid[y0:y1,x0:x1]
below=yy>=np.interp(xx+0.5,lx,ly)-0.2
m&=~below
m=cv2.dilate(m.astype(np.uint8),np.ones((3,3),np.uint8))>0
m&=~(yy>=np.interp(xx+0.5,lx,ly)+0.5)&(xx<=1413)
# glass colour model: plane fitted on clean glass pixels around the piece
gy,gx=np.mgrid[412:476,1362:1413]
gs=A[412:476,1362:1413].astype(float)
ok=(gs[:,:,1]>215)&(gs[:,:,2]>232)&(gs[:,:,0]>185)
X=np.c_[np.ones(ok.sum()),gx[ok],gy[ok]]
co=[np.linalg.lstsq(X,gs[:,:,c][ok],rcond=None)[0] for c in range(3)]
fill=np.stack([co[c][0]+co[c][1]*xx+co[c][2]*yy for c in range(3)],-1)
# feathered mask (2 px) so no hard seam
mf=cv2.GaussianBlur(m.astype(np.float32),(0,0),1.0)
mf=np.clip(mf*1.6,0,1); mf[m]=1.0
mf[(xx>1413)]=0
res=A[y0:y1,x0:x1].astype(float)*(1-mf[:,:,None])+fill*mf[:,:,None]
out[y0:y1,x0:x1]=np.round(res).astype(np.uint8)
Image.fromarray(out).save(SP+'/picfix/L16a/final_new.png')
