import numpy as np, math
from PIL import Image, ImageDraw
SS=4
OUT=(42,34,28); IN=(224,203,165); TICK=(150,118,84)
def _pts(p0,p1,sag,n=40):
    (x0,y0),(x1,y1)=p0,p1; pts=[]
    for i in range(n+1):
        t=i/n; x=x0+(x1-x0)*t; y=y0+(y1-y0)*t+sag*4*t*(1-t); pts.append((x,y))
    return pts
def ropes(img, specs, w=6.0):
    """specs: list of (p0,p1,sag). draws on RGB image in place (returns new)."""
    W,H=img.size
    xs=[p for s in specs for p in (s[0],s[1])]; 
    x0=int(min(p[0] for p in xs))-40; y0=int(min(p[1] for p in xs))-40-int(max(0,min(s[2] for s in specs)))
    x1=int(max(p[0] for p in xs))+40; y1=int(max(p[1] for p in xs))+40+int(max(0,max(s[2] for s in specs)))
    x0,y0=max(0,x0),max(0,y0); x1,y1=min(W,x1),min(H,y1)
    lay=Image.new('RGBA',((x1-x0)*SS,(y1-y0)*SS),(0,0,0,0)); d=ImageDraw.Draw(lay)
    for p0,p1,sag in specs:
        pts=[((x-x0)*SS,(y-y0)*SS) for x,y in _pts(p0,p1,sag)]
        d.line(pts,fill=OUT+(255,),width=int(w*SS),joint='curve')
        d.line(pts,fill=IN+(255,),width=int((w-2.6)*SS),joint='curve')
        # ticks every ~7px along the rope
        L=0; acc=0
        for (ax,ay),(bx,by) in zip(pts,pts[1:]):
            seg=math.hypot(bx-ax,by-ay); 
            if seg==0: continue
            ux,uy=(bx-ax)/seg,(by-ay)/seg; nx,ny=-uy,ux
            s=0
            while s<seg:
                if (acc+s)%(7*SS)<1*SS and (acc+s)>4*SS:
                    cx,cy=ax+ux*s,ay+uy*s; h=(w-2.6)*SS/2
                    d.line([(cx+nx*h-ux*1.5*SS,cy+ny*h-uy*1.5*SS),(cx-nx*h+ux*1.5*SS,cy-ny*h+uy*1.5*SS)],fill=TICK+(255,),width=int(1.2*SS))
                s+=1*SS/2
            acc+=seg
    lay=lay.resize((x1-x0,y1-y0),Image.LANCZOS)
    out=img.convert('RGBA'); out.alpha_composite(lay,(x0,y0)); return out.convert('RGB')
def hook(img, x, y, side, s=1.0):
    """small dark hook at (x,y) (attachment point = hook tip), side=-1 left(opens left) / +1 right"""
    r=int(9*s); lay=Image.new('RGBA',((2*r+8)*SS,(2*r+8)*SS),(0,0,0,0)); d=ImageDraw.Draw(lay)
    c=(r+4)*SS
    box=[c-r*SS*0.6,c-r*SS*0.6,c+r*SS*0.6,c+r*SS*0.6]
    a0,a1=(90,330) if side>0 else (210,450)
    d.arc(box,a0,a1,fill=(30,30,34,255),width=int(4*s*SS)); d.arc(box,a0,a1,fill=(95,98,105,255),width=int(1.6*s*SS))
    lay=lay.resize((2*r+8,2*r+8),Image.LANCZOS); out=img.convert('RGBA'); out.alpha_composite(lay,(int(x-r-4),int(y-r-4))); return out.convert('RGB')
def sprite(name, h, flip=False, wscale=1.0):
    im=Image.open(f'/tmp/L48a/sp/{name}.png').convert('RGBA')
    bb=im.getbbox(); im=im.crop(bb)
    s=h/im.height; im=im.resize((max(1,round(im.width*s*wscale)),round(h)),Image.LANCZOS)
    if flip: im=im.transpose(Image.FLIP_LEFT_RIGHT)
    return im
def place(img, spr, cx, cy):
    out=img.convert('RGBA'); out.alpha_composite(spr,(int(round(cx-spr.width/2)),int(round(cy-spr.height/2)))); return out.convert('RGB')
def waist(spr, cx, cy):
    """returns waist y and plate x extents (left,right) in image coords, using ring row (metal pixels)"""
    a=np.array(spr); al=a[...,3]>128; rgb=a[...,:3].astype(int)
    mx=rgb.max(2); mn=rgb.min(2); metal=al&((mx-mn)<30)&(mx>90)
    rows=metal.sum(1); wy=int(np.argmax(rows)); xs=np.where(al[wy])[0]
    top=cy-spr.height/2; left=cx-spr.width/2
    return top+wy, left+xs.min(), left+xs.max()
def dashes(img, x, y0, y1, start=118, period=38.25, L=18, w=4):
    d=ImageDraw.Draw(img); y=start
    while y<y1:
        if y+L>y0: d.rectangle([x-w/2, max(y,y0), x+w/2-1, min(y+L,y1)], fill=(246,244,236))
        y+=period
    return img
def place_rot(img, spr, cx, cy, ang):
    """rotate sprite by ang degrees (counterclockwise), place centered; return img, hooks (left,right) world points"""
    a=np.array(spr); al=a[...,3]>128; rgb=a[...,:3].astype(int)
    mx=rgb.max(2); mn=rgb.min(2); metal=al&((mx-mn)<30)&(mx>90)
    wy=int(np.argmax(metal.sum(1))); xs=np.where(al[wy])[0]
    w,h=spr.size; pts=[(xs.min()-5,wy),(xs.max()+5,wy)]
    r=spr.rotate(ang,resample=Image.BICUBIC,expand=True)
    th=math.radians(ang); out=[]
    for px,py in pts:
        dx,dy=px-w/2,py-h/2
        rx=dx*math.cos(th)+dy*math.sin(th); ry=-dx*math.sin(th)+dy*math.cos(th)
        out.append((cx+rx,cy+ry))
    o=img.convert('RGBA'); o.alpha_composite(r,(int(round(cx-r.width/2)),int(round(cy-r.height/2))))
    return o.convert('RGB'), out
def plate(img, x, y, side, s=1.0):
    """riveted dark steel plate centered at (x,y) + hook on the outer side; returns (img, tie point)"""
    d=ImageDraw.Draw(img); w=int(10*s); h=int(18*s)
    d.rectangle([x-w//2,y-h//2,x+w//2,y+h//2],fill=(78,80,86),outline=(25,25,28),width=2)
    r=max(1,int(1.8*s)); 
    for yy in (y-h//2+5, y+h//2-5): d.ellipse([x-r,yy-r,x+r,yy+r],fill=(175,178,184))
    hx=x+side*(w//2+7*s)
    img=hook(img,hx,y,side,1.1*s)
    return img,(hx+side*3,y)
