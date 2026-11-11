import numpy as np
from PIL import Image, ImageDraw
SP='/tmp/claude-0/-home-claude/adba3dea-fd2a-5075-a226-d8c1b6963879/scratchpad'
A=np.array(Image.open(SP+'/L49c/r1/final_v1.png').convert('RGB'))
out=A.copy()
S=8
WATER=(125,193,230); INK=(6,12,10)
# ---------- 1. left end of the left puddle: round lobes + cusps, outlines closed ----------
x0,y0,x1,y1=782,880,850,1000
big=Image.fromarray(A[y0:y1,x0:x1]).resize(((x1-x0)*S,(y1-y0)*S),Image.NEAREST)
d=ImageDraw.Draw(big)
P=lambda pts:[((x-x0)*S,(y-y0)*S) for x,y in pts]
def bez(p0,c1,c2,p3,n=40):
    t=np.linspace(0,1,n)[:,None]
    p0,c1,c2,p3=map(np.array,(p0,c1,c2,p3))
    return [tuple(v) for v in ((1-t)**3*p0+3*(1-t)**2*t*c1+3*(1-t)*t**2*c2+t**3*p3)]
# cusp where the top outline meets the upper edge of the first sand bay
cusp=(806.4,895.0)
# lobe A: between first sand bay and second sand bay
lobeA=bez((810.5,911.0),(800.5,917.0),(799.5,935.5),(810.5,939.0))
# lobe B: below the second sand bay up to the bottom outline
lobeB=bez((810.5,954.5),(802.5,957.5),(801.5,965.5),(810.5,966.6))
# water fill inside the new lobes (drawn first, outline afterwards)
nose=bez((813,890.8),(803.0,892.0),(803.0,897.8),(813,899.4))
d.polygon(P(nose+[(813,890.8)]),fill=WATER)
d.polygon(P(lobeA+[(811.5,939.0),(811.5,911.0)]),fill=WATER)
d.polygon(P(lobeB+[(811.5,966.6),(811.5,954.5)]),fill=WATER)
def stroke(pts,w):
    q=P(pts); d.line(q,fill=INK,width=int(round(w*S)),joint='curve')
    r=w*S/2
    for (px,py) in (q[0],q[-1]): d.ellipse([px-r,py-r,px+r,py+r],fill=INK)
stroke(nose,2.8)
stroke([(814,908.5),(810.5,911.0)]+lobeA[1:-1]+[(810.5,939.0),(813,939.4)],2.8)
stroke([(813.5,953.4),(810.5,954.5)]+lobeB[1:-1]+[(810.5,966.6),(813,967.0)],2.8)
# tip of the little oval puddle below
stroke([(812,981.8),(809.6,984.2),(812,987.2)],2.2)
patch=np.array(big.resize((x1-x0,y1-y0),Image.BOX))
out[y0:y1,x0:x1]=patch
# ---------- 2. white sliver between right puddle and first grape pile ----------
for y in range(917,929):
    for x in range(1232,1244):
        r,g,b=[int(v) for v in A[y,x]]
        if g>215 and b>240:
            # purple side only: a dark outline pixel lies to the left in this row
            if any(int(A[y,xx].sum())<150 for xx in range(x-4,x)):
                for xx in range(x+2,x+8):
                    r2,g2,b2=[int(v) for v in A[y,xx]]
                    if not (g2>215 and b2>240) and int(A[y,xx].sum())>200:
                        out[y,x]=A[y,xx]; break
                else:
                    out[y,x]=A[y+3,x+2]
import cv2
m=np.zeros(out.shape[:2],np.uint8)
for (yy,xx) in [(919,1238),(919,1239),(919,1240),(919,1241),(918,1240),(920,1240),(930,1229)]:
    m[yy,xx]=255
out=cv2.inpaint(out,m,2,cv2.INPAINT_TELEA)
Image.fromarray(out).save(SP+'/picfix/L49c/final_new.png')
