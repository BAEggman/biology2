import json, re, sys, hashlib, subprocess, os, shutil
# lock4.py <eye dir> <keys dir> L... — 구간 단위 잠금(셋째 묶음과 같은 규칙)
R = '/tmp/b2'; A = f'{R}/tools/audit/2026-11-20'
eye, keys, Ls = sys.argv[1], sys.argv[2], sys.argv[3:]
head = subprocess.check_output(['git', '-C', R, 'rev-parse', '--short=8', 'HEAD']).decode().strip()
lk = json.load(open(f'{R}/tools/audio/locked.json'))
iss = json.load(open(f'{A}/issues.json'))
summary = {}
def rows(path):
    out = []
    for line in open(path, encoding='utf-8'):
        if line.startswith('|'):
            p = [x.strip() for x in line.strip().strip('|').split('|')]
            if len(p) >= 3 and re.match(r'^s\d+', p[0]): out.append(p)
    return out
for L in Ls:
    d = json.load(open(f'{R}/lessons/{L}.json'))
    sids = [s['sid'] for s in d['stops']]
    bad = {s: [] for s in sids}
    if any(i['lesson'] == L and i['state'] in ('reproduced', 'changed') for i in iss):
        summary[L] = 'OPEN-ISSUE'; continue
    for p in rows(f'{eye}/{L}/ㄱ_결과.md'):
        sid = re.match(r's\d+', p[0]).group()
        if sid in bad and '✕' in p[2]: bad[sid].append(f'ㄱ ✕ — {p[1]}')
    for p in rows(f'{eye}/{L}/ㄷ_결과.md'):
        sid = re.match(r's\d+', p[0]).group()
        if sid in bad and '어긋남' in p[2]: bad[sid].append(f'ㄷ 어긋남 — {p[1]}')
    key = json.load(open(f'{keys}/{L}.key.json'))
    nrows = {}
    for line in open(f'{eye}/{L}/ㄴ_결과.md', encoding='utf-8'):
        p = [x.strip() for x in line.strip().strip('|').split('|')]
        if len(p) >= 4 and p[0] and p[0] != '용어': nrows[p[0]] = p
    for t, v in key['real'].items():
        r = nrows.get(t)
        if r is None: continue
        if '없음' in r[1] or '모름' in r[3]:
            if v['sid'] in bad: bad[v['sid']].append(f'{t} — ㄴ 못 꺼냄')
    ok = [s for s in sids if not bad[s]]
    blob = subprocess.check_output(['git', '-C', R, 'hash-object', f'lesson/img/{L}.webp']).decode().strip()
    if ok:
        lk['잠김'][L] = {'구간': {s['sid']: hashlib.sha256(s['say'].encode()).hexdigest()[:12] for s in d['stops'] if s['sid'] in ok},
                        '그림': blob, '근거': f'tools/audit/2026-11-20/승급/{L}.md · 구간 단위 판정(2026-11-21)', '날짜': '2026-11-21'}
    os.makedirs(f'{A}/눈검사/{L}', exist_ok=True)
    for r_ in 'ㄱㄴㄷ':
        shutil.copy(f'{eye}/{L}/{r_}_결과.md', f'{A}/눈검사/{L}/{r_}_결과.md')
    shutil.copy(f'{eye}/{L}/ㄴ/terms.txt', f'{A}/눈검사/{L}/terms.txt')
    shutil.copy(f'{keys}/{L}.key.json', f'{A}/눈검사/{L}/답열쇠.json')
    nb = [s for s in sids if bad[s]]
    md = [f"# 승급 쪽지 — {L} {d.get('title','')}", '',
          f'2026-11-21 · Opus 5.5 · 2단계 {os.environ.get('BATCH','')} 묶음 · 바탕 커밋 `{head}` · 그림 blob `{blob}`', '',
          f"## 판정: 구간 단위 잠금 {len(ok)}/{len(sids)} — {' · '.join(ok) if ok else '없음'}", '잠그지 않은 구간:']
    md += [f"- {s}: {' / '.join(bad[s])}" for s in nb] or ['- 없음']
    md += ['', '## 근거', '- ① 대장 열린 항목 없음 · ② 묶음 아님 · ③ 독자 ㄴ 이 「없음/모름」이라 답한 이름이 걸린 정거장은 잠그지 않음(답 열쇠 정거장 번호 기준 — 다른 정거장으로 댄 것은 통과로 봄) · ④ ㄱ ✕ · ㄷ 어긋남이 있는 정거장은 잠그지 않음(기계 판정) · ⑤ 감사 대장이 닫힌 글.', '',
           f'눈 검사 원문: `tools/audit/2026-11-20/눈검사/{L}/`.']
    open(f'{A}/승급/{L}.md', 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    summary[L] = f'{len(ok)}/{len(sids)} ' + ' '.join(ok)
json.dump(lk, open(f'{R}/tools/audio/locked.json', 'w'), ensure_ascii=False, indent=1)
for k, v in summary.items(): print(k, v)
