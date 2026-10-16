"""draw_drops.py — 바다 빛 물방울(잉크 테두리 · 하이라이트)을 그린다. python3 draw_drops.py in.png out.png R Ht cx1,by1 cx2,by2 ..."""
import sys, math, numpy as np
from PIL import Image, ImageDraw, ImageFilter
S=8
def sprite(R,Ht):
    w=int(2*R+6); h=int(Ht+6)
    big=Image.new('RGBA',(w*S,h*S),(0,0,0,0)); d=ImageDraw.Draw(big)
    cx=w/2; by=h-3; cyc=by-R; tip=(cx,by-Ht)
    dist=cyc-tip[1]; ang=math.asin(R/dist); ty=cyc-R*math.sin(ang)
    arc=[]
    for t in np.linspace(0,2*math.pi,240,endpoint=False):
        x=cx+R*math.cos(t); y=cyc+R*math.sin(t)
        if y>=ty-1e-6: arc.append((t,x,y))
    arc=sorted(arc,key=lambda p:(p[0]-(-math.pi/2+1e-9))%(2*math.pi))
    poly=[(tip[0]*S,tip[1]*S)]+[(x*S,y*S) for _,x,y in arc]
    d.polygon(poly,fill=(126,174,165,255))
    shade=Image.new('RGBA',big.size,(0,0,0,0)); sd=ImageDraw.Draw(shade)
    sd.ellipse([(cx-R*0.55)*S,(cyc-R*0.35)*S,(cx+R*0.55)*S,(cyc+R*0.75)*S],fill=(150,196,186,150))
    sd.ellipse([(cx-R*0.55)*S,(cyc-R*0.95)*S,(cx-R*0.05)*S,(cyc-R*0.25)*S],fill=(225,240,236,210))
    shade=shade.filter(ImageFilter.GaussianBlur(S*0.8))
    mask=Image.new('L',big.size,0); ImageDraw.Draw(mask).polygon(poly,fill=255)
    big=Image.composite(Image.alpha_composite(big,shade),big,mask)
    d=ImageDraw.Draw(big); d.line(poly+[poly[0]],fill=(56,74,66,255),width=int(1.6*S),joint='curve')
    return big.resize((w,h),Image.LANCZOS),(cx,by)
inp,outp,R,Ht=sys.argv[1],sys.argv[2],float(sys.argv[3]),float(sys.argv[4])
img=Image.open(inp).convert('RGBA'); sp,(ax,ay)=sprite(R,Ht)
for p in sys.argv[5:]:
    cx,by=[float(v) for v in p.split(',')]
    img.alpha_composite(sp,(int(round(cx-ax)),int(round(by-ay))))
img.convert('RGB').save(outp)
