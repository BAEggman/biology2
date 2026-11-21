#!/usr/bin/env python3
"""mkhold.py — 대장(tools/audit/2026-11-20/issues.json)에서 lesson/audio/hold.json 을 만든다(지시서 §1 의 hold · 보기 화면 명세 §1.9 의 2).

검수 보류 = 대장에서 아직 글을 고치지 못한 내용 오류가 걸린 구간:
  상태가 open · reproduced · proposed · blocked 이고(changed = 글은 고쳤고 그림만 남음 → 보류 아님)
  중요도가 critical 이거나, major 이면서 분류가 「과학·범위」.
재생기(lesson/narration-player.js)는 이 구간을 스스로 읽지 않고(3.5초 뒤 다음) 「검수 보류 — 내용 확인 중」을 보인다.
손으로 넘긴 정거장에서는 녹음 대신 기기 음성으로만 읽는다.

쓰는 법: python3 tools/audio/mkhold.py          (쓴다)
        python3 tools/audio/mkhold.py --check  (지금 파일이 대장과 같은지만 — 다르면 1)
"""
import json, os, sys
R = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LEDGER = os.path.join(R, 'tools/audit/2026-11-20/issues.json')
OUT = os.path.join(R, 'lesson/audio/hold.json')
OPEN = {'open', 'reproduced', 'proposed', 'blocked'}

def build():
    X = [json.loads(l.rstrip().rstrip(',')) for l in open(LEDGER, encoding='utf-8') if l.startswith('{')]
    H = {}
    for x in X:
        if x.get('state') not in OPEN: continue
        if not (x.get('sev') == 'critical' or (x.get('sev') == 'major' and x.get('cat') == '과학·범위')): continue
        for sid in x.get('sids') or []:
            d = H.setdefault(x['lesson'], {})
            d[sid] = (d[sid] + ' · ' + x['id']) if sid in d else x['id']
    H = {k: dict(sorted(v.items(), key=lambda kv: int(kv[0][1:]))) for k, v in sorted(H.items())}
    head = {'_뜻': '검수 보류 구간 {과: {sid: 대장 항목 ID}} — tools/audio/mkhold.py 가 대장에서 만든다(손으로 고치지 않는다). 재생기는 이 구간을 스스로 읽지 않는다.'}
    return {**head, **H}

def dump(o): return json.dumps(o, ensure_ascii=False, indent=1) + '\n'

if __name__ == '__main__':
    new = dump(build())
    if '--check' in sys.argv:
        cur = open(OUT, encoding='utf-8').read() if os.path.exists(OUT) else ''
        if cur != new:
            print('✕ lesson/audio/hold.json 이 대장과 다르다 — python3 tools/audio/mkhold.py'); sys.exit(1)
        n = sum(len(v) for k, v in json.loads(new).items() if not k.startswith('_'))
        print(f'✓ hold.json 대장과 같음 — 보류 {n} 구간'); sys.exit(0)
    open(OUT, 'w', encoding='utf-8').write(new)
    print(new)
