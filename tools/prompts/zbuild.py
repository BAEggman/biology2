#!/usr/bin/env python3
"""zbuild.py <recipe.json> [--write] — 4단계(그림 고침 · 2026-11-22 · Opus 5.5)의 그림을 다시 만드는 길.

recipe.json (그 과의 tools/prompts/<ID>_src/ 에 둔다 — 경로는 recipe 가 있는 폴더 기준):
  {"lesson": "L36c", "base": "<커밋>",                        바탕 = git show <커밋>:lesson/img/<ID>.webp
   "steps": [
     {"zone": "A", "crop": [x0, y0, x1, y1],                  zone3.py crop — 지금까지의 결과에서 오린다
      "gem": "gem_A1.webp", "allow": "x0,y0,x1,y1[;…]",       Gemini 가 돌려준 그림(무손실 webp) · 붙일 상자(바탕 좌표)
      "thr": 28, "opts": ["--ident", "--R=14", "--fit=…"]},    zone3.py paste 의 선택(없으면 기본)
     {"pil": "pil_x.py", "args": []}                          python3 <pil> <들어갈 png> <나올 png> [args…]
   ]}
결과는 WEBP quality 85 · method 6. --write 면 lesson/img/<ID>.webp 에 쓰고, 아니면 /tmp/zbuild/<ID>.webp 에 쓴 뒤
지금 설치된 그림과 픽셀이 같은지(같은 길로 다시 만들어지는지) 알린다.
"""
import io, json, os, shutil, subprocess, sys
import numpy as np
from PIL import Image

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
rp = os.path.abspath(sys.argv[1]); WRITE = '--write' in sys.argv
R = json.load(open(rp, encoding='utf-8')); here = os.path.dirname(rp); lid = R['lesson']
tmp = f'/tmp/zbuild/{lid}'; shutil.rmtree(tmp, ignore_errors=True); os.makedirs(f'{tmp}/z')
raw = subprocess.run(['git', 'show', f"{R['base']}:lesson/img/{lid}.webp"], cwd=ROOT, capture_output=True, check=True).stdout
cur = f'{tmp}/s0.png'; Image.open(io.BytesIO(raw)).convert('RGB').save(cur)
Z = os.path.join(ROOT, 'tools/prompts/zone3.py')
for i, st in enumerate(R['steps'], 1):
    nxt = f'{tmp}/s{i}.png'
    if 'zone' in st:
        n = st['zone']; x0, y0, x1, y1 = st['crop']
        subprocess.run(['python3', Z, 'crop', cur, f'{tmp}/z', n, str(x0), str(y0), str(x1), str(y1)], check=True, stdout=subprocess.DEVNULL)
        gem = f'{tmp}/z/gem_{n}.png'; Image.open(os.path.join(here, st['gem'])).convert('RGB').save(gem)
        cmd = ['python3', Z, 'paste', cur, f'{tmp}/z', n, gem, nxt, st['allow'], str(st.get('thr', 28))] + st.get('opts', [])
        out = subprocess.run(cmd, check=True, capture_output=True, text=True).stdout.strip()
        print(f'  {i}. zone {n} {st["crop"]} ← {st["gem"]} · {out[-120:]}')
    elif 'pil' in st:
        subprocess.run(['python3', os.path.join(here, st['pil']), cur, nxt] + [str(a) for a in st.get('args', [])], check=True)
        print(f'  {i}. pil {st["pil"]}')
    cur = nxt
dst = os.path.join(ROOT, f'lesson/img/{lid}.webp') if WRITE else f'/tmp/zbuild/{lid}.webp'
Image.open(cur).convert('RGB').save(dst, 'WEBP', quality=85, method=6)
inst = np.array(Image.open(os.path.join(ROOT, f'lesson/img/{lid}.webp')).convert('RGB'))
made = np.array(Image.open(dst).convert('RGB'))
print(lid, '→', dst, f'{os.path.getsize(dst) // 1024} KB', '· 설치된 그림과', '같은 픽셀' if np.array_equal(inst, made) else '다름')
