import sys; sys.path.insert(0,'/tmp/L48a')
from lib import *
import numpy as np
from PIL import Image, ImageDraw
img=Image.open('w4.png').convert('RGB'); a=np.array(img)
src=a[700:730,1522:1562].copy()   # clean wood strip
for y0 in (600,630,660,690,750,780):
    a[y0:y0+30,1522:1562]=src
img=Image.fromarray(a)
T=112; S=round(T*0.6)
LR=(1250,575); RR=(1537,600)
seq=[('navy_c',T,511),('sky_c',S,610),('sky_c',T,710),('navy_c',S,809)]
specs=[]; plates=[]
def half(n,side,h):
    im=Image.open(f'/tmp/L48a/sp/half_{n}_{side}.png').convert('RGBA'); im=im.crop((0,0,im.width,int(im.height*0.97)))
    s=h/im.height; return im.resize((max(1,round(im.width*s*1.45)),round(h*0.92)),Image.LANCZOS)
for side,WX,RING in (('R',1286,LR),('L',1474,RR)):
    for n,h,cy in seq:
        sp=half(n,side,h)
        al=np.array(sp)[...,3]>128; mid=int(sp.height/2); xs=np.where(al[mid])[0]
        if side=='R': left=WX-xs.min(); px=WX
        else: left=WX-xs.max(); px=WX
        o=img.convert('RGBA'); o.alpha_composite(sp,(int(left),int(cy-sp.height/2))); img=o.convert('RGB')
        plates.append((px,cy,side)); 
        hx=px-11 if side=='R' else px+11
        specs.append((RING,(hx-3 if side=='R' else hx+3,cy),0))
img=ropes(img,specs,w=6.5)
d=ImageDraw.Draw(img)
for px,cy,side in plates:
    x0=px-6 if side=='R' else px-4
    d.rectangle([x0,cy-9,x0+10,cy+9],fill=(78,80,86),outline=(25,25,28),width=2)
    d.ellipse([x0+3,cy-6,x0+6,cy-3],fill=(170,172,178)); d.ellipse([x0+3,cy+3,x0+6,cy+6],fill=(170,172,178))
    img=hook(img,(px-11 if side=='R' else px+11),cy,-1 if side=='R' else 1,1.0); d=ImageDraw.Draw(img)
# silver C pieces
lay=Image.new('RGBA',(400*SS,400*SS),(0,0,0,0)); dl=ImageDraw.Draw(lay)
pieces=[(1372,585,16,30,250),(1408,645,15,200,60),(1366,705,16,120,330),(1404,765,15,300,160)]
OX,OY=1280,500
for cx,cy,r,a0,a1 in pieces:
    bx=[(cx-OX-r)*SS,(cy-OY-r)*SS,(cx-OX+r)*SS,(cy-OY+r)*SS]
    dl.arc(bx,a0,a1,fill=(25,25,30,255),width=int(10*SS))
    dl.arc(bx,a0,a1,fill=(196,200,208,255),width=int(6.5*SS))
    bi=[bx[0]+1.2*SS,bx[1]+1.2*SS,bx[2]-1.2*SS,bx[3]-1.2*SS]
    dl.arc(bi,a0+25,(a0+(a1-a0)%360*0.5),fill=(255,255,255,255),width=int(1.6*SS))
lay=lay.resize((400,400),Image.LANCZOS); o=img.convert('RGBA'); o.alpha_composite(lay,(OX,OY)); img=o.convert('RGB')
img.save('w4c.png')
