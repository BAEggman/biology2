#!/usr/bin/env python3
"""git merge driver for test/baseline.json — %O %A %B
줄 단위 병합(git merge-file --diff3). 부딪친 곳이 세 쪽 모두 한 줄 `"키": {…},` 이고 키가 같으면
그 사전을 키 단위로 3-way 병합한다(예: "cardEdits" — 두 쪽이 저마다 카드 고침을 적은 경우). 그 밖은 부딪침(1).
"""
import sys, json, re, subprocess

O, A, B = sys.argv[1:4]
r = subprocess.run(['git', 'merge-file', '-p', '--diff3', '-L', 'HEAD', '-L', 'base', '-L', 'pick', A, O, B],
                   capture_output=True, text=True)
if r.returncode == 0:
    open(A, 'w', encoding='utf-8').write(r.stdout); sys.exit(0)
LINE = re.compile(r'^(\s*)"([^"]+)": (\{.*\})(,?)$')
out, i, L = [], 0, r.stdout.split('\n')
while i < len(L):
    if not L[i].startswith('<<<<<<< HEAD'):
        out.append(L[i]); i += 1; continue
    j = L.index('||||||| base', i); k = L.index('=======', j); e = next(n for n in range(k, len(L)) if L[n].startswith('>>>>>>> pick'))
    a, o, b = L[i + 1:j], L[j + 1:k], L[k + 1:e]
    if not (len(a) == len(o) == len(b) == 1):
        sys.exit('baseline.json 병합: 여러 줄이 부딪친다')
    ma, mo, mb = (LINE.match(x[0]) for x in (a, o, b))
    if not (ma and mo and mb and ma.group(2) == mo.group(2) == mb.group(2)):
        sys.exit('baseline.json 병합: 한 줄 사전이 아니다')
    da, do, db = (json.loads(x.group(3)) for x in (ma, mo, mb))
    for x, d in ((ma, da), (mo, do), (mb, db)):
        if json.dumps(d, ensure_ascii=False) != x.group(3):
            sys.exit('baseline.json 병합: 사전 직렬화 꼴이 다르다')
    res = {}
    for key in list(da) + [q for q in db if q not in da]:
        va, vb, vo = da.get(key), db.get(key), do.get(key)
        if va == vb: v = va
        elif va == vo: v = vb
        elif vb == vo: v = va
        else: sys.exit(f'baseline.json 병합: {ma.group(2)}.{key} 가 두 쪽에서 다르게 바뀌었다')
        if v is not None: res[key] = v
    out.append(f'{ma.group(1)}"{ma.group(2)}": {json.dumps(res, ensure_ascii=False)}{ma.group(4)}')
    i = e + 1
open(A, 'w', encoding='utf-8').write('\n'.join(out))
sys.exit(0)
