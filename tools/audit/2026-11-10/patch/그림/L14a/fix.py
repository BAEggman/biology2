import numpy as np
from PIL import Image
SP='/tmp/claude-0/-home-claude/adba3dea-fd2a-5075-a226-d8c1b6963879/scratchpad'
a=np.array(Image.open(SP+'/L14a/r1/final_v1.png').convert('RGB')).astype(np.float32)
o=a.copy()
base=a[997,1578:1681]                       # last clean wood row (grain lines, right wall edge)
lref=a[997,1571:1578].mean(axis=0)
for y in range(999,1019):
    delta=a[y,1571:1578].mean(axis=0)-lref   # floor-side bevel shading, taken from the intact wood to the left
    o[y,1578:1681]=np.clip(base+delta,0,255)
Image.fromarray(np.clip(o+0.5,0,255).astype(np.uint8)).save(SP+'/picfix/L14a/final_new.png')
