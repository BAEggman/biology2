#!/usr/bin/env python3
"""설치 레시피 한 줄: python3 tools/install_img.py <pid> <src.png>
(247,241,224) 위에 합성 → 크기 맞춤 LANCZOS → img/<pid>.webp (q92 m6) + tools/blind/png/<pid>.png
크기: 이미 설치본(tools/blind/png/<pid>.png)이 있고 비율이 같으면(1% 안) **그 크기 그대로**(10/1 — s07p05 687×1024 가 너비 1024 로 키워질 뻔한 일 뒤로),
      없으면 너비 1024."""
import sys, os
from PIL import Image
pid, src = sys.argv[1], sys.argv[2]
im = Image.open(src).convert('RGBA')
bg = Image.new('RGBA', im.size, (247, 241, 224, 255)); bg.alpha_composite(im); im = bg.convert('RGB')
old = 'tools/blind/png/%s.png' % pid
w = 1024; h = round(im.height * w / im.width)
if os.path.exists(old):
    ow, oh = Image.open(old).size
    if abs(ow / oh - im.width / im.height) < 0.01 * (ow / oh):
        w, h = ow, oh
    else:
        print('⚠ 비율이 설치본(%dx%d)과 달라 너비 1024 로 설치' % (ow, oh))
if im.size != (w, h):
    im = im.resize((w, h), Image.LANCZOS)
im.save('img/%s.webp' % pid, 'WEBP', quality=92, method=6)
os.makedirs('tools/blind/png', exist_ok=True)
im.save(old, 'PNG')
print(pid, im.size, os.path.getsize('img/%s.webp' % pid))
