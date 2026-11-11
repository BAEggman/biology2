import numpy as np
from PIL import Image
SP='/tmp/claude-0/-home-claude/adba3dea-fd2a-5075-a226-d8c1b6963879/scratchpad'
a=np.array(Image.open(SP+'/L46a/r1/final_v1.png').convert('RGB'))
o=a.copy()
# (1) light-pink sliver right of the inner wall line -> continue the brown wall column downward
for x in range(1352,1362):
    o[793:833,x]=a[791,x]
    o[832,x]=(a[791,x]*0.75).astype(np.uint8); o[833,x]=(a[791,x]*0.4).astype(np.uint8)
# (2) stair/bump at top of the pink in the narrow strip left of the line: flatten at y=799
for x in range(1341,1346):
    o[793:799,x]=a[791,x]
Image.fromarray(o).save(SP+'/picfix/L46a/final_new.png')
