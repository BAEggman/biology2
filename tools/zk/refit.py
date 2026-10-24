"""refit.py crop.png out.png fitted.png — 비율이 달라진 Gemini 결과를 높이로 맞추고 가로 어긋남(ox)을 찾아 조각 크기(488×H)로 되돌린다(빈 자리는 조각 화소)."""
import sys, numpy as np
from PIL import Image
c=Image.open(sys.argv[1]).convert('RGB'); z=Image.open(sys.argv[2]).convert('RGB')
W,H=c.size; zw=round(z.width*H/z.height); z=z.resize((zw,H),Image.LANCZOS)
C=np.asarray(c).astype(float); Z=np.asarray(z).astype(float)
best=None
for ox in range(-60,61):
    xs=max(0,ox); xe=min(W,ox+zw); 
    if xe-xs<W*0.6: continue
    a=C[:, xs:xe]; b=Z[:, xs-ox:xe-ox]
    e=np.mean((a-b)**2)
    if best is None or e<best[0]: best=(e,ox)
e,ox=best
out=C.copy(); xs=max(0,ox); xe=min(W,ox+zw); out[:, xs:xe]=Z[:, xs-ox:xe-ox]
Image.fromarray(np.clip(out,0,255).astype('uint8')).save(sys.argv[3])
print(f'zw={zw} ox={ox} mse={e:.1f}')
