#!/usr/bin/env python3
# apply_A25_L43e.py — 25장 「지층 절벽의 계단」 가운데 Hox · Ubx 두 장(K1-37 · X-EV-29)을 L43e s1 에 「카드만」(2026-11-15 · Opus 5.5).
#   왜: L43e s1 의 상자 초파리는 「분홍 배 상자에는 아무것도 달리지 않았다」 — 배에서 다리 형성이 억제된 꼴이 이미 그려졌다.
#       같은 사실을 절벽 그림에 또 그리지 않는다(인계서 배운 것 (59) · L54_세계_설계.md).
#   say 에 한 문장 — Ubx · 다리 형성 억제 · 갑각류형 조상 → 6다리 곤충(기본서 캠벨 25장 §12).
# 사용: python3 apply_A25_L43e.py [--write]  → 뒤이어 `python3 tools/kit/gen_sync.py L43e` (L43e 는 gen 파일이 있는 과)
import json, sys, re
ROOT = '/tmp/b2'; WRITE = '--write' in sys.argv
p = f'{ROOT}/lessons/L43e.json'; t = open(p, encoding='utf-8').read(); d = json.loads(t)
fmt = None
for ind in (1, 2):
    for nl in ('', '\n'):
        if json.dumps(d, ensure_ascii=False, indent=ind) + nl == t: fmt = (ind, nl)
if not fmt: raise SystemExit('✕ 파일 모양')
S = open(f'{ROOT}/index.html', encoding='utf-8').read()
CARDS = {c['id'] for c in json.loads(re.search(r'<script[^>]*id=["\']CARDS["\'][^>]*>([\s\S]*?)</script>', S).group(1))}
OLD = '줄여서 혹스, Hox 유전자라 부른다.'
NEW = OLD + ' 분홍 배 상자에 다리가 하나도 없는 것도 혹스 유전자의 일이다. 곤충의 배에서는 혹스 유전자의 하나인 Ubx 가 다리 형성을 억제한다. 마디마다 다리가 달린 갑각류형 조상에서 다리가 여섯뿐인 곤충, 6다리 곤충이 진화한 까닭이다.'
st = d['stops'][0]; assert st['sid'] == 's1'
for c in ('K1-37', 'X-EV-29'):
    assert c in CARDS, c
    assert c not in (st.get('cards') or []), c
assert st['say'].count(OLD) == 1
st['cards'] = list(st['cards']) + ['K1-37', 'X-EV-29']
st['say'] = st['say'].replace(OLD, NEW)
assert len(st['say']) <= 560, len(st['say'])
print('L43e s1', st['cards'], 'say', len(st['say']))
if WRITE:
    open(p, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=fmt[0]) + fmt[1]); print('written')
