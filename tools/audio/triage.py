#!/usr/bin/env python3
# triage.py <판 폴더> <답 열쇠 폴더> L... — 독자 ㄱ·ㄴ·ㄷ 결과 + 감사 대장 + 그림 잠금(grp)을 읽어 구간마다 ①~④ 를 「넘음 / 볼 것 / 안 됨」으로 가른다.
# 분류일 뿐 판정이 아니다 — 잠금은 사람이(⑤ 글 · 과학 읽기 포함) 정한다. 표는 stdout(마크다운).
#   안 됨: ① 대장에 그 과의 열린 항목 · ③ ㄴ 이 답 낱말을 「없음/모름」 · ④ ㄱ ✕ · ㄷ 어긋남
#   볼 것: ㄷ ✕ · 끊김 · 의심 · ㄴ 이 다른 정거장을 댐 · ㄱ △
import json, re, sys, os
R = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
eye, keys, Ls = sys.argv[1], sys.argv[2], sys.argv[3:]
iss = json.load(open(f'{R}/tools/audit/2026-11-20/issues.json'))
def rows(p):
    for line in open(p, encoding='utf-8'):
        if line.startswith('|'):
            c = [x.strip() for x in line.strip().strip('|').split('|')]
            if len(c) >= 3 and re.match(r'^s\d+', c[0]): yield re.match(r's\d+', c[0]).group(), c
for L in Ls:
    d = json.load(open(f'{R}/lessons/{L}.json')); sids = [s['sid'] for s in d['stops']]
    no = {s: [] for s in sids}; see = {s: [] for s in sids}
    op = [i['id'] for i in iss if i['lesson'] == L and i['state'] in ('reproduced', 'changed')]
    for s in sids:
        if op: no[s].append('① 열린 항목 ' + ' '.join(op))
    for s, c in rows(f'{eye}/{L}/ㄱ_결과.md'):
        if s in no and '✕' in c[2]: no[s].append(f'ㄱ ✕ {c[1]}')
        elif s in no and '△' in c[2]: see[s].append(f'ㄱ △ {c[1]}')
    for s, c in rows(f'{eye}/{L}/ㄷ_결과.md'):
        if s not in no: continue
        if '어긋남' in c[2]: no[s].append(f'ㄷ 어긋남 {c[1]}')
        for w in ('✕', '끊김', '의심'):
            if w in c[2]: see[s].append(f'ㄷ {w} {c[1]}')
    key = json.load(open(f'{keys}/{L}.key.json')); n = {}
    for line in open(f'{eye}/{L}/ㄴ_결과.md', encoding='utf-8'):
        c = [x.strip() for x in line.strip().strip('|').split('|')]
        if len(c) >= 4 and c[0] and c[0] != '용어': n[c[0]] = c
    for t, v in key['real'].items():
        c = n.get(t); s = v['sid']
        if c is None or s not in no: continue
        if '없음' in c[1] or '모름' in c[3]: no[s].append(f'ㄴ 못 꺼냄 {t}')
        elif s not in re.findall(r's\d+', c[1]): see[s].append(f'ㄴ 다른 정거장 {t}→{c[1]}')
    print(f'### {L}\n\n| 구간 | 분류 | 까닭 |\n|---|---|---|')
    for s in sids:
        k = '안 됨' if no[s] else ('볼 것' if see[s] else '넘음')
        print(f"| {s} | {k} | {' / '.join(no[s] + see[s])[:300] or '—'} |")
    print()
