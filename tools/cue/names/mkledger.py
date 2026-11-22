#!/usr/bin/env python3
# mkledger.py [--write] — 이름 장부(지시서 tools/plan/2026-11-22/지시서_Opus_이름고리.md §2 · 2026-11-22 · Opus 5.5).
#   줄 하나 = 과 × 낱말. 자동 칸은 다음에서 다시 만든다:
#     ① tools/audit/2026-11-20/떨어진구간.json 의 「ㄴ 못 꺼냄」 구간 까닭(③ …) — 출처 「못 꺼냄」
#     ② 눈검사 원문(ㄴ_결과.md · 답열쇠.json)의 「하는 일로 짐작」 「남은 것이라서」 — 출처 「△」(잠금 · 녹음은 건드리지 않음)
#     ③ 독자 ㄴ 의 답 줄 · 독자 ㄱ 의 이름 대기 줄(그 구간) · hooks.json 의 고리 · 카드(index.html CARDS) 수 · 지금 글(say · hook)의 그 낱말 문장
#     ④ stoprules 의 ①(열린 항목) · ②(기호 묶음) — 「고치지 않음(그 일감에서 같이)」 표시
#   손 칸(갈래 · 처방 · 일감 · 상태 · 근거)은 tools/cue/names/가름.json 에만 쓴다 — 다시 만들어도 남는다.
#   결과: tools/cue/names/장부.json · 장부.md. --write 없이 돌리면 수만 보인다.
import json, os, re, sys, glob, subprocess
A = os.path.dirname(os.path.abspath(__file__))
R = os.path.abspath(os.path.join(A, '..', '..', '..'))
sys.path.insert(0, f'{R}/tools/audio')
from stoprules import load_issues, OPEN, NOT_GRP, SHARED

EYE = f'{R}/tools/audit/2026-11-20/눈검사'
H = json.load(open(f'{R}/tools/hooks.json', encoding='utf-8'))
HOOKS = H['hooks']
ALIAS = {k: v['이름'] for k, v in (H.get('_표기별칭') or {}).get('목록', {}).items()}
CARDS = {c['id']: c for c in json.loads(re.search(r'id=["\']CARDS["\'][^>]*>([\s\S]*?)</script>', open(f'{R}/index.html', encoding='utf-8').read()).group(1))}
ISS = load_issues()
SC = json.loads(subprocess.check_output(['node', f'{A}/stopcards.js'], cwd=R))
G = json.load(open(f'{A}/가름.json', encoding='utf-8')) if os.path.exists(f'{A}/가름.json') else {}
strip = lambda s: re.sub(r'<[^>]+>', '', str(s or ''))
SUBN = str.maketrans('₀₁₂₃₄₅₆₇₈₉⁺⁻', '0123456789+-')
norm = lambda t: t.translate(SUBN)


def parse_why(why):
    """떨어진 구간 까닭에서 ③ 낱말들."""
    out = []
    for p in re.split(r'\s*/\s*', why):
        p = p.strip()
        if not (p.startswith('③') or '못 꺼냄' in p): continue
        p = re.sub(r'\s*·\s*④.*$', '', p)
        m = re.match(r'^③?\s*ㄴ 못 꺼냄\s+(.+)$', p)
        if m: out.append(m.group(1).strip()); continue
        m = re.match(r'^③?\s*(.+?)\s*(—|✕)', p)
        if m: out += [w.strip() for w in re.split(r'\s*·\s*', m.group(1)) if w.strip()]
    return out


def eye_dirs(L):
    """ㄴ 원문이 든 폴더(맨 위 → 그림N 차례) — 나중 것이 앞 것을 덮는다."""
    ds = [f'{EYE}/{L}'] + sorted(glob.glob(f'{EYE}/{L}/그림*'), key=lambda p: int(re.sub(r'\D', '', os.path.basename(p)) or 0))
    return [d for d in ds if os.path.exists(f'{d}/ㄴ_결과.md')]


def n_rows(d):
    rows = {}
    for line in open(f'{d}/ㄴ_결과.md', encoding='utf-8'):
        c = [x.strip() for x in line.strip().strip('|').split('|')]
        if len(c) >= 4 and c[0] and c[0] not in ('용어', '---') and not set(c[0]) <= set('-: '):
            rows[c[0]] = c
    return rows


