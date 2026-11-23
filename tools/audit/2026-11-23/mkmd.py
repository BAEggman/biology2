#!/usr/bin/env python3
# mkmd.py — 덱감사.json → 덱감사.md(사람이 읽는 요약 · 과마다 줄). 손으로 고치지 않는다.
import json
from collections import Counter
A = '/tmp/b2/tools/audit/2026-11-23'
d = json.load(open(f'{A}/덱감사.json', encoding='utf-8'))
cell = lambda s, n=150: (str(s or '').replace('|', '／').replace('\n', ' ')[:n])
done = d['끝난 과']; rows = d['줄']
o = ['# 덱 감사 2026-11-23 — 요약(`덱감사.json` 에서 만듦 · `mkmd.py`)', '',
     f'- 끝난 과 **{len(done)} / 142** · 줄 {len(rows)}',
     '- 부호별: ' + ' · '.join(f'{k} {v}' for k, v in sorted(Counter(r["부호"] for r in rows).items(), key=lambda kv: (min(x["급"] for x in rows if x["부호"] == kv[0]), -kv[1]))),
     '- 처방별: ' + ' · '.join(f'{k} {v}' for k, v in Counter(r["처방"] for r in rows).most_common()),
     '- 급: 1 = C(반대로 가르침) · 2 = D1(도해판) · 3 = N · N′ · K · 4 = M · R · 5 = W · T · 6 = D2 · D3 · 7 = X · 8 = V (채점표 §8)', '',
     '## 과별 수', '', '| 과 | 줄 | C | D1 | N · N′ | K | M | R | 그 밖 | 카드(줄에 걸린 합) | 총평 |', '|---|---|---|---|---|---|---|---|---|---|---|']
for L in done:
    rs = [r for r in rows if r['과'] == L]; c = Counter(r['부호'] for r in rs)
    oth = len(rs) - c['C'] - c['D1'] - c['N'] - c['N′'] - c['K'] - c['M'] - c['R']
    o.append(f"| {L} | {len(rs)} | {c['C']} | {c['D1']} | {c['N'] + c['N′']} | {c['K']} | {c['M']} | {c['R']} | {oth} | {sum(r['카드'] for r in rs)} | {cell(d['과'][L].get('총평'), 120)} |")
o += ['', '## 줄(과 · 급 차례)', '']
for L in done:
    o += [f'### {L}', '', '| 구간 | 부호 | 급 | 근거 | 걸린 | 카드 | 처방 |', '|---|---|---|---|---|---|---|']
    for r in sorted([r for r in rows if r['과'] == L], key=lambda r: r['급']):
        o.append(f"| {r['구간']} | {r['부호']} | {r['급']} | {cell(r['근거'], 220)} | {cell(r.get('걸린'), 70)} | {r['카드']} | {r['처방']} |")
    m = d['과'][L]
    if m.get('버린 줄'): o.append('- 본 세션이 버린 대역 줄: ' + ' · '.join(f'{k}: {v}' for k, v in m['버린 줄'].items()))
    if m.get('메모'): o.append('- 본 세션: ' + m['메모'])
    o.append('')
open(f'{A}/덱감사.md', 'w', encoding='utf-8').write('\n'.join(o) + '\n')
print('덱감사.md', len(done), '과')
