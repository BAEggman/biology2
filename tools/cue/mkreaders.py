#!/usr/bin/env python3
# mkreaders.py <과 id> <판 폴더> [--seed N] — 눈 검사 셋(tools/cue/README.md §8)의 판을 독자마다 따로 만든다(2026-11-20 · Opus 5.5).
#   <판>/ㄱ/  full.jpg · small.jpg(780 px 폭) · sN.jpg(· sN_k.jpg) · stops.tsv(sid · obj)          — 독자 ㄱ(블라인드 · 이름 대기)
#   <판>/ㄴ/  full.jpg · small.jpg · sN.jpg(· sN_k.jpg) · terms.txt(답 낱말 + 가짜 낱말, 섞음)      — 독자 ㄴ(이름 인출 · obj/fact/hook 없음)
#   <판>/ㄷ/  full.jpg · sN.jpg(· sN_k.jpg) · stops.tsv(sid · obj · fact)                         — 독자 ㄷ(사실 대조)
#   답 열쇠(어느 낱말이 진짜 · 어느 정거장 · 고리 종류)는 판 밖 <판>.key.json 에 — 독자에게 주지 않는다.
#   답 낱말 = tools/audit/2026-11-19/lesson_names.js 가 그 과에서 뽑은 이름(카드 답의 음차 · 약어) + fact 머리말(「X — …」의 X 가 짧을 때).
#   가짜 낱말 = 같은 단원(tools/lesson_topics.js) 다른 과의 이름에서, 이 과에 없는 것을 답 낱말 수의 절반쯤.
import json, os, random, re, subprocess, sys, shutil
from PIL import Image
ROOT = '/tmp/b2'
lid, out = sys.argv[1], sys.argv[2]
seed = int(sys.argv[sys.argv.index('--seed') + 1]) if '--seed' in sys.argv else 7
d = json.load(open(f'{ROOT}/lessons/{lid}.json', encoding='utf-8'))
sids = [s['sid'] for s in d['stops']]
shutil.rmtree(out, ignore_errors=True)
for r in 'ㄱㄴㄷ':
    os.makedirs(f'{out}/{r}')
    subprocess.run(['python3', f'{ROOT}/tools/prompts/mkcheck2.py', lid, f'{out}/{r}', ','.join(sids)], check=True, stdout=subprocess.DEVNULL)
im = Image.open(f'{ROOT}/lesson/img/{lid}.webp').convert('RGB')
sm = im.resize((780, round(im.height * 780 / im.width)), Image.LANCZOS)
for r in 'ㄱㄴ': sm.save(f'{out}/{r}/small.jpg', quality=88)
os.remove(f'{out}/ㄴ/stops.tsv')
open(f'{out}/ㄷ/stops.tsv', 'w', encoding='utf-8').write('\n'.join(f"{s['sid']}\t{s['obj']}\t{s['fact']}" for s in d['stops']) + '\n')
rows = json.loads(subprocess.check_output(['node', f'{ROOT}/tools/audit/2026-11-19/lesson_names.js', '--json'], cwd=ROOT))
real = {}
for r in rows:
    if r['lesson'] == lid: real.setdefault(r['term'], {'sid': r['sid'], 'cls': r['cls'], 'props': r['props']})
for s in d['stops']:
    h = s['fact'].split(' — ')[0].strip()
    for part in re.split(r'\s*[·,]\s*', h):
        if 2 <= len(part) <= 12 and part not in real and not re.search(r'\s', part): real[part] = {'sid': s['sid'], 'cls': 'fact', 'props': None}
# (2026-11-21 넷째 묶음) 답 열쇠 고침 — ① 정거장 번호를 카드가 아니라 이 과의 stops 에서 다시 잡는다(그 낱말이 hook · fact · obj · say 에 처음 나오는 정거장) · ② 군더더기 낱말(괄호 짝 안 맞음 · 화살표 · 「/」 · 한 글자 · 흔한 말)을 뺀다.
JUNK = {'생산', '바이러스', '세균', '세포', '단백질', '효소', '호르몬', '물', '빛'}
def _clean(t):
    return not (len(t) < 2 or t in JUNK or t.count('(') != t.count(')') or re.search(r'[↑↓→←/]', t))
def _home(t):
    for f in ('hook', 'fact', 'obj', 'say'):
        for s in d['stops']:
            if t in (s.get(f) or ''): return s['sid']
    return None
for t in list(real):
    if not _clean(t): real.pop(t); continue
    h = _home(t)
    if h and h != real[t]['sid']: real[t]['sid_card'] = real[t]['sid']; real[t]['sid'] = h
src = open(f'{ROOT}/tools/lesson_topics.js', encoding='utf-8').read()
scene = d.get('scene', '')
# 같은 단원: lesson_topics.js 의 단원 덩어리에서 이 과의 장면(sNN)이나 id 가 든 덩어리
units = re.split(r"\{\s*title:\s*'", src)[1:]
mine = next((u for u in units if f"'{scene}'" in u or f"'{lid}'" in u), '')
sc = set(re.findall(r"'(s\d\d)'", mine)); ls = set(re.findall(r"'(L\d\d[a-z])'", mine))
pool = sorted({r['term'] for r in rows if r['lesson'] != lid and (r['lesson'][:3].replace('L', 's') in sc or r['lesson'] in ls) and r['term'] not in real})
rnd = random.Random(seed)
fake = rnd.sample(pool, min(len(pool), max(3, len(real) // 2)))
terms = list(real) + fake; rnd.shuffle(terms)
open(f'{out}/ㄴ/terms.txt', 'w', encoding='utf-8').write('\n'.join(terms) + '\n')
json.dump({'lesson': lid, 'real': real, 'fake': fake}, open(f'{out}.key.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print(lid, 'stops', len(sids), '· 답 낱말', len(real), '· 가짜', len(fake), '→', out)
