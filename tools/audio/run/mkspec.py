#!/usr/bin/env python3
# mkspec.py <decisions.json> <batch 이름> <청취표 경로> [rejected.json] — 판정 기록으로 공개 목록(ids) · 묶음 spec 초안 · 청취표를 만든다.
#   판정: CLEAR · CLEAR_ALLOWED_VARIANT 만 싣는다(REDO · HOLD 는 빼고 rejected 로). id 는 「L_sid_vN」(가장 높은 판).
import json, sys, re, os
D = json.load(open(sys.argv[1])); batch = sys.argv[2]; sheet = sys.argv[3]
rej = json.load(open(sys.argv[4])) if len(sys.argv) > 4 else []
best = {}
for k, v in D.items():
    m = re.match(r'(L\w+?_s\d+)_v(\d+)$', k); b, n = m.group(1), int(m.group(2))
    if b not in best or n > best[b][0]: best[b] = (n, v)
acc = []; hold = []
for b, (n, v) in sorted(best.items()):
    i = f'{b}_v{n}'
    if v['status'] in ('CLEAR', 'CLEAR_ALLOWED_VARIANT'):
        r = '원문과 같음' if v['status'] == 'CLEAR' else '경미한 차이 허용'
        acc.append({'id': i, 'review': f"{v['review']} 받아 적기 — {r}" + (f" · {v.get('notes') or v.get('note')}" if (v.get('notes') or v.get('note')) else '')})
    else: hold.append((i, v))
spec = {'batch': batch, 'date': '2026-11-21',
        'by': 'Claude Opus 5.5 — Gemini 작업 모드(Kore) 녹음 · 따로 연 Gemini 작업 대화의 받아 적기(원문 없음) · 다른 곳만 필청 A/B · 사람은 듣지 않음',
        'hashes': 'tools/audio/batches/hashes_20261121.txt', 'accepted': acc,
        'rejected_attempts': rej + [{'id': i, 'reason': f"{v['status']} — {(v.get('notes') or v.get('note',''))}"} for i, v in hold], 'extra': {}}
json.dump(spec, open(f'/tmp/work/{batch}.json', 'w'), ensure_ascii=False, indent=1)
json.dump([a['id'] for a in acc], open(f'/tmp/work/{batch}_ids.json', 'w'))
pri = [a for a in acc if '청취 때 확인' in a['review'] or not a['id'].endswith('_v1')]
rest = [a for a in acc if a not in pri]
L = [f'# 청취표 — {batch} ({len(acc)} 구간)', '', '위쪽은 다시 만든 판과 「청취 때 확인할 곳」. 들어 보고 「괜찮음 / 다시」만 알려 주세요.', '',
     '| # | 구간 | 녹음 | AI 표시 |', '|---|---|---|---|']
for n, a in enumerate(pri + rest, 1):
    Lx, s, v = a['id'].split('_')
    L.append(f"| {n} | {Lx} {s} ({v}) | [듣기](https://baeggman.github.io/biology2-audio/{a['id']}.mp3) | {a['review'].split(' — ',1)[-1]} |")
open(sheet, 'w').write('\n'.join(L) + '\n')
print(len(acc), 'accepted ·', len(hold), 'held/redo')
