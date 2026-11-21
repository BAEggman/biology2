#!/usr/bin/env python3
# reserved.py <낱말…> — 그 낱말(물건 · 소리)이 이미 임자가 있는지(11-19 지시서 §5 · cue/README §2).
#   tools/hooks.json 의 _심볼예약(열쇠 · 뜻)과 hooks[이름].props · 왜 에서 찾고, tools/cue/canon.json 의 정본 규칙도 본다.
import json, os, signal, sys, unicodedata
signal.signal(signal.SIGPIPE, signal.SIG_DFL)
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
N = lambda s: unicodedata.normalize('NFC', s or '')
H = json.load(open(os.path.join(ROOT, 'tools/hooks.json'), encoding='utf-8'))
C = json.load(open(os.path.join(ROOT, 'tools/cue/canon.json'), encoding='utf-8'))
if len(sys.argv) < 2: print(__doc__ if __doc__ else '쓰임: reserved.py 낱말 …'); sys.exit(1)
for w in map(N, sys.argv[1:]):
    print(f'■ {w}')
    n = 0
    for k, v in H.get('_심볼예약', {}).items():
        if w in N(k) or w in N(str(v)): print(f'  [예약] {k} — {str(v)[:220]}'); n += 1
    for name, h in H.get('hooks', {}).items():
        props = ' · '.join(map(str, h.get('props', [])))
        if w in N(name) or w in N(props): print(f"  [고리] {name}: {props}  ({h.get('형태','')} · {str(h.get('왜',''))[:80]})"); n += 1
    for r in C.get('규칙', []):
        if w in N(json.dumps(r, ensure_ascii=False)): print(f"  [정본] {r['개념']} = {' / '.join(r['있어야'])}  예외 {r.get('예외', {})}"); n += 1
    if not n: print('  (임자 없음)')
