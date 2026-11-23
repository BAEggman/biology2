#!/usr/bin/env python3
# mkaudit.py <과…> — 덱 감사(상시 요청 지시서 §4)의 과마다 판을 만든다(2026-11-23 · Opus 5.5).
#   저장소: tools/audit/2026-11-23/과/<과>/기계.md — 기계 걸음(문 1 · 2 · 3 · 장부 · 떨어진 구간 · 대장 · 녹음 · 잠금)과 정거장 표 · 걸린 카드
#   저장소 밖: /tmp/audit/<과>/판/  full.jpg(1400) · small.jpg(780) · sN.jpg(· sN_k.jpg) — 사용자 대역 독자와 본 세션이 본다
#              /tmp/audit/<과>/눈/  mkreaders.py 의 ㄱ · ㄴ · ㄷ 판(눈 검사가 없거나 그림이 그 뒤 바뀐 과만 · --eye 를 주면 늘 만든다)
import json, os, re, subprocess, sys, shutil
from PIL import Image
R = '/tmp/b2'; OUT = '/tmp/audit'; A = f'{R}/tools/audit/2026-11-23'
EYE0 = f'{R}/tools/audit/2026-11-20/눈검사'
strip = lambda s: re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', str(s or ''))).strip()
def node(*a): return json.loads(subprocess.check_output(['node', *a], cwd=R))
NAMES = node('tools/audit_lesson_names.js', '--json')
CANON = node('tools/audit_lesson_canon.js', '--json')
BOARDS = node('tools/audit_lesson_boards.js', '--json')
SC = node('tools/cue/names/stopcards.js')
CARDS = {c['id']: c for c in json.loads(re.search(r'id=["\']CARDS["\'][^>]*>([\s\S]*?)</script>', open(f'{R}/index.html', encoding='utf-8').read()).group(1))}
LED = json.load(open(f'{R}/tools/cue/names/장부.json', encoding='utf-8'))
DROP = json.load(open(f'{R}/tools/audit/2026-11-20/떨어진구간.json', encoding='utf-8'))['rows']
ISS = json.load(open(f'{R}/tools/audit/2026-11-20/issues.json', encoding='utf-8'))
MAN = json.load(open(f'{R}/lesson/audio/manifest.json', encoding='utf-8'))['lessons']
LOCK = json.load(open(f'{R}/tools/cue/lock.json', encoding='utf-8'))
def gitct(p):
    o = subprocess.run(['git', 'log', '-1', '--format=%ct', '--', p], cwd=R, capture_output=True, text=True).stdout.strip()
    return int(o or 0)
def need_eye(L):
    e = f'{EYE0}/{L}'
    return (not os.path.isdir(e)) or gitct(f'lesson/img/{L}.webp') > gitct(e)
