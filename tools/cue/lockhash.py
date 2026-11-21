#!/usr/bin/env python3
# lockhash.py — 그림 · 글 잠금(tools/cue/lock.json)의 해시를 다시 낸다(2026-11-20 · 11-19 지시서 §4 「잠금은 두 가지」).
#   python3 tools/cue/lockhash.py            → 잠긴 과마다 JSON 한 줄: {id, 글, 그림, 공개그림차} (verify_lock.js 가 읽는다)
#   python3 tools/cue/lockhash.py --write L17e  → 지금 상태로 lock.json 의 글 · 그림 해시를 고쳐 쓴다(잠금을 풀거나 고칠 때만 · 까닭을 같이 고친다)
# 글  = 정거장마다 obj · fact · hook · say 를 \x1f 로 이어 \x1e 로 이은 것의 sha256
# 그림 = 무손실 원본(lock.json 의 「원본」 PNG)에서 「x 이상 전부」 + 「잠긴 정거장의 상자」 픽셀의 sha256
# 공개그림차 = 공개 그림(lesson/img/<ID>.webp)을 풀어 같은 구역을 원본과 견준 평균 절대 차(0 ~ 255) — 손실 압축이라 0 이 아닐 수 있음 · 문턱은 lock.json
import hashlib, json, os, sys
from PIL import Image
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOCK = os.path.join(ROOT, 'tools/cue/lock.json')
def boxes(b):
    if not b: return []
    return b if isinstance(b[0], list) else [b]
def mask_px(im, spec, stops):
    W, H = im.size; px = im.load(); sel = set()
    x0 = spec.get('x_from')
    if x0 is not None:
        for y in range(H):
            for x in range(x0, W): sel.add((x, y))
    for sid in spec.get('boxes', []):
        for (x, y, w, h) in boxes(stops[sid]['box']):
            for yy in range(max(0, y), min(H, y + h)):
                for xx in range(max(0, x), min(W, x + w)): sel.add((xx, yy))
    return sorted(sel)
def calc(lid, ent):
    d = json.load(open(os.path.join(ROOT, 'lessons', lid + '.json'), encoding='utf-8'))
    stops = {s['sid']: s for s in d['stops']}
    text = '\x1e'.join('\x1f'.join(s.get(k) or '' for k in ('obj', 'fact', 'hook', 'say')) for s in d['stops'])
    src = Image.open(os.path.join(ROOT, ent['원본'])).convert('RGB')
    pub = Image.open(os.path.join(ROOT, 'lesson', d['img'])).convert('RGB')
    sel = mask_px(src, ent['그림영역'], stops)
    a = src.load(); b = pub.load() if pub.size == src.size else None
    h = hashlib.sha256(); diff = 0
    for (x, y) in sel:
        p = a[x, y]; h.update(bytes(p))
        if b: q = b[x, y]; diff += abs(p[0]-q[0]) + abs(p[1]-q[1]) + abs(p[2]-q[2])
    return {'id': lid, '글': hashlib.sha256(text.encode('utf-8')).hexdigest(), '그림': h.hexdigest(),
            '공개그림차': round(diff / (3 * len(sel)), 3) if b else None, '크기같음': pub.size == src.size, '픽셀수': len(sel)}
L = json.load(open(LOCK, encoding='utf-8'))
if '--write' in sys.argv:
    lid = sys.argv[sys.argv.index('--write') + 1]; r = calc(lid, L[lid])
    L[lid]['글'] = r['글']; L[lid]['그림'] = r['그림']
    open(LOCK, 'w', encoding='utf-8').write(json.dumps(L, ensure_ascii=False, indent=1) + '\n'); print(json.dumps(r, ensure_ascii=False))
else:
    for lid, ent in L.items():
        if lid.startswith('_'): continue
        print(json.dumps(calc(lid, ent), ensure_ascii=False))
