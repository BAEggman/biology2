#!/usr/bin/env python3
# reserve_A11.py — 11장 덧붙임(L45a s12 · 2026-11-16 · Opus 5.5)의 예약.
import json
P = '/tmp/b2/tools/hooks.json'
txt = open(P, encoding='utf-8').read(); d = json.loads(txt)
assert json.dumps(d, ensure_ascii=False, indent=1) == txt
R = d['_심볼예약']
B = '[2026-11-16 11장 덧붙임]'
new = {
 '하늘에서 곧게 내려온 햇살 기둥이 비추는 잎 모자 여자의 무릎 위 열린 도시락(샌드위치 · 물뿌리개를 기울임) + 곁에서 빈 접시를 든 채 그 도시락의 샌드위치를 집는 빨간 셔츠 남자':
   f'독립영양(CO₂ · 무기물로 제 유기물 — 빛으로 하면 광독립영양 · 대부분의 식물) ↔ 종속영양(남이 만든 유기물을 먹음) 전용 {B} — L45a s12. ⚠ 풀밭만 오려 그리면 햇살이 구역 윗변에서 끊겨 「잎 널에서 빛이 나온다」로 읽힌다(L1 · 일치 검사 1회) — 하늘까지 세로로 오린 구역(M1)에서.',
}
for k, v in new.items():
    assert k not in R, k
    R[k] = v
out = json.dumps(d, ensure_ascii=False, indent=1)
assert json.loads(out) == d
open(P, 'w', encoding='utf-8').write(out)
print('예약', len(R))
