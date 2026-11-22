#!/usr/bin/env python3
# stoprules.py — 구간 단위 잠금 규칙 ①~④ 를 한곳에서(2026-11-22 · Opus 5.5 · 덧붙임 지시 §4.1).
#   triage.py(분류표) · run/lock_stops.py(잠금) · audit/2026-11-20/dropped.py(떨어진 구간 목록)가 이 모듈을 같이 쓴다.
#
#   안 됨 ① 그 구간에 닿는(sids) 대장의 열린 항목(state = reproduced · changed · blocked)
#   안 됨 ② 그 과에 기호 묶음(grp — 「기본서대조」 표시는 빼고)이 걸린 열린 항목이 있으면 과 전체
#   안 됨 ③ 독자 ㄴ 이 답 낱말을 「없음/모름」(답 열쇠의 정거장)
#   안 됨 ④ 독자 ㄱ ✕ · 독자 ㄷ 어긋남
#   볼 것: 그림 범위(scope · 없으면 fix0)의 열린 항목이 닿는 구간의 상자(box)와 겹치는 다른 구간 — 「다시 그릴 구역」
#          · 아직 정해지지 않은 기호 묶음을 같이 쓰는 과(SHARED) — 그 기호가 나오는 구간인지 손으로
#          · ㄷ ✕ · 끊김 · 의심 · ㄴ 이 다른 정거장을 댐 · ㄱ △
#   넘음: 그 밖. 넘음도 ⑤(본 세션이 글 · 과학을 읽음)를 거쳐야 잠근다.
import json, os, re

R = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
OPEN = ('reproduced', 'changed', 'blocked')
NOT_GRP = {'기본서대조'}
# 11-20 지시서 §4.3 「염색체문법」 — 대장에 항목은 없지만 같은 기호를 쓰는 과
SHARED = {'염색체문법': ['L48a', 'L48b', 'L48f', 'L34b', 'L36b']}


def load_issues():
    return json.load(open(f'{R}/tools/audit/2026-11-20/issues.json', encoding='utf-8'))


def load_lesson(L):
    return json.load(open(f'{R}/lessons/{L}.json', encoding='utf-8'))


def is_pic(i):
    sc = (i.get('scope') or i.get('fix0') or '').strip()
    return '그림' in sc and not sc.startswith('글')


def _overlap(a, b):
    ax, ay, aw, ah = a; bx, by, bw, bh = b
    return ax < bx + bw and bx < ax + aw and ay < by + bh and by < ay + ah


def _rows(p):
    if not os.path.exists(p): return
    for line in open(p, encoding='utf-8'):
        if line.startswith('|'):
            c = [x.strip() for x in line.strip().strip('|').split('|')]
            if len(c) >= 3 and re.match(r'^s\d+', c[0]): yield re.match(r's\d+', c[0]).group(), c


def classify(L, eye=None, key=None, issues=None, lesson=None):
    """구간마다 (분류, 안 됨 까닭[], 볼 것 까닭[]).
    eye: 독자 결과가 든 폴더(ㄱ_결과.md · ㄴ_결과.md · ㄷ_결과.md) — 없으면 대장 규칙(①②)만.
    key: 답 열쇠 JSON 경로 또는 dict."""
    iss = load_issues() if issues is None else issues
    d = load_lesson(L) if lesson is None else lesson
    stops = d['stops']; sids = [s['sid'] for s in stops]
    def _boxes(b):
        if not b: return []
        return [b] if isinstance(b[0], (int, float)) else b
    box = {s['sid']: _boxes(s.get('box')) for s in stops}
    no = {s: [] for s in sids}; see = {s: [] for s in sids}
    op = [i for i in iss if i['lesson'] == L and i['state'] in OPEN]
    g = [i for i in op if i.get('grp') and i['grp'] not in NOT_GRP]
    if g:
        why = '② 기호 묶음 대기 ' + ' '.join(sorted({f"{i['grp']}({i['id']})" for i in g}))
        for s in sids: no[s].append(why)
    for i in op:
        for s in i.get('sids') or []:
            if s in no: no[s].append(f"① 열린 항목 {i['id']}")
        if is_pic(i):
            zone = [b for s in (i.get('sids') or []) for b in box.get(s, [])]
            for s in sids:
                if s in (i.get('sids') or []): continue
                if any(_overlap(a, b) for a in box[s] for b in zone):
                    see[s].append(f"다시 그릴 구역 {i['id']}")
    for grp, Ls in SHARED.items():
        if L in Ls and any(i.get('grp') == grp and i['state'] in OPEN for i in iss):
            for s in sids: see[s].append(f'기호 묶음 {grp} 을 같이 쓰는 과 — 그 기호가 나오는 구간은 잠그지 않음')
    if eye:
        for s, c in _rows(f'{eye}/ㄱ_결과.md'):
            if s in no and '✕' in c[2]: no[s].append(f'④ ㄱ ✕ {c[1]}')
            elif s in no and '△' in c[2]: see[s].append(f'ㄱ △ {c[1]}')
        for s, c in _rows(f'{eye}/ㄷ_결과.md'):
            if s not in no: continue
            if '어긋남' in c[2] and not re.search(r'어긋남\s*(없음|-|아님)', c[2]): no[s].append(f'④ ㄷ 어긋남 {c[1]}')
            for w in ('✕', '끊김', '의심'):
                if w in c[2] and not re.search(w + r'\s*(없음|아님)', c[2]) and '의도한' not in c[2]:
                    see[s].append(f'ㄷ {w} {c[1]}')
        kd = json.load(open(key, encoding='utf-8')) if isinstance(key, str) else key
        np_ = f'{eye}/ㄴ_결과.md'
        if kd and os.path.exists(np_):
            n = {}
            for line in open(np_, encoding='utf-8'):
                c = [x.strip() for x in line.strip().strip('|').split('|')]
                if len(c) >= 4 and c[0] and c[0] not in ('용어', '---'): n[c[0]] = c
            for t, v in kd['real'].items():
                c = n.get(t); s = v['sid']
                if c is None or s not in no: continue
                if '없음' in c[1] or '모름' in c[3]: no[s].append(f'③ ㄴ 못 꺼냄 {t}')
                elif s not in re.findall(r's\d+', c[1]): see[s].append(f'ㄴ 다른 정거장 {t}→{c[1]}')
    out = {}
    for s in sids:
        out[s] = ('안 됨' if no[s] else ('볼 것' if see[s] else '넘음'), no[s], see[s])
    return out
