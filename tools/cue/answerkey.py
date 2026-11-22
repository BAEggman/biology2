#!/usr/bin/env python3
# answerkey.py — 독자 ㄴ 의 답 열쇠(어느 낱말이 진짜 · 어느 정거장)를 만드는 한곳(2026-11-22 · Opus 5.5 · 지시서_Opus_이름고리 §2 ㉮).
#   mkreaders.py(판을 만들 때) · names/relock.py(이름 2 — 고친 열쇠로 규칙 ③ 을 다시 태울 때) · test/verify_answerkey.js 가 같이 쓴다.
#   python3 tools/cue/answerkey.py <과>…  → {과: real}   ·   --all → 모든 과
#
#   답 낱말 = lesson_names.js 가 그 과에서 뽑은 이름(카드 답의 음차 · 약어) + fact 머리말(「X — …」 의 X · 「—」 가 없으면 fact 의 짧은 낱말).
#   군더더기를 뺀다(채점표 §3 의 1 · 2 와 연장 흠만 — 본 세션 혼자 넓히지 않는다):
#     · 괄호 짝이 안 맞는 조각 · 화살표 · 「/」 · 한 글자 · 수(1.5ATP · 600만 · C16 — 수는 독자 ㄷ 이 본다)
#     · JUNK(누구나 아는 총칭) · hooks.json 「_이름장부면제」 목록(낱말마다 까닭)
#     · 같은 과의 다른 줄과 표기만 다른 것(IP3 ↔ IP₃ · 산화질소(NO) ↔ NO) · 「…들」 복수
import json, os, re, subprocess, sys
R = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
JUNK = {'생산', '바이러스', '세균', '세포', '단백질', '효소', '호르몬', '물', '빛'}
SUB = str.maketrans('₀₁₂₃₄₅₆₇₈₉⁺⁻', '0123456789+-')
norm = lambda t: t.translate(SUB)
_rows = None


def exempt():
    H = json.load(open(f'{R}/tools/hooks.json', encoding='utf-8'))
    return set((H.get('_이름장부면제') or {}).get('목록', {}))


def name_rows():
    global _rows
    if _rows is None:
        _rows = json.loads(subprocess.check_output(['node', f'{R}/tools/audit/2026-11-19/lesson_names.js', '--json'], cwd=R))
    return _rows


def clean(t, EX=None):
    EX = exempt() if EX is None else EX
    if len(t) < 2 or t in JUNK or t in EX: return False
    if t.count('(') != t.count(')') or re.search(r'[↑↓→←/]', t): return False
    if re.fullmatch(r'[\d.,]+\s*(만|억|ATP|년)?|[\d.,]+[A-Za-z]+|C\d+', norm(t)): return False
    if t.endswith('들') and t[:-1] in JUNK | EX: return False
    return True


def make_key(lid, d=None, rows=None, EX=None):
    d = d or json.load(open(f'{R}/lessons/{lid}.json', encoding='utf-8'))
    rows = name_rows() if rows is None else rows
    EX = exempt() if EX is None else EX
    real = {}
    for r in rows:
        if r['lesson'] == lid: real.setdefault(r['term'], {'sid': r['sid'], 'cls': r['cls'], 'props': r['props']})
    for s in d['stops']:
        h = s['fact'].split(' — ')[0].strip()   # 「—」 가 없으면 fact 전체의 짧은 낱말(목록) — 바이러스 이름처럼 꼭 필요한 것이 여기서 온다
        for part in re.split(r'\s*[·,]\s*', h):
            if 2 <= len(part) <= 12 and part not in real and not re.search(r'\s', part): real[part] = {'sid': s['sid'], 'cls': 'fact', 'props': None}
    def home(t):
        for f in ('hook', 'fact', 'obj', 'say'):
            for s in d['stops']:
                if t in (s.get(f) or ''): return s['sid']
        return None
    for t in list(real):
        if not clean(t, EX): real.pop(t); continue
        h = home(t)
        if h and h != real[t]['sid']: real[t]['sid_card'] = real[t]['sid']; real[t]['sid'] = h
    # 표기만 다른 것: 첨자를 편 꼴이 같으면 하나만(글에 나오는 쪽을 남김) · 「X(Y)」 는 X 나 Y 가 이미 있으면 뺌
    seen = {}
    for t in list(real):
        n = norm(t)
        if n in seen:
            score = lambda x: (bool(home(x)), x != norm(x))      # 글에 나오는 쪽 · 첨자를 쓴 쪽(IP₃)을 남김
            keep, drop = (t, seen[n]) if score(t) > score(seen[n]) else (seen[n], t)
            real.pop(drop, None); seen[n] = keep
        else: seen[n] = t
    for t in list(real):
        m = re.fullmatch(r'(.+?)\((.+)\)', t)
        if m and (m.group(1) in real or m.group(2) in real): real.pop(t)
    return real


if __name__ == '__main__':
    Ls = sorted(f[:-5] for f in os.listdir(f'{R}/lessons') if re.match(r'L\d\d[a-z]\.json$', f)) if '--all' in sys.argv else [a for a in sys.argv[1:] if a.startswith('L')]
    print(json.dumps({L: make_key(L) for L in Ls}, ensure_ascii=False))
