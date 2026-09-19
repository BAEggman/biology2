#!/usr/bin/env python3
"""설치 레시피 한 줄: python3 tools/install_img.py <pid> <src.png>
(247,241,224) 위에 합성 → 너비 1024 LANCZOS → img/<pid>.webp (q92 m6) + tools/blind/png/<pid>.png"""
import sys, os
from PIL import Image
pid, src = sys.argv[1], sys.argv[2]
im = Image.open(src).convert('RGBA')
bg = Image.new('RGBA', im.size, (247, 241, 224, 255)); bg.alpha_composite(im); im = bg.convert('RGB')
w = 1024; h = round(im.height * w / im.width)
im = im.resize((w, h), Image.LANCZOS)
im.save('img/%s.webp' % pid, 'WEBP', quality=92, method=6)
os.makedirs('tools/blind/png', exist_ok=True)
im.save('tools/blind/png/%s.png' % pid, 'PNG')
print(pid, im.size, os.path.getsize('img/%s.webp' % pid))
