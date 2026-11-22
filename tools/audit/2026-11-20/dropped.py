#!/usr/bin/env python3
# dropped.py [--write] — 떨어진 구간 목록(2026-11-22 덧붙임 지시 §4.2).
#   눈 검사를 한 과(눈검사/<L>/)에서 잠기지 않은 구간마다 까닭을 한 줄로 → 떨어진구간.md · 떨어진구간.json
#   까닭의 출처: ① 승급 쪽지(승급/<L>.md)의 「- sN: …」 줄 → 없으면 ② 눈검사 원문(ㄱ · ㄴ · ㄷ_결과.md · 답열쇠.json)을
#   tools/audio/stoprules.py 로 다시 가름(그림 고친 뒤의 눈 검사 그림N/ 만 있는 과는 마지막 그림N 의 ㄱ · ㄷ).
#   재판정 칸(㉠ 독자가 틀림 · ㉡ 글이 그림보다 많이 말함 · ㉢ 그림이 틀리거나 빠짐 · ㉣ 이름을 못 꺼냄)은 손으로 —
#   다시 만들 때 앞 파일의 재판정 칸을 그대로 옮긴다(지우지 않는다).
import json, os, re, sys, glob
A = os.path.dirname(os.path.abspath(__file__))
R = os.path.abspath(os.path.join(A, '..', '..', '..'))
sys.path.insert(0, f'{R}/tools/audio')
from stoprules import classify, load_issues, OPEN

iss = load_issues()
lk = json.load(open(f'{R}/tools/audio/locked.json', encoding='utf-8'))['잠김']
EYE = f'{A}/눈검사'
Ls = sorted(x for x in os.listdir(EYE) if os.path.isdir(f'{EYE}/{x}'))
prev = {}
if os.path.exists(f'{A}/떨어진구간.json'):
    for r in json.load(open(f'{A}/떨어진구간.json', encoding='utf-8'))['rows']:
        if r.get('re'): prev[(r['lesson'], r['sid'])] = r['re']
if os.path.exists(f'{A}/떨어진구간.md'):   # 사람은 md 의 재판정 칸을 고친다 — md 가 먼저
    for line in open(f'{A}/떨어진구간.md', encoding='utf-8'):
        c = [x.strip() for x in line.strip().strip('|').split('|')]
        if len(c) >= 6 and re.match(r'^L\d\d[a-z]$', c[0]) and re.match(r'^s\d+$', c[1]) and c[-1]:
            prev[(c[0], c[1])] = c[-1]

def kinds(t):
    k = []
    if re.search(r'열린 항목|^①|\b①', t): k.append('① 열린 항목')
    if re.search(r'②|기호 묶음', t): k.append('② 기호 묶음')
    if re.search(r'ㄱ\s*✕', t): k.append('ㄱ ✕')
    if '어긋남' in t and not re.search(r'어긋남\s*(없음|0)', t): k.append('ㄷ 어긋남')
    if re.search(r'못 꺼냄|③', t): k.append('ㄴ 못 꺼냄')
    if re.search(r'⑤', t): k.append('⑤ 글 · 과학')
    if '이름 인출을 안 함' in t: k.append('ㄴ 안 함')
    if '넘음(분류)' in t: k.append('넘음 · 보수적')
    if not k: k.append('볼 것')
    return k

def note_lines(L):
    p = f'{A}/승급/{L}.md'
    out = {}
    if not os.path.exists(p): return out
    for line in open(p, encoding='utf-8'):
        m = re.match(r'^-\s*((?:s\d+)(?:\s*[·,]\s*s\d+)*)\s*[:：]\s*(.+)', line.strip())
        if m:
            for s in re.findall(r's\d+', m.group(1)): out[s] = m.group(2).strip()
    return out

