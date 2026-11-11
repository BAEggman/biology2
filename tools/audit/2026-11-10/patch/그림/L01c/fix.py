from PIL import Image
import numpy as np
SP='/tmp/claude-0/-home-claude/adba3dea-fd2a-5075-a226-d8c1b6963879/scratchpad'
src=SP+'/L01c/r1/final_v2.png'
a=np.array(Image.open(src).convert('RGB')).astype(np.float32)
o=a.copy()
# --- 1. left seam: flat floor grey
rng=np.random.RandomState(1)
BG=np.array([181,181,181],np.float32)
for y in range(492,506):
    # outline start (crate edge) on this row
    x0=668
    for x in range(662,676):
        if a[y,x,0]<60: x0=x;break
    # pole diagonal outline: pixels right of it begin at xs
    for x in range(581,x0):
        if y>=499:
            # pole outline diagonal: dark pixels near x<=578+(y-499)+4
            if x<=580+(y-500) and x<600: continue
        o[y,x]=BG
# --- 2. step under neck's right wall: remove black line, split colours
WALL=np.array([120,127,126],np.float32)
for y in range(503,510):
    for x in range(834,855):
        # wall colour down to y=506, one-pixel blend row, plate colour (taken from row 511) below
        plate=a[511,x]
        t=1.0 if y<=506 else (0.5 if y==507 else 0.0)
        if y<=502: continue
        o[y,x]=t*WALL+(1-t)*plate
Image.fromarray(np.clip(o+0.5,0,255).astype(np.uint8)).save(SP+'/picfix/L01c/final_new.png')
