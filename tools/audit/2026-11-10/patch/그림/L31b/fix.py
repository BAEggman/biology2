from PIL import Image, ImageDraw
import numpy as np
SP='/tmp/claude-0/-home-claude/adba3dea-fd2a-5075-a226-d8c1b6963879/scratchpad'
src=SP+'/L31b/r1/final_v1.png'
im=Image.open(src).convert('RGB')
X0,Y0,X1,Y1=560,540,640,625
S=8
crop=im.crop((X0,Y0,X1,Y1))
big=crop.resize((crop.width*S,crop.height*S),Image.NEAREST)
d=ImageDraw.Draw(big)
def P(pts): return [((x-X0)*S,(y-Y0)*S) for x,y in pts]
BG=(239,190,113); SH=(190,143,72); BR=(125,96,70); BRD=(106,78,64)
# clear the cut-edge strip (shoe right of x=598 region incl. light line) to bg first, only right of 600
d.rectangle(P([(600,556),(640,620)]),fill=BG)
# shadow extension
d.polygon(P([(597,605),(606,605),(611,604.5),(615,606.5),(613,609.5),(606,610.5),(597,610)]),fill=SH)
# outer black toe
outer=[(599,567.5),(603,568.5),(607,572),(609.8,577),(611,583),(610,589),(607,595),(602,600.5),(598,603.3),(593,604.3)]
d.polygon(P(outer),fill=(0,0,0))
inner=[(596.5,573.5),(599,572.5),(600.5,572),(603,573),(605.5,576),(607,580.5),(607.3,585),(606,590),(603,594.5),(599.5,598),(594,600),(594,584),(596.5,584)]
d.polygon(P(inner),fill=BR)
# darker shade strip along right inside
out=big.resize(crop.size,Image.BOX)
res=im.copy()
res.paste(out,(X0,Y0))
res.save(SP+'/picfix/L31b/final_new.png')
