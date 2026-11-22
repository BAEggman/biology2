#!/usr/bin/env python3
# lock_stops.py <판 폴더> <답 열쇠 폴더> L... [--ok L:s1,s2] [--no L:s3] [--why L:s3=까닭] [--write]
#   구간 단위 잠금(locked.json `_규칙_구간단위`). 규칙 ①~④ 는 tools/audio/stoprules.py(triage.py 와 같은 것).
#   - 「넘음」 구간을 잠근다. 「볼 것」 은 손으로 본 뒤 --ok 로 준 것만. 「안 됨」 은 --ok 로도 잠그지 않는다(멈춤).
#   - --no 는 ⑤(본 세션이 글 · 과학을 읽음)에서 걸린 구간 — 잠그지 않고 --why 의 까닭을 쪽지에 적는다.
#   - --write 가 없으면 무엇을 잠글지 보이기만 한다. --write 는 ⑤ 를 마친 뒤에만.
#   - 이미 잠긴 구간은 글 해시 · 그림 blob 이 같을 때만 이어 둔다(다르면 빼고 알린다 — 11-20 §16).
#   - 쪽지 `승급/<L>.md` 에 잠그지 않은 구간마다 까닭(①~④ · 볼 것 · ⑤)을 적는다 → dropped.py 가 읽는다.
import json, re, sys, hashlib, subprocess, os, shutil, datetime
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))
from stoprules import classify, R, load_lesson
A = f'{R}/tools/audit/2026-11-20'

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
WHY = {}
for v in take('--why'):
    k, t = v.split('=', 1); WHY[k] = t
WRITE = '--write' in args
if WRITE: args.remove('--write')
eye, keys, Ls = args[0], args[1], args[2:]
head = subprocess.check_output(['git', '-C', R, 'rev-parse', '--short=8', 'HEAD']).decode().strip()
today = os.environ.get('DATE') or datetime.date.today().isoformat()
batch = os.environ.get('BATCH', '')
lk = json.load(open(f'{R}/tools/audio/locked.json', encoding='utf-8'))
sha = lambda t: hashlib.sha256(t.encode()).hexdigest()[:12]
summary = {}
for L in Ls:
    d = load_lesson(L); say = {s['sid']: s['say'] for s in d['stops']}
    res = classify(L, f'{eye}/{L}', f'{keys}/{L}.key.json')
    for s in OK.get(L, ()):
        if res[s][0] == '안 됨': sys.exit(f'{L} {s}: 「안 됨」 구간은 --ok 로 잠그지 않는다 — {res[s][1]}')
    blob = subprocess.check_output(['git', '-C', R, 'hash-object', f'lesson/img/{L}.webp']).decode().strip()
    old = lk['잠김'].get(L)
    keep = {}
    if old:
        if old.get('그림') != blob: print(f'⚠ {L}: 잠금의 그림 blob 이 지금과 다르다 — 예전 잠금은 이어 두지 않음(11-20 §16 대로 따로 판정)')
        else: keep = {s: h for s, h in old['구간'].items() if s in say and sha(say[s]) == h}
    new = [s for s, (k, _, _) in res.items() if (k == '넘음' or s in OK.get(L, ())) and s not in NO.get(L, ())]
    lockset = {**keep, **{s: sha(say[s]) for s in new}}
    sids = list(say)
    ok = [s for s in sids if s in lockset]
    summary[L] = f"{len(ok)}/{len(sids)} " + ' '.join(ok)
    if not WRITE: continue
    if ok:
        prev = old.get('근거', '') if old and keep else ''
        lk['잠김'][L] = {'구간': {s: lockset[s] for s in ok}, '그림': blob,
                        '근거': f'tools/audit/2026-11-20/승급/{L}.md · 구간 단위 판정({today}' + (f' · 묶음 {batch}' if batch else '') + ')',
                        '날짜': today}
    os.makedirs(f'{A}/눈검사/{L}', exist_ok=True)
    for r_ in 'ㄱㄴㄷ':
        if os.path.exists(f'{eye}/{L}/{r_}_결과.md'): shutil.copy(f'{eye}/{L}/{r_}_결과.md', f'{A}/눈검사/{L}/{r_}_결과.md')
    if os.path.exists(f'{eye}/{L}/ㄴ/terms.txt'): shutil.copy(f'{eye}/{L}/ㄴ/terms.txt', f'{A}/눈검사/{L}/terms.txt')
    shutil.copy(f'{keys}/{L}.key.json', f'{A}/눈검사/{L}/답열쇠.json')
    md = [f"# 승급 쪽지 — {L} {d.get('title', '')}", '',
          f"{today} · Opus 5.5 · 구간 단위 판정{(' · 묶음 ' + batch) if batch else ''} · 바탕 커밋 `{head}` · 그림 blob `{blob}`", '',
          f"## 판정: 구간 단위 잠금 {len(ok)}/{len(sids)} — {' · '.join(ok) if ok else '없음'}", '',
          '## 잠그지 않은 구간(구간별 까닭 — `dropped.py` 가 읽는다)']
    for s in sids:
        if s in ok: continue
        k, no, see = res[s]
        if s in NO.get(L, ()): why = '⑤ ' + WHY.get(f'{L}:{s}', '본 세션이 글 · 과학을 읽고 멈춤')
        elif k == '안 됨': why = ' / '.join(no)
        else: why = '볼 것(손 판정에서 잠그지 않음) — ' + ' / '.join(see) + (f" · {WHY[f'{L}:{s}']}" if f'{L}:{s}' in WHY else '')
        md.append(f'- {s}: {why}')
    if len(ok) == len(sids): md.append('- 없음')
    hand = [s for s in ok if res[s][0] == '볼 것']
    md += ['', '## 근거(`_규칙_구간단위` · 규칙은 `tools/audio/stoprules.py`)',
           '- ① 그 구간에 닿는 대장의 열린 항목 없음 · ② 기호 묶음 대기 아님 · ③ 독자 ㄴ 이 답 낱말을 「없음/모름」이라 한 정거장은 잠그지 않음 · ④ ㄱ ✕ · ㄷ 어긋남 0 · ⑤ 본 세션이 잠근 구간의 글 · 과학을 읽음.',
           f"- 「볼 것」 이었는데 손으로 보고 잠근 구간: {' · '.join(f'{s}({chr(47).join(res[s][2])[:120]})' for s in hand) or '없음'}" + (' — ' + ' · '.join(WHY[f'{L}:{s}'] for s in hand if f'{L}:{s}' in WHY) if any(f'{L}:{s}' in WHY for s in hand) else ''),
           f"- 이어 둔 앞 잠금: {' · '.join(sorted(keep, key=lambda x: int(x[1:]))) or '없음'}",
           '', 'say sha256(앞 12자): ' + ' · '.join(f'{s} {lockset[s]}' for s in ok), '',
           f'눈 검사 원문: `tools/audit/2026-11-20/눈검사/{L}/`(ㄱ · ㄴ · ㄷ 결과 · terms · 답 열쇠). 독자는 sonnet · 회마다 새로 부름 · 서로의 결과를 못 봄.']
    open(f'{A}/승급/{L}.md', 'w', encoding='utf-8').write('\n'.join(md) + '\n')
if WRITE:
    json.dump(lk, open(f'{R}/tools/audio/locked.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
for k, v in summary.items(): print(k, v)
if not WRITE: print('(보기만 함 — ⑤ 를 마친 뒤 --write)')
