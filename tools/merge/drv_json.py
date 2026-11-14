#!/usr/bin/env python3
"""git merge driver for tools/hooks.json (json.dumps indent=1 · ensure_ascii=False) — %O %A %B
키 단위 3-way 병합(사전은 깊이 들어감 · %A 의 키 차례 + %B 의 새 키는 %B 의 앞 키 뒤에).
같은 글을 두 쪽이 모두 고쳤을 때: 둘 다 옛 글 뒤에 덧붙였으면 옛 글 + %A 덧붙임 + %B 덧붙임, 아니면 부딪침(1).
목록: 한쪽만 바뀌었으면 그쪽 · 둘 다면 %A 차례 + %B 에만 새로 생긴 것.
"""
import sys, json

O, A, B = sys.argv[1:4]
rd = lambda p: open(p, encoding='utf-8').read()
tA = rd(A)
jO, jA, jB = json.loads(rd(O)), json.loads(tA), json.loads(rd(B))
fmt = lambda x: json.dumps(x, ensure_ascii=False, indent=1)
for t in (rd(O), tA, rd(B)):
    if fmt(json.loads(t)) != t.rstrip('\n'):
        sys.exit('hooks.json 병합: 직렬화 꼴이 indent=1 이 아니다')
conf = []
MISSING = object()


def m(a, b, o, path):
    if a == b: return a
    if o is MISSING:
        if isinstance(a, dict) and isinstance(b, dict): o = {}
        else: conf.append(path); return a
    if a == o: return b
    if b == o: return a
    if isinstance(a, dict) and isinstance(b, dict) and isinstance(o, dict):
        res = {}
        for k in a:
            vb = b.get(k, MISSING); vo = o.get(k, MISSING)
            if vb is MISSING:
                if vo is MISSING or vo == a[k]:
                    if vo is MISSING: res[k] = a[k]          # %A 에서 새로
                    continue                                  # %B 에서 지움(%A 는 그대로) → 지움
                conf.append(path + '/' + k + '(지움 · 고침)'); res[k] = a[k]; continue
            res[k] = m(a[k], vb, vo, path + '/' + k)
        prev = None
        for k in b:                                           # %B 에서 새로 — %B 의 앞 키 뒤에
            if k not in a and k not in o:
                items = list(res.items())
                pos = next((n + 1 for n, (kk, _) in enumerate(items) if kk == prev), len(items))
                items.insert(pos, (k, b[k])); res = dict(items)
            elif k not in a and k in o and b[k] != o[k]:
                conf.append(path + '/' + k + '(고침 · 지움)')
            prev = k
        return res
    if isinstance(a, str) and isinstance(b, str) and isinstance(o, str):
        if b.startswith(o):                                   # pick 은 덧붙이기만 — HEAD 의 고친 글 뒤에 그 덧붙임
            sys.stderr.write(f'hooks.json 병합: {path} — HEAD 글 + pick 덧붙임 {len(b) - len(o)}자\n')
            return a + b[len(o):]
        if a.startswith(o):                                   # HEAD 는 덧붙이기만 — pick 의 고친 글 뒤에 그 덧붙임
            sys.stderr.write(f'hooks.json 병합: {path} — pick 글 + HEAD 덧붙임 {len(a) - len(o)}자\n')
            return b + a[len(o):]
    if isinstance(a, list) and isinstance(b, list):
        return a + [x for x in b if x not in a and (not isinstance(o, list) or x not in o)]
    conf.append(path); return a


res = m(jA, jB, jO, '')
if conf:
    sys.stderr.write('hooks.json 병합: 부딪침 ' + ' | '.join(conf[:20]) + '\n')
    sys.exit(1)
open(A, 'w', encoding='utf-8').write(fmt(res) + ('\n' if tA.endswith('\n') else ''))
sys.exit(0)
