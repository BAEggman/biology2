#!/usr/bin/env python3
# setrow.py <JSON파일> — 6+1 심판 결과를 이름 장부의 손 칸(가름.json)과 유지 — 붐빔 통(hooks.json 「_유지붐빔」)에 옮긴다. 그 뒤 mkledger.py --write 로 장부를 다시 만든다.
# JSON: {"rows": {"L16a|낱말": {갈래, 처방, 근거, 일감, 상태}}, "붐빔": {"L16a PKA": {까닭, 일감, 날짜}}}
import json, os, sys, subprocess
A = os.path.dirname(os.path.abspath(__file__)); R = os.path.abspath(os.path.join(A, '..', '..', '..'))
d = json.load(open(sys.argv[1], encoding='utf-8'))
gp = f'{A}/가름.json'; g = json.load(open(gp, encoding='utf-8'))
for k, v in d.get('rows', {}).items():
    g.setdefault(k, {}).update(v)
json.dump(g, open(gp, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
if d.get('붐빔'):
    hp = f'{R}/tools/hooks.json'; raw = open(hp, encoding='utf-8').read(); h = json.loads(raw)
    h['_유지붐빔']['목록'].update(d['붐빔'])
    indent = 1 if raw.startswith('{\n "') else 2
    json.dump(h, open(hp, 'w', encoding='utf-8'), ensure_ascii=False, indent=indent)
subprocess.run(['python3', f'{A}/mkledger.py', '--write'], check=True)
