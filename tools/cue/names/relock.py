#!/usr/bin/env python3
# relock.py [L…] [--ok L:s1,s2] [--no L:s3 --why L:s3=까닭] [--write] — 이름 2 · 3 의 다시 잠금(지시서_Opus_이름고리 §3 · 2026-11-22 · Opus 5.5).
#   떨어진 구간을 규칙(tools/audio/stoprules.py)에 다시 태운다. 답 열쇠 = 눈검사 원문의 답열쇠.json 에서
#     ㉮(장부 갈래 — 군더더기) 낱말과 · 다시 잰 독자 ㄴ 이 ○(맞는 정거장 + 설계한 고리 종류)로 꺼낸 낱말(names/다시재기/판정.json)을 뺀 것.
#     → 그 낱말 때문에만 「안 됨」 이던 구간이 넘음/볼 것이 된다. 독자 ㄱ · ㄷ 과 대장 ①② 는 그대로 본다.
#   「넘음」 은 잠금 후보 · 「볼 것」 은 손으로 본 뒤 --ok 로 준 것만 · ⑤(글 · 과학 읽기)에서 걸린 것은 --no.
#   --write: tools/audio/locked.json 의 그 과 잠금에 구간을 **덧붙인다**(앞 잠금 · 쪽지는 지우지 않음 — lock_stops.py 와 다름).
#     그림 blob 이 잠금과 다르면 덧붙이지 않는다(11-20 §16). 쪽지 승급/<L>.md 끝에 「이름 고리 다시 잠금」 칸을 붙인다.
#   이름 장부의 상태(가름.json)도 고친다: 그 구간의 ㉮ · ㉯ 줄 → 「잠김」.
import json, os, re, sys, glob, hashlib, subprocess, datetime
A = os.path.dirname(os.path.abspath(__file__))
R = os.path.abspath(os.path.join(A, '..', '..', '..'))
sys.path.insert(0, f'{R}/tools/audio'); sys.path.insert(0, f'{R}/tools/cue')
from stoprules import classify, load_lesson
from answerkey import clean   # 답 열쇠 연장과 같은 군더더기 잣대(test/verify_answerkey.js)
EYE = f'{R}/tools/audit/2026-11-20/눈검사'
args = sys.argv[1:]
def take(flag):
    out = []
    while flag in args:
        k = args.index(flag); out.append(args[k + 1]); del args[k:k + 2]
    return out
def lmap(vals):
    m = {}
    for v in vals:
        L, ss = v.split(':', 1); m.setdefault(L, set()).update(x for x in ss.split(',') if x)
    return m
OK, NO = lmap(take('--ok')), lmap(take('--no'))
WHY = dict(v.split('=', 1) for v in take('--why'))
WRITE = '--write' in args
if WRITE: args.remove('--write')
G = json.load(open(f'{A}/가름.json', encoding='utf-8'))
PASS = json.load(open(f'{A}/다시재기/판정.json', encoding='utf-8')) if os.path.exists(f'{A}/다시재기/판정.json') else {}
drop_rows = json.load(open(f'{R}/tools/audit/2026-11-20/떨어진구간.json', encoding='utf-8'))['rows']
LEDW = {}
for _k, _e in json.load(open(f'{A}/장부.json', encoding='utf-8')).items():
    if _e['출처'] == '못 꺼냄':
        for _s in _e['구간']: LEDW.setdefault((_e['과'], _s), []).append(_e['낱말'])
NAMEDROP = {(r['lesson'], r['sid']) for r in drop_rows if 'ㄴ 못 꺼냄' in r['kinds']}
Ls = args or sorted({r['lesson'] for r in drop_rows if 'ㄴ 못 꺼냄' in r['kinds']})
lk = json.load(open(f'{R}/tools/audio/locked.json', encoding='utf-8'))
sha = lambda t: hashlib.sha256(t.encode()).hexdigest()[:12]
today = os.environ.get('DATE') or datetime.date.today().isoformat()
head = subprocess.check_output(['git', '-C', R, 'rev-parse', '--short=8', 'HEAD']).decode().strip()


def eye_dir(L):
    ds = [f'{EYE}/{L}'] + sorted(glob.glob(f'{EYE}/{L}/그림*'), key=lambda p: int(re.sub(r'\D', '', os.path.basename(p)) or 0))
    ds = [d for d in ds if os.path.exists(f'{d}/ㄴ_결과.md') and os.path.exists(f'{d}/답열쇠.json')]
    return ds[-1] if ds else None


def gone(L, w):
    g = (G.get(f'{L}|{w}') or {}).get('갈래')
    return g == '㉮' or not clean(w) or PASS.get(f'{L}|{w}', {}).get('판정') == '○'