def cell(s, n=None): s = strip(s).replace('|', '／'); return s[:n] + '…' if n and len(s) > n else s
def build(L, eye=False):
    d = json.load(open(f'{R}/lessons/{L}.json', encoding='utf-8'))
    sids = [s['sid'] for s in d['stops']]
    pan = f'{OUT}/{L}/판'; shutil.rmtree(pan, ignore_errors=True); os.makedirs(pan)
    subprocess.run(['python3', f'{R}/tools/prompts/mkcheck2.py', L, pan, ','.join(sids)], check=True, stdout=subprocess.DEVNULL)
    os.remove(f'{pan}/stops.tsv')
    im = Image.open(f'{R}/lesson/img/{L}.webp').convert('RGB')
    im.resize((780, round(im.height * 780 / im.width)), Image.LANCZOS).save(f'{pan}/small.jpg', quality=88)
    ne = need_eye(L) or eye
    if ne: subprocess.run(['python3', f'{R}/tools/cue/mkreaders.py', L, f'{OUT}/{L}/눈'], check=True, stdout=subprocess.DEVNULL)
    rec = set((MAN.get(L) or {}).keys())
    o = [f'# 기계 걸음 — {L} · {d.get("title","")}', '', f'- 부제: {strip(d.get("sub",""))}', f'- 그림: lesson/img/{L}.webp ({im.width}×{im.height}) · 정거장 {len(sids)} · 녹음된 구간 {len(rec)}: {" ".join(sorted(rec, key=lambda s:int(s[1:]))) or "없음"}',
         f'- 잠금(lock.json): {"있음 — 잠긴 글 · 그림은 지적하지 않는다" if L in LOCK else "없음"}',
         f'- 눈 검사: {"이번에 새로(" + OUT + "/" + L + "/눈)" if ne else "있음 — " + EYE0 + "/" + L + " (ㄱ · ㄴ · ㄷ 결과 · 답열쇠)"}', '',
         '## 정거장(보이는 것 obj · 사실 fact · 고리 hook · 걸린 카드)', '']
    for s in d['stops']:
        ids = SC.get(L, {}).get(s['sid'], [])
        o.append(f"### {s['sid']}{' (녹음됨)' if s['sid'] in rec else ''}")
        o.append(f"- obj: {strip(s['obj'])}")
        o.append(f"- fact: {strip(s['fact'])}")
        o.append(f"- hook: {strip(s.get('hook'))}")
        o.append(f"- say: {cell(s.get('say'), 400)}")
        cs = []
        for cid in ids[:8]:
            c = CARDS.get(cid.split('#')[0])
            if c: cs.append(f"{cid}: {cell(c.get('q'), 90)} → {cell((c.get('a') or '') + ' ' + ' '.join(c.get('it') or []), 110)}")
        o.append(f"- 카드 {len(ids)}" + (':' if cs else ''))
        o += [f'  - {x}' for x in cs]
        if len(ids) > 8: o.append(f'  - … {len(ids) - 8} 장 더')
        o.append('')
    o += ['## 문 1 — 이름 짝(카드 답의 음차 · 약어 · tools/audit_lesson_names.js)', '', '| 구간 | 낱말 | 판정 | 사전의 소품 | 장부 갈래 · 상태 |', '|---|---|---|---|---|']
    for r in [r for r in NAMES if r['lesson'] == L]:
        e = LED.get(f"{L}|{r['term']}") or {}
        g = r['gate'] + (' · 옛 면제' if r['old'] and r['gate'] == 'N' else '')
        o.append(f"| {r['sid']} | {r['term']} | {g} | {' / '.join(r['props'] or []) or '—'} | {e.get('갈래','')} {cell(e.get('상태',''),40)} |")
    lr = [e for k, e in LED.items() if e['과'] == L and not any(r['lesson'] == L and r['term'] == e['낱말'] for r in NAMES)]
    if lr:
        o += ['', '장부의 다른 줄(독자 ㄴ 이 못 꺼냈거나 「하는 일로 짐작」으로 맞힌 낱말):', '']
        o += [f"- {e['낱말']} · {' '.join(e.get('구간', []))} · {e['출처']} · {e.get('갈래','')} {cell(e.get('상태',''),50)}" for e in lr]
    o += ['', '## 문 2 — 기호 일관(canon.json)', '']
    o += [f"- {x['규칙']}: {x['까닭']}" for x in CANON if x['과'] == L] or ['- 어긋남 없음']
    o += ['', '## 문 3 — 판 낱말(obj)', '']
    o += [f"- {x['sid']}: {' · '.join(x['낱말'])}{' (허용)' if x['허용'] else ''}" for x in BOARDS if x['과'] == L] or ['- 없음']
    o += ['', '## 떨어진 구간(11-20 눈 검사 · 잠기지 않은 까닭)', '']
    o += [f"- {r['sid']}: {cell(r['why'], 220)}" for r in DROP if r['lesson'] == L] or ['- 없음']
    o += ['', '## 대장(issues.json)의 이 과 항목', '']
    o += [f"- {x['id']} · {x.get('state')} · {','.join(x.get('sids') or [])} · {x.get('cat','')} · {cell(x.get('note0') or x.get('reproduced') or '', 160)}" for x in ISS if x.get('lesson') == L] or ['- 없음']
    os.makedirs(f'{A}/과/{L}', exist_ok=True)
    open(f'{A}/과/{L}/기계.md', 'w', encoding='utf-8').write('\n'.join(o) + '\n')
    return ne
if __name__ == '__main__':
    eye = '--eye' in sys.argv
    for L in [a for a in sys.argv[1:] if not a.startswith('--')]:
        print(L, '눈 새로' if build(L, eye) else '눈 있음')
