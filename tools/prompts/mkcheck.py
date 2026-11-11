# mkcheck.py <lid> <outdir> <sid,sid,...> — 일치 검사 판: full.jpg · s*.jpg(상자 합 + 여백) · stops.tsv(sid · obj)
import json, sys, os
from PIL import Image
lid, out, sids = sys.argv[1], sys.argv[2], sys.argv[3].split(',')
os.makedirs(out, exist_ok=True)
d = json.load(open(f'/tmp/b2/lessons/{lid}.json', encoding='utf-8'))
im = Image.open(f'/tmp/b2/lesson/img/{lid}.webp').convert('RGB')
im.resize((1400, round(im.height * 1400 / im.width)), Image.LANCZOS).save(f'{out}/full.jpg', quality=88)
rows = []
for sid in sids:
    s = next(s for s in d['stops'] if s['sid'] == sid); b = s.get('box')
    rows.append(f"{sid}\t{s['obj']}")
    if not b: continue
    bs = b if isinstance(b[0], list) else [b]
    x0 = min(x for x, y, w, h in bs); y0 = min(y for x, y, w, h in bs)
    x1 = max(x + w for x, y, w, h in bs); y1 = max(y + h for x, y, w, h in bs)
    m = 60; x0 = max(0, x0 - m); y0 = max(0, y0 - m); x1 = min(im.width, x1 + m); y1 = min(im.height, y1 + m)
    c = im.crop((x0, y0, x1, y1)); sc = min(1000 / c.width, 800 / c.height, 3)
    c.resize((round(c.width * sc), round(c.height * sc)), Image.LANCZOS).save(f'{out}/{sid}.jpg', quality=88)
open(f'{out}/stops.tsv', 'w', encoding='utf-8').write('\n'.join(rows) + '\n')
print(lid, len(rows), 'stops →', out)