def g_rows(L):
    """독자 ㄱ 의 이름 대기 표: 상자 칸 → 줄."""
    ds = [f'{EYE}/{L}'] + sorted(glob.glob(f'{EYE}/{L}/그림*'))
    out = {}
    for d in ds:
        p = f'{d}/ㄱ_결과.md'
        if not os.path.exists(p): continue
        t = open(p, encoding='utf-8').read()
        m = re.search(r'이름 대기([\s\S]*?)\n## ', t)
        if not m: continue
        for line in m.group(1).splitlines():
            c = [x.strip() for x in line.strip().strip('|').split('|')]
            if len(c) >= 3 and re.match(r'^s\d+', c[0]):
                for s in re.findall(r's\d+', c[0]): out.setdefault(s, []).append(' | '.join(c[1:3]))
    return out


def hook_of(w):
    return HOOKS.get(w) or HOOKS.get(norm(w)) or (ALIAS.get(w) and HOOKS.get(ALIAS[w]))


def flags(L, sids):
    f = []
    op = [i for i in ISS if i['lesson'] == L and i['state'] in OPEN]
    g = sorted({i['grp'] for i in op if i.get('grp') and i['grp'] not in NOT_GRP})
    if g: f.append('② 기호 묶음 ' + '·'.join(g))
    for i in op:
        hit = [s for s in (i.get('sids') or []) if s in sids]
        if hit: f.append(f"① 열린 항목 {i['id']}({','.join(hit)})")
    for grp, Ls in SHARED.items():
        if L in Ls: f.append(f'② 같이 쓰는 기호 {grp}')
    return f


def build():
    rows = json.load(open(f'{R}/tools/audit/2026-11-20/떨어진구간.json', encoding='utf-8'))['rows']
    led = {}
    def add(L, w, sid, src, kinds=None):
        k = f'{L}|{w}'
        e = led.setdefault(k, {'과': L, '낱말': w, '구간': [], '출처': src, '떨어진 갈래': []})
        if sid and sid not in e['구간']: e['구간'].append(sid)
        if src == '못 꺼냄': e['출처'] = '못 꺼냄'
        if kinds:
            g = '이름뿐' if kinds == ['ㄴ 못 꺼냄'] else '겹침(' + ' · '.join(x for x in kinds if x != 'ㄴ 못 꺼냄') + ')'
            if f'{sid} {g}' not in e['떨어진 갈래']: e['떨어진 갈래'].append(f'{sid} {g}')
    for r in rows:
        if 'ㄴ 못 꺼냄' not in r['kinds']: continue
        for w in parse_why(r['why']): add(r['lesson'], w, r['sid'], '못 꺼냄', r['kinds'])
    # △ — 하는 일로 짐작 · 남은 것이라서(맞는 정거장이라도 고리가 일을 안 함)
    nans = {}; keys = {}
    for L in sorted(os.listdir(EYE)):
        for d in eye_dirs(L):
            nans.setdefault(L, {}).update(n_rows(d))
            if os.path.exists(f'{d}/답열쇠.json'): keys[L] = json.load(open(f'{d}/답열쇠.json', encoding='utf-8'))
        if L not in keys or L not in nans: continue
        for t, v in keys[L]['real'].items():
            c = nans[L].get(t)
            if c and re.search(r'하는 일로 짐작|남은 것', c[3]) and not ('없음' in c[1] or '모름' in c[3]):
                if f'{L}|{t}' not in led: add(L, t, v['sid'], '△')
    for k, e in led.items():
        L, w = e['과'], e['낱말']
        d = json.load(open(f'{R}/lessons/{L}.json', encoding='utf-8'))
        kv = (keys.get(L) or {}).get('real', {}).get(w)
        if kv:
            e['답열쇠'] = {'sid': kv.get('sid'), 'cls': kv.get('cls')}
            if kv.get('sid') and kv['sid'] not in e['구간']: e['구간'].append(kv['sid'])
        e['구간'].sort(key=lambda s: int(s[1:]))
        c = (nans.get(L) or {}).get(w)
        e['독자 ㄴ'] = ' | '.join(c[1:5]) if c else ''
        gr = g_rows(L)
        e['독자 ㄱ'] = {s: gr.get(s, []) for s in e['구간']}
        hk = hook_of(w)
        e['사전'] = {'props': hk.get('props'), '형태': hk.get('형태')} if hk else None
        cids = sorted({cid for s in d['stops'] for cid in SC.get(L, {}).get(s['sid'], [])})
        ans = q = 0
        for cid in cids:
            cc = CARDS.get(cid.split('#')[0])
            if not cc: continue
            a = strip((cc.get('a') or '') + ' ' + ' '.join(cc.get('it') or []))
            if w in a or norm(w) in norm(a): ans += 1
            elif w in strip(cc.get('q')) or norm(w) in norm(strip(cc.get('q'))): q += 1
        e['카드'] = {'답': ans, '물음만': q}
        sent = []
        for s in d['stops']:
            for f in ('hook', 'say'):
                for x in re.split(r'(?<=[.다])\s+', strip(s.get(f))):
                    if w in x or (hk and any(p in x for p in (hk.get('props') or []))):
                        sent.append(f"{s['sid']} {f}: {x}")
        e['글'] = sent[:6]
        e['obj'] = {s['sid']: strip(s['obj']) for s in d['stops'] if s['sid'] in e['구간']}
        e['막힘'] = flags(L, e['구간'])
        e.update({kk: vv for kk, vv in (G.get(k) or {}).items()})
    return led