rows = []
for L in Ls:
    d = json.load(open(f'{R}/lessons/{L}.json', encoding='utf-8'))
    sids = [s['sid'] for s in d['stops']]
    locked = set((lk.get(L) or {}).get('구간', {}))
    notes = note_lines(L)
    e = f'{EYE}/{L}'
    if os.path.exists(f'{e}/ㄱ_결과.md') or os.path.exists(f'{e}/ㄷ_결과.md'):
        src_eye, key = e, (f'{e}/답열쇠.json' if os.path.exists(f'{e}/답열쇠.json') else None)
    else:
        pics = sorted(glob.glob(f'{e}/그림*'), key=lambda p: int(re.sub(r'\D', '', os.path.basename(p)) or 0))
        src_eye, key = (pics[-1] if pics else None), None
    res = classify(L, src_eye, key, issues=iss, lesson=d)
    for s in sids:
        if s in locked: continue
        k, no, see = res[s]
        if s in notes:
            why, src = notes[s], '쪽지'
        else:
            why = ' / '.join(no + see)
            if not key: why = (why + ' / ' if why else '') + 'ㄴ 이름 인출을 안 함(그림 고친 뒤 ㄱ · ㄷ 만 봄)'
            if not why: why = '넘음(분류) — 잠그지 않은 까닭이 쪽지에 구간별로 없음 · 보수적 잠금'
            src = '원문' + ('' if key else '(ㄴ 없음 · ' + (os.path.basename(src_eye) if src_eye else '독자 결과 없음') + ')')
        rows.append({'lesson': L, 'sid': s, 'kinds': kinds(why), 'why': why[:400], 'src': src, 'cls': k,
                     're': prev.get((L, s), '')})

from collections import Counter
kc = Counter(x for r in rows for x in r['kinds'])
rc = Counter((r['re'] or '')[:1] for r in rows if r['re'])
done = sum(1 for r in rows if r['re'])
md = ['# 떨어진 구간 — 눈 검사를 했는데 잠기지 않은 구간', '',
      '`python3 tools/audit/2026-11-20/dropped.py --write` 가 눈검사 폴더 · 잠금 목록(`tools/audio/locked.json`) · 승급 쪽지 · 대장에서 다시 만든다. 손으로 고치는 곳은 **재판정 칸뿐**(다시 만들어도 남는다).',
      '재판정: ㉠ 독자가 틀림 · ㉡ 글이 그림보다 많이 말함 · ㉢ 그림이 틀리거나 빠짐(대장 새 줄) · ㉣ 이름을 못 꺼냄 — 덧붙임 지시 §5(묶음 다의 일).', '',
      f"## 수\n- 눈 검사를 한 과 {len(Ls)} · 떨어진 구간 **{len(rows)}** · 재판정 끝 **{done}**" + (' (' + ' · '.join(f'{k} {v}' for k, v in sorted(rc.items())) + ')' if rc else ''),
      '- 까닭 갈래(한 구간에 여럿일 수 있음): ' + ' · '.join(f'{k} {v}' for k, v in kc.most_common()),
      f"- 까닭의 출처: 쪽지 {sum(r['src'] == '쪽지' for r in rows)} · 원문에서 다시 뽑음 {sum(r['src'] != '쪽지' for r in rows)}", '',
      '## 목록', '| 과 | 구간 | 갈래 | 까닭 | 출처 | 재판정 |', '|---|---|---|---|---|---|']
for r in rows:
    md.append(f"| {r['lesson']} | {r['sid']} | {' · '.join(r['kinds'])} | {r['why'].replace('|', '/')} | {r['src']} | {r['re']} |")
summary = {'lessons': len(Ls), 'dropped': len(rows), 'rejudged': done, 'by_re': dict(rc), 'by_kind': dict(kc)}
if '--write' in sys.argv:
    open(f'{A}/떨어진구간.md', 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    json.dump({'_뜻': '떨어진구간.md 의 기계용 사본 — re(재판정)만 손으로', 'summary': summary, 'rows': rows},
              open(f'{A}/떨어진구간.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(json.dumps(summary, ensure_ascii=False))