out = {}
for L in Ls:
    ed = eye_dir(L)
    if not ed: continue
    # ㄱ · ㄷ 는 그림 고친 뒤의 마지막 판(그림N)에 있으면 그것 — dropped.py 와 같은 원문
    key = json.load(open(f'{ed}/답열쇠.json', encoding='utf-8'))
    key2 = {**key, 'real': {t: v for t, v in key['real'].items() if not gone(L, t)}}
    before = classify(L, ed, key)
    after = classify(L, ed, key2)
    d = load_lesson(L); say = {s['sid']: s['say'] for s in d['stops']}
    locked = set((lk['잠김'].get(L) or {}).get('구간', {}))
    cand = {}
    for s, (k, no, see) in after.items():
        if s in locked or k == '안 됨': continue
        if before[s][0] != '안 됨' and (L, s) not in NAMEDROP: continue   # 규칙으론 볼 것이었는데 앞 세션이 손으로 「못 꺼냄」으로 떨군 구간도 본다
        left = [w for w in LEDW.get((L, s), []) if not gone(L, w)]
        if left: continue   # 장부의 못 꺼낸 낱말이 아직 남음(㉰ · ㉱ · ㉲) — 잠그지 않는다
        cand[s] = (k, see)
    out[L] = cand
    for s, (k, see) in cand.items():
        mark = '잠금' if (k == '넘음' or s in OK.get(L, ())) and s not in NO.get(L, ()) else ('⑤ 멈춤' if s in NO.get(L, ()) else '볼 것 — 손으로')
        print(f"{L} {s} {k} → {mark}" + (f" · {' / '.join(see)[:160]}" if see else ''))
    if not WRITE: continue
    new = [s for s, (k, see) in cand.items() if (k == '넘음' or s in OK.get(L, ())) and s not in NO.get(L, ())]
    stop = [s for s in NO.get(L, ()) if s in cand]
    if not new and not stop: continue
    blob = subprocess.check_output(['git', '-C', R, 'hash-object', f'lesson/img/{L}.webp']).decode().strip()
    ent = lk['잠김'].get(L)
    if not new:
        open(f'{R}/tools/audit/2026-11-20/승급/{L}.md', 'a', encoding='utf-8').write('\n'.join(['', f'## 이름 고리 다시 재기 — {today} · Opus 5.5 · 바탕 커밋 `{head}`'] + [f"- {s} 멈춤 ⑤ — {WHY.get(f'{L}:{s}', '')}" for s in stop]) + '\n')
        continue
    if ent and ent.get('그림') != blob:
        print(f'⚠ {L}: 잠금의 그림 blob 이 지금과 다르다 — 덧붙이지 않음'); continue
    if not ent:
        ent = lk['잠김'][L] = {'구간': {}, '그림': blob, '근거': f'tools/audit/2026-11-20/승급/{L}.md', '날짜': today}
    for s in new: ent['구간'][s] = sha(say[s])
    ent['구간'] = dict(sorted(ent['구간'].items(), key=lambda kv: int(kv[0][1:])))
    ent['근거'] += f' · {today} 이름 고리 다시 잠금({" ".join(new)} — tools/cue/names/장부.md)'
    ent['날짜'] = today
    words = {s: sorted(w for w in key['real'] if key['real'][w]['sid'] == s and gone(L, w)) for s in new}
    note = ['', f'## 이름 고리 다시 잠금 — {today} · Opus 5.5 · 바탕 커밋 `{head}`(tools/cue/names/relock.py)']
    for s in new:
        why = []
        for w in words[s]:
            g = (G.get(f'{L}|{w}') or {}).get('갈래')
            if g == '㉮' or not clean(w): why.append(f'{w}: ㉮ 군더더기 — 답 열쇠에서 뺌({(G.get(f"{L}|{w}") or {}).get("근거", "answerkey.clean")})')
            else: why.append(f"{w}: 다시 잰 독자 ㄴ ○ — {PASS[f'{L}|{w}'].get('근거', '')}")
        hand = (f" · 볼 것을 손으로 봄({' / '.join(cand[s][1])[:200]})" + (f" — {WHY[f'{L}:{s}']}" if f'{L}:{s}' in WHY else ' — 글이 그 물건을 「보자」고 하지 않거나 작은 흔들림(△)')) if cand[s][0] == '볼 것' else ''
        note.append(f'- {s} 잠금(say {sha(say[s])}) — ' + ' / '.join(why) + hand)
    for s in NO.get(L, ()):
        if s in cand: note.append(f"- {s} 멈춤 ⑤ — {WHY.get(f'{L}:{s}', '')}")
    note.append('- ①②④ · ⑤(본 세션이 이 구간의 글 · 과학을 다시 읽음)는 그대로 넘음.')
    open(f'{R}/tools/audit/2026-11-20/승급/{L}.md', 'a', encoding='utf-8').write('\n'.join(note) + '\n')
    for k2, v in G.items():
        l2, w2 = k2.split('|', 1)
        if l2 == L and v.get('갈래') in ('㉮', '㉯') and any(w2 in words[s] for s in new): v['상태'] = '잠김'
if WRITE:
    json.dump(lk, open(f'{R}/tools/audio/locked.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    json.dump(G, open(f'{A}/가름.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
else:
    print('(보기만 함 — ⑤ 를 마친 뒤 --write)')
