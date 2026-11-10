#!/usr/bin/env python3
# apply_patch.py — 감사 고침을 과 원본(lessons/<ID>.json)과 카드(index.html · srs_v8.html)에 적용한다.
# 사용: python3 tools/audit/apply_patch.py <patch.json> [--check]
#  patch.json = {"ops":[{lesson,stop,field,old,new,from?,note?}], "cards":[{card,field(q|a),old,new,from?}]}
#   stop = -1 이면 과 단위 칸(title · sub). old 는 그 칸 안에 정확히 한 번 나와야 한다.
# 파일 꼴을 건드리지 않으려고 칸의 JSON 문자열만 글자 그대로 갈아 끼운다. 하나라도 어긋나면 아무것도 쓰지 않는다.
import json, sys, os, re, collections
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..')
P = json.load(open(sys.argv[1], encoding='utf-8')); CHECK = '--check' in sys.argv
enc = lambda s: json.dumps(s, ensure_ascii=False)
errs = []; notes = []; out = {}; n_ops = 0
by = collections.OrderedDict()
for op in P.get('ops', []): by.setdefault(op['lesson'], []).append(op)
for les, ops in by.items():
    path = os.path.join(ROOT, 'lessons', les + '.json'); text = open(path, encoding='utf-8').read(); d = json.loads(text)
    cur = {}  # (stop, field) -> 현재 값
    orig = {}
    for op in ops:
        k, f = op['stop'], op['field']
        if (k, f) not in cur:
            v = d[f] if k < 0 else d['stops'][k][f]; cur[(k, f)] = v; orig[(k, f)] = v
        v = cur[(k, f)]
        if v.count(op['old']) != 1: errs.append(f"{les}#{k}.{f}: old 가 {v.count(op['old'])}번 — 「{op['old'][:40]}」"); continue
        cur[(k, f)] = v.replace(op['old'], op['new']); n_ops += 1
    for (k, f), v in cur.items():
        if v == orig[(k, f)]: continue
        if f == 'fact' and len(v) > 60: errs.append(f"{les}#{k}.fact {len(v)}자 (> 60): {v}")
        a, b = enc(orig[(k, f)]), enc(v)
        if text.count(a) != 1: errs.append(f"{les}#{k}.{f}: 파일에 원문이 {text.count(a)}번"); continue
        text = text.replace(a, b)
    try:
        d2 = json.loads(text)
        for (k, f), v in cur.items():
            got = d2[f] if k < 0 else d2['stops'][k][f]
            if got != v: errs.append(f"{les}#{k}.{f}: 적용 뒤 값이 다르다")
    except Exception as e: errs.append(f"{les}: JSON 깨짐 {e}")
    out[path] = text
cards = P.get('cards', [])
for fn in ('index.html', 'srs_v8.html'):
    path = os.path.join(ROOT, fn)
    if not os.path.exists(path): continue
    text = open(path, encoding='utf-8').read()
    for c in cards:
        m = re.search(r'\{"id":' + re.escape(enc(c['card'])) + r',"q":("(?:[^"\\]|\\.)*"),"a":("(?:[^"\\]|\\.)*")', text)
        if not m:
            (errs if fn == 'index.html' else notes).append(f"{fn}: 카드 {c['card']} 못 찾음"); continue
        g = 1 if c['field'] == 'q' else 2
        if json.loads(m.group(g)) != c['old']: errs.append(f"{fn}: 카드 {c['card']}.{c['field']} 원문이 다르다 — 지금 「{json.loads(m.group(g))[:50]}」"); continue
        s, e = m.span(g); text = text[:s] + enc(c['new']) + text[e:]
    out[path] = text
print(f"과 {len(by)} · 고침 {n_ops}/{len(P.get('ops', []))} · 카드 고침 {len(cards)}")
for n in notes: print('· ' + n)
if errs:
    print('\n'.join('✕ ' + e for e in errs)); sys.exit(1)
if CHECK: print('검사만 — 쓰지 않음'); sys.exit(0)
for path, text in out.items(): open(path, 'w', encoding='utf-8').write(text)
print('적용함:', len(out), '파일')