if __name__ == '__main__':
    led = build()
    from collections import Counter
    c = Counter(e['출처'] for e in led.values())
    gc = Counter(e.get('갈래', '—') for e in led.values() if e['출처'] == '못 꺼냄')
    print(json.dumps({'줄': len(led), '출처': c, '갈래(못 꺼냄)': gc, '과': len({e['과'] for e in led.values() if e['출처'] == '못 꺼냄'})}, ensure_ascii=False))
    if '--write' in sys.argv:
        json.dump(led, open(f'{A}/장부.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        L = ['# 이름 장부 — 못 꺼낸 낱말(과 × 낱말)', '',
             '`python3 tools/cue/names/mkledger.py --write` 가 다시 만든다. 손 칸(갈래 · 처방 · 일감 · 상태 · 근거)은 `가름.json` 에만 쓴다. 지시서: `tools/plan/2026-11-22/지시서_Opus_이름고리.md` §2.', '',
             '갈래: ㉮ 군더더기 · ㉯ 다시 재면 나옴 · ㉰ 사전에 있는데 흘림 · ㉱ 얹는 고리(글) · ㉲ 새 소품(그림) · ㉳ 유지 — 붐빔(심판만). 출처 「△」는 잠금을 넘었지만 「하는 일로 짐작」으로 맞힌 낱말(㉲ 일감에만 보탬).', '',
             '## 수']
        for k, v in sorted(gc.items()): L.append(f'- {k}: {v}')
        L.append(f"- △ 줄: {c.get('△', 0)}")
        L += ['', '## 줄', '| 과 | 구간 | 낱말 | 출처 | 카드(답) | 사전 | 독자 ㄴ | 막힘 | 갈래 | 처방 | 상태 |', '|---|---|---|---|---|---|---|---|---|---|---|']
        for k, e in sorted(led.items(), key=lambda kv: (kv[1]['출처'] != '못 꺼냄', kv[0])):
            sp = ' / '.join((e['사전'] or {}).get('props') or [])[:40] if e['사전'] else ''
            cell = lambda x: str(x or '').replace('|', '¦').replace('\n', ' ')
            L.append(f"| {e['과']} | {' '.join(e['구간'])} | {cell(e['낱말'])} | {e['출처']} | {e['카드']['답']} | {cell(sp)} | {cell(e['독자 ㄴ'])[:70]} | {cell(' · '.join(e['막힘']))[:50]} | {e.get('갈래', '')} | {cell(e.get('처방', ''))[:80]} | {cell(e.get('상태', ''))} |")
        open(f'{A}/장부.md', 'w', encoding='utf-8').write('\n'.join(L) + '\n')
