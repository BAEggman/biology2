#!/usr/bin/env python3
"""git merge driver for index.html (biology2) — %O %A %B
- CARDS 줄(<script id="CARDS" …>): 카드 id · 필드 단위 3-way 병합
- BUILD 줄(<script>/*BUILD:START …): %A 를 둔다 — 뒤에 node build.js 가 다시 만든다
- 「새 Sketchy 과」 배지 줄(id="lessonBtn"): %A 를 둔다 — 뒤에 build_lesson.js 가 다시 센다
- 나머지 줄: git merge-file
결과를 %A 에 쓰고, 풀리지 않으면 1 로 끝난다(그 자리에서 손으로 푼다).
"""
import sys, json, re, subprocess, tempfile, os

O, A, B = sys.argv[1:4]
rd = lambda p: open(p, encoding='utf-8').read()
tO, tA, tB = rd(O), rd(A), rd(B)
SPECIAL = [('CARDS', lambda l: l.startswith('<script id="CARDS"')),
           ('BUILD', lambda l: l.startswith('<script>/*BUILD:START')),
           ('BADGE', lambda l: 'id="lessonBtn"' in l)]


def split(t):
    out, sp = [], {}
    for l in t.split('\n'):
        tag = next((n for n, f in SPECIAL if f(l)), None)
        if tag:
            if tag in sp:
                sys.exit(f'index.html 병합: {tag} 줄이 둘')
            sp[tag] = l
            out.append(f'@@@B2-SPECIAL-{tag}@@@')
        else:
            out.append(l)
    return '\n'.join(out), sp


rO, sO = split(tO); rA, sA = split(tA); rB, sB = split(tB)
with tempfile.TemporaryDirectory() as d:
    for n, t in (('A', rA), ('O', rO), ('B', rB)):
        open(os.path.join(d, n), 'w', encoding='utf-8').write(t)
    r = subprocess.run(['git', 'merge-file', '-p', '-L', 'HEAD', '-L', 'base', '-L', 'pick',
                        os.path.join(d, 'A'), os.path.join(d, 'O'), os.path.join(d, 'B')],
                       capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write('index.html 병합: 특수 줄 밖에서 글이 부딪친다\n')
        sys.exit(1)
    merged = r.stdout

RE = re.compile(r'(<script id="CARDS" type="application/json">)(.*)(</script>)$')


def cards(l):
    m = RE.match(l)
    arr = json.loads(m.group(2))
    assert json.dumps(arr, ensure_ascii=False, separators=(',', ':')) == m.group(2), 'CARDS 직렬화가 다르다'
    return m.group(1), arr, m.group(3)


pre, cO, post = cards(sO['CARDS']); _, cA, _ = cards(sA['CARDS']); _, cB, _ = cards(sB['CARDS'])
dO = {c['id']: c for c in cO}; dA = {c['id']: c for c in cA}; dB = {c['id']: c for c in cB}
conf = []


def merge_card(i, a, b, o):
    if a == b: return a
    if o is None: conf.append(i); return a
    if a == o: return b
    if b == o: return a
    res = {}
    for k in list(a) + [k for k in b if k not in a]:
        va, vb, vo = a.get(k, None), b.get(k, None), o.get(k, None)
        if va == vb: v = va
        elif va == vo: v = vb
        elif vb == vo: v = va
        else: conf.append(f'{i}.{k}'); v = va
        if v is not None: res[k] = v
    return res


res = []
for c in cA:
    i = c['id']
    if i in dO and i not in dB:          # pick 쪽에서 지움
        if c == dO[i]: continue
        conf.append(i + '(지움 · 고침)'); res.append(c); continue
    res.append(merge_card(i, c, dB[i], dO.get(i)) if i in dB else c)
ids = [c['id'] for c in res]
prev = None
for c in cB:                              # pick 쪽에서 새로 생긴 카드 — pick 의 앞 카드 뒤에
    i = c['id']
    if i not in dO and i not in dA:
        k = ids.index(prev) + 1 if prev in ids else len(res)
        res.insert(k, c); ids.insert(k, i)
    prev = i
if conf:
    sys.stderr.write('index.html 병합: 카드가 부딪친다 ' + ', '.join(conf) + '\n')
    sys.exit(1)
cards_line = pre + json.dumps(res, ensure_ascii=False, separators=(',', ':')) + post
for tag, line in (('CARDS', cards_line), ('BUILD', sA.get('BUILD')), ('BADGE', sA.get('BADGE'))):
    ph = f'@@@B2-SPECIAL-{tag}@@@'
    if line is None:
        if ph in merged: sys.exit(f'index.html 병합: {tag} 자리만 있고 줄이 없다')
        continue
    if merged.count(ph) != 1: sys.exit(f'index.html 병합: {tag} 자리 {merged.count(ph)}')
    merged = merged.replace(ph, line)
open(A, 'w', encoding='utf-8').write(merged)
sys.exit(0)
