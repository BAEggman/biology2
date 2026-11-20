#!/usr/bin/env python3
# parse_handoff.py <인계문.md> [--write] [--full <밖의 경로.json>] — 2026-11-20 인계문 부록 A(그림–대본 전수 감사)를 읽어 작업 대장의 뼈대를 만들고, 지금 저장소와 다시 맞춰 본다(Fable 5.2 · 2026-11-20).
#   · 인계문과 감사 원문은 공개 저장소에 넣지 않는다(프로젝트 문서 `claude/인계문_2026-11-20_전문.md` · 사용자 컴퓨터 ~/Downloads/biology_claude_handoff_full_20261120.md).
#   · 그냥 돌리면 **세어 보기만** 한다(수 · 인용문이 지금 글에 있는지 · 그림 해시). 파일은 안 건드린다.
#   · --write: issues.json · lessons.json 을 고친다. **대장을 덮어쓰지 않는다** — 이미 있는 줄에서는 인계문에서 온 칸(sids · sev · kind · cat · quote · line)만 새로 고치고,
#     손으로 채운 칸(state · fix0 · grp · note0 · 그 밖에 Opus 가 더한 칸)과 인계문에 없는 줄(N-…)은 그대로 둔다.
#   · --full 을 주면 원문 칸(현재 표현 · 그림 관찰 · 판단 · 수정안 · 근거)까지 든 JSON 을 **저장소 밖**에 쓴다(작업용 — 커밋하지 않는다).
# 확인하는 수: 과 142(보류 86 · 조건부 56) · 항목 246(미해결 216 = 최우선 8 · 중요 121 · 경미 87 / 언어 복구로 해결 30).
import re, json, sys, glob, os, subprocess, collections
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
F = sys.argv[1]; full_out = sys.argv[sys.argv.index('--full') + 1] if '--full' in sys.argv else None
L = open(F, encoding='utf-8').read().split('\n')
a = next(i for i, l in enumerate(L) if l.startswith('## 8. 구간별 상세 근거'))
b = next(i for i, l in enumerate(L) if l.startswith('## 9. 이번에 실제 복구한'))
SEV = {'최우선': 'critical', '중요': 'major', '경미': 'minor', '공개본 언어 복구 완료': 'resolved_lang'}
lessons, issues, cur, iss = {}, [], None, None
for i in range(a, b):
    l = L[i]
    m = re.match(r'^### (L\d{2}[a-z]) — (.*)$', l)
    if m: cur = {'id': m.group(1), 'line': i + 1, 'verdict': None, 'sha': None, 'n': None, 'keep': '', 'issues': []}; lessons[cur['id']] = cur; iss = None; continue
    if cur is None: continue
    m = re.match(r'^\*\*(녹음 보류|조건부 통과)\*\* · (\d+)구간 대조 · .*이미지 SHA `([0-9a-f]+)`', l)
    if m: cur['verdict'] = 'hold' if m.group(1) == '녹음 보류' else 'cond'; cur['n'] = int(m.group(2)); cur['sha'] = m.group(3); continue
    if l.startswith('유지할 점:'): cur['keep'] = l[len('유지할 점:'):].strip(); continue
    m = re.match(r'^\*\*(L\d{2}[a-z]-\d+[a-z]?) · (.*?) · (최우선|중요|경미|공개본 언어 복구 완료)(.*?)\*\*', l)
    if m:
        iss = {'id': m.group(1), 'lesson': cur['id'], 'sid_raw': m.group(2), 'sev': SEV[m.group(3)], 'kind': m.group(4).strip(' ·'), 'line': i + 1, 'f': {}}
        issues.append(iss); cur['issues'].append(iss['id']); continue
    m = re.match(r'^- ([^:]{2,14}): ?(.*)$', l)
    if m and iss is not None: iss['f'][m.group(1)] = m.group(2)
def sids(raw):
    out = []
    for part in re.split(r'[,;/·\s]+', raw):
        m = re.match(r'^s(\d+)\s*[-~–]\s*s(\d+)$', part)
        if m: out += [f's{k}' for k in range(int(m.group(1)), int(m.group(2)) + 1)]
        elif re.match(r'^s\d+$', part): out.append(part)
    return out
def cat(k):
    t = k.lower()
    if re.search(r'name|이름|명칭|회상|recall|retriev|reconstruct|cue|단서|니모닉|사용자 요구', t): return '이름·단서'
    if re.search(r'visual|시각|그림|수량|방향|count|direction|가닥|위치|구획|색|모양|literal|합성|가시', t): return '그림·수량·방향'
    if re.search(r'scien|과학|범위|일반화|단정|정확|인과|용어|개념|scope|general|precision|causal|termin|error|오류|적용|예외|절단|흡수|기전|정의|수치|단위|절대|배타|혼동|오독|누락|모순', t): return '과학·범위'
    if re.search(r'language|문법|비문|말투|wording|tone|narration|손상|corruption|문장|대본|structure|낭독|발음', t): return '말·문장'
    return '기타'
