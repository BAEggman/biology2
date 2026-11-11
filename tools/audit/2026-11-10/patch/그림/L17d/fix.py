import numpy as np, cv2
from PIL import Image
SP='/tmp/claude-0/-home-claude/adba3dea-fd2a-5075-a226-d8c1b6963879/scratchpad'
A=np.array(Image.open(SP+'/L17d/r1/final_v1.png').convert('RGB'))
a=A.astype(np.float32)
Bch=A[:,:,2].astype(int)-A[:,:,0].astype(int)
ys=np.arange(660,866)
xl=[];xr=[]
for y in ys:
    xs=np.where(Bch[y,1730:1830]>12)[0]+1730
    xl.append(xs.min()); xr.append(xs.max())
pl=np.polyfit(ys,xl,3); pr=np.polyfit(ys,xr,3)
def bounds(y):
    yy=min(max(y,660),865)
    return np.polyval(pl,yy), np.polyval(pr,yy)
Y0,Y1=650,872
# wall colour per row: left sample (wall between door frame and band, only where it exists) and right sample, interpolated across
def samp(y,xa,xb): return np.median(a[y,xa:xb],axis=0)
colR=np.zeros((Y1-Y0,3),np.float32); colL=np.zeros((Y1-Y0,3),np.float32); hasL=np.zeros(Y1-Y0,bool)
for y in range(Y0,Y1):
    l,r=bounds(y); r=int(round(r)); l=int(round(l)) if y>=660 else 1773
    colR[y-Y0]=samp(y,r+8,r+18)
    if l-14>=1756:
        colL[y-Y0]=samp(y,l-14,l-9); hasL[y-Y0]=True
def vmed(arr):
    out=arr.copy()
    for i in range(len(arr)):
        out[i]=np.median(arr[max(0,i-9):min(len(arr),i+10)],axis=0)
    return out
colR=vmed(colR); colL=vmed(colL)
o=a.copy()
for y in range(Y0,Y1):
    l,r=bounds(y)
    xs=int(round(l))-7
    if y>=757: xs=int(round(l))
    else: xs=1754 if y>=690 else max(xs,1754)
    xe=int(round(r))+7
    if y<660: xs=1764; xe=1810
    for x in range(xs,xe+1):
        if hasL[y-Y0]:
            t=(x-xs)/float(max(1,xe-xs)); c=(1-t)*colL[y-Y0]+t*colR[y-Y0]
        else: c=colR[y-Y0]
        # 2px feather at the right/top/bottom borders so the fill melts into the untouched wall
        w=min(1.0,(xe-x+1)/2.5, (y-Y0+1)/3.0, (Y1-y)/3.0)
        o[y,x]=(1-w)*a[y,x]+w*c
# stray bluish anti-alias pixels left along the door-frame edge
for y in range(690,872):
    for x in range(1738,1772):
        p=o[y,x]
        if p[2]-p[0]>5 and p.mean()>40:
            o[y,x]=colL[y-Y0] if hasL[y-Y0] else colR[y-Y0]
# brick joint that ran behind the band (visible on both sides): draw it across, AA, sampled colour/thickness
S=4
H,W=240*S,120*S
lay=np.zeros((H,W),np.float32)
def pt(x,y): return (int((x-1700)*S),int((y-650)*S))
cv2.line(lay,pt(1750,780.0),pt(1790,788.0),1.0,int(2.6*S),cv2.LINE_AA)
lay=cv2.resize(lay,(120,240),interpolation=cv2.INTER_AREA)
joint=np.array([12,9,7],np.float32)
# only use the part left of x=1778 (the rest already exists in the original)
for yy in range(240):
    for xx in range(120):
        x=1700+xx; y=650+yy
        if x<1788 and x>=1748 and lay[yy,xx]>0:
            t=lay[yy,xx]
            o[y,x]=np.minimum(o[y,x],(1-t)*o[y,x]+t*joint)
Image.fromarray(np.clip(o+0.5,0,255).astype(np.uint8)).save(SP+'/picfix/L17d/final_new.png')
