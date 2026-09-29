#!/usr/bin/env python3
"""s11p01 — (기록용) 둘째 걸음 제미나이 안내 그림: 지운 그림(CLEAN) 위에 판자 다섯을 평면으로 칠함. 이 안으로 받은 v3b 는 뾰족한 끝 없는 나무토막 넷 + 분기점까지 다시 그려 버려 **쓰지 않았다** — 판자는 s11p01_okazaki_planks.py 가 손으로 붙인다. 판자 자리(t, o)는 이 스크립트와 같은 틀이다."""
import numpy as np
from PIL import Image, ImageDraw
g=Image.open('s11p01_clean.png').convert('RGB'); dg=ImageDraw.Draw(g)
c0=np.array([496.0,640.0]); d=np.array([-0.7071,0.7071]); n=np.array([0.7071,0.7071])
def P(t,o): return c0+d*t+n*o
WOOD=(206,158,98); OUT=(60,40,25)
planks=[(58,130,12),(138,210,-2),(218,290,-8),(298,370,-8),(378,450,-4)]
for (t0,t1,o) in planks:
    w=12; tip=14
    poly=[P(t0,o-w),P(t1-tip,o-w),P(t1,o),P(t1-tip,o+w),P(t0,o+w)]
    dg.polygon([tuple(p) for p in poly],fill=WOOD)
    dg.line([tuple(p) for p in poly+[poly[0]]],fill=OUT,width=2)
    nx,ny=P(t0+8,o)
    dg.ellipse([nx-5,ny-5,nx+5,ny+5],fill=(70,70,75),outline=(20,20,20))
g.save('s11p01_guide3.png'); g.save('/mnt/user-data/outputs/gem/cur_s11p01_guide3.png')
g.crop((40,520,720,1000)).save('z_s11_guide3.png')
print('joint', P(294,-8).round(), 'newest', P(58,12).round(), P(130,12).round())