LS = {os.path.basename(p)[:-5]: json.load(open(p, encoding='utf-8')) for p in glob.glob(os.path.join(ROOT, 'lessons', 'L*.json'))}
norm = lambda t: re.sub(r'\s+', '', t)
for x in issues:
    x['sids'] = sids(x['sid_raw']); x['cat'] = cat(x['kind'])
    Lz = LS.get(x['lesson']); q = x['f'].get('현재 표현', '')
    if x['sev'] == 'resolved_lang' or not Lz: x['quote'] = 'n/a'; continue
    stops = [s for s in Lz['stops'] if s['sid'] in x['sids']] or Lz['stops']
    hay = norm(' '.join(' '.join(str(s.get(k, '')) for k in ('obj', 'fact', 'hook', 'say')) for s in stops))
    allh = norm(' '.join(' '.join(str(s.get(k, '')) for k in ('obj', 'fact', 'hook', 'say')) for s in Lz['stops']))
    fr = [f.strip(' "“”\'‘’.…') for f in re.split(r' / |…|\.\.\.', re.sub(r'^(fact|obj|hook|say):\s*', '', q)) if len(f.strip(' "“”\'‘’.…')) >= 6]
    hit = sum(1 for f in fr if norm(f) in hay)
    x['quote'] = 'n/a' if not fr else 'found' if hit == len(fr) else 'partial' if hit else 'elsewhere' if any(norm(f) in allh for f in fr) else 'not_found'
blob = lambda p: subprocess.run(['git', '-C', ROOT, 'hash-object', p], capture_output=True, text=True).stdout.strip()
for lid, v in lessons.items():
    Lz = LS.get(lid); v['stops_now'] = len(Lz['stops']) if Lz else None
    v['img_same'] = bool(Lz) and blob(os.path.join(ROOT, 'lesson', Lz['img'])) == v['sha']
c = collections.Counter(x['sev'] for x in issues); cv = collections.Counter(v['verdict'] for v in lessons.values())
print('과', len(lessons), dict(cv), '· 항목', len(issues), dict(c))
print('인용문 대조(미해결):', dict(collections.Counter(x['quote'] for x in issues if x['sev'] != 'resolved_lang')))
print('그림 해시가 지금과 같은 과:', sum(v['img_same'] for v in lessons.values()), '/', len(lessons), '· 구간 수가 같은 과:', sum(v['n'] == v['stops_now'] for v in lessons.values()))
assert len(lessons) == 142 and len(issues) == 246 and c['critical'] == 8 and c['major'] == 121 and c['minor'] == 87 and c['resolved_lang'] == 30, '인계문의 수와 다르다'
here = os.path.dirname(os.path.abspath(__file__))
def lines(path, rows):   # 한 줄에 한 항목 — diff 가 읽히게
    with open(path, 'w', encoding='utf-8') as f:
        f.write('[\n' + ',\n'.join(json.dumps(r, ensure_ascii=False) for r in rows) + '\n]\n')
if '--write' in sys.argv:
    ip = os.path.join(here, 'issues.json')
    old = {r['id']: r for r in json.load(open(ip, encoding='utf-8'))} if os.path.exists(ip) else {}
    rows = []
    for x in issues:
        r = dict(old.pop(x['id'], {}))          # 손으로 채운 칸을 지킨다
        r.update({'id': x['id'], 'lesson': x['lesson'], 'sids': x['sids'], 'sev': x['sev'], 'kind': x['kind'], 'cat': x['cat'], 'quote': x['quote'], 'line': x['line']})
        r.setdefault('state', 'resolved_lang' if x['sev'] == 'resolved_lang' else 'open')
        rows.append(r)
    rows += list(old.values())                  # 인계문에 없는 줄(N-…)은 뒤에 그대로
    lines(ip, rows)
    lines(os.path.join(here, 'lessons.json'), [{'lesson': lid, 'verdict': v['verdict'], 'stops': v['n'], 'img_blob': v['sha'], 'img_same': v['img_same'], 'issues': v['issues'], 'line': v['line']} for lid, v in sorted(lessons.items())])
    print('썼다 → issues.json(', len(rows), '줄) · lessons.json')
else:
    print('(세어 보기만 했다 — 파일을 고치려면 --write)')
if full_out:
    assert not os.path.abspath(full_out).startswith(ROOT + os.sep), '원문이 든 JSON 은 저장소 밖에 쓴다'
    json.dump({'lessons': lessons, 'issues': issues}, open(full_out, 'w', encoding='utf-8'), ensure_ascii=False)
    print('원문 포함 →', full_out)
