#!/usr/bin/env python3
# lesson_sid.py — 과의 정거장마다 바뀌지 않는 ID(sid)를 준다. 시험 기록이 정거장 번호가 아니라 이 ID 에 붙는다
#   (2026-11-10 감사 · GPT T08: 정거장을 넣고 빼면 번호에 붙은 기록이 다른 사실로 옮겨 간다).
# 규칙: 처음 한 번은 순서대로 s1, s2 … · 그 뒤 새 정거장은 「그 과에서 쓴 가장 큰 번호 + 1」 · 한 번 준 ID 는 지우거나 다시 쓰지 않는다.
# 사용: python3 tools/lesson_sid.py [L31a …]   (인자 없으면 lessons/*.json 전부 · 이미 다 있으면 아무것도 안 바꾼다)
# 파일 꼴을 건드리지 않으려고 글자 그대로 끼워 넣는다: 정거장의 첫 키 "obj" 앞에 "sid".
import json, re, sys, os, glob
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
ids = sys.argv[1:] or sorted(os.path.basename(f)[:-5] for f in glob.glob(os.path.join(ROOT, 'lessons', 'L*.json')))
changed = 0
for i in ids:
    p = os.path.join(ROOT, 'lessons', i + '.json'); t = open(p, encoding='utf-8').read(); d = json.loads(t)
    have = [s.get('sid') for s in d['stops']]
    if all(have): 
        assert len(set(have)) == len(have), f'{i}: sid 가 겹친다'; continue
    mx = max([int(x[1:]) for x in have if x] or [0])
    ms = list(re.finditer(r'\{(\s*)("sid"\s*:\s*"[^"]*",\s*)?"obj"(\s*):(\s*)', t))
    assert len(ms) == len(d['stops']), f'{i}: 정거장 {len(d["stops"])}개인데 "obj" 로 시작하는 것이 {len(ms)}개'
    out = []; last = 0
    for k, m in enumerate(ms):
        if m.group(2): continue
        mx += 1; ws = m.group(1); sep = ':' + m.group(4)
        ins = '{' + ws + '"sid"' + sep + '"s' + str(mx) + '",' + (ws if ws else '')
        out.append(t[last:m.start()] + ins + '"obj"' + m.group(3) + ':' + m.group(4)); last = m.end()
    t2 = ''.join(out) + t[last:]
    d2 = json.loads(t2); s2 = [s.get('sid') for s in d2['stops']]
    assert all(s2) and len(set(s2)) == len(s2), f'{i}: 넣은 뒤 sid 가 비었거나 겹친다'
    for a, b in zip(d['stops'], d2['stops']):
        b2 = dict(b); b2.pop('sid'); a2 = dict(a); a2.pop('sid', None); assert a2 == b2, f'{i}: 내용이 달라졌다'
    open(p, 'w', encoding='utf-8').write(t2); changed += 1
print(f'과 {len(ids)} · sid 를 넣은 과 {changed}')
