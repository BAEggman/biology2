#!/usr/bin/env python3
"""zcrop.py — 임의 사각형 조각(1배 좌표) + 올릴 배율. 사용: zcrop.py base2x.png NAME x0,y0,x1,y1 UP [--out DIR] [--gem PATH]
crop_NAME.png(2배 조각) · crop_NAME.json({box,scale:2}) · (gem) UP배로 올린 조각을 저장."""
import sys, json, argparse
from PIL import Image
ap=argparse.ArgumentParser(); ap.add_argument('base'); ap.add_argument('NAME'); ap.add_argument('box'); ap.add_argument('UP',type=float)
ap.add_argument('--out',default='.'); ap.add_argument('--gem',default='')
a=ap.parse_args(); box=[int(v) for v in a.box.split(',')]
im=Image.open(a.base); c=im.crop(tuple(v*2 for v in box)); c.save(f'{a.out}/crop_{a.NAME}.png')
json.dump({'name':a.NAME,'box':box,'scale':2},open(f'{a.out}/crop_{a.NAME}.json','w'))
if a.gem:
    g=c.resize((round(c.width*a.UP/2),round(c.height*a.UP/2)),Image.LANCZOS); g.save(a.gem); print('gem',g.size)
print('crop',a.NAME,box,c.size)
