#!/usr/bin/env python3
"""덱감사.json → 고침순위.md

점수 = Σ(줄마다 (9 − 급) × max(카드,1)) × 기출 비중(그 과의 단원이 기출 1,475문 가운데 차지하는 수).
급은 RUBRIC 의 C=1 … V=8 이라 작을수록 급하다 — 9 − 급 으로 뒤집어 더한다.
기출 비중: index.html 의 EXAM questions 를 topic 으로 센 수. 과 → 단원은 tools/lesson_topics.js 의 topic id 를
아래 TOPIC 표로 EXAM topic key 에 잇는다(둘 이상이면 평균).
처방 갈래: 줄의 「처방」 낱말로 글로 풀림 / 구역 편집 / 다시 그림 을 센다.
시간 짐작: 글로 풀림 6+1 한 번 25분 · 구역 편집 한 구역 30~50분(40) · 다시 그림 반나절(240분).
"""
import json, re, os, subprocess, collections, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..'))

TOPIC = {
 'cell-structure': ['cell', 'membrane'], 'cell-signaling': ['signal'], 'cell-cycle': ['division', 'meiosis'],
 'cell-death': ['division'], 'dna': ['dna'], 'gene-expression': ['expr', 'regul'], 'cell-respiration': ['resp'],
 'photosynthesis': ['photo'], 'vitamins': ['enzyme', 'chem'], 'homeostasis': ['body'], 'endocrine': ['endo'],
 'muscle': ['neuro'], 'renal': ['excr'], 'nervous': ['neuro'], 'circulation': ['circ'], 'immune': ['immune'],
 'breathing': ['circ'], 'digestion': ['digest'], 'reproduction': ['repro', 'dev'], 'microbes': ['virus', 'divers'],
 'fungi': ['divers'], 'animals': ['divers'], 'evolution': ['evol', 'popgen'], 'plant-diversity': ['plant', 'divers'],
 'plant-transport': ['plant'], 'plant-regulation': ['plant'],
}

def exam_counts():
    t = open(os.path.join(ROOT, 'index.html'), encoding='utf-8').read()
    d = json.loads(re.search(r'<script id="EXAM" type="application/json">(.*?)</script>', t, re.S).group(1))
    return collections.Counter(q['topic'] for q in d['questions'])

def lesson_topics():
    js = ("const {lessonTopics}=require('./tools/lesson_topics');const fs=require('fs');"
          "const Ls=fs.readdirSync('lessons').filter(f=>/^L.*\\.json$/.test(f)).map(f=>JSON.parse(fs.readFileSync('lessons/'+f)));"
          "const o={};for(const u of lessonTopics(Ls))for(const t of u.topics)for(const l of t.main)o[l.id]=[t.id,t.title];"
          "process.stdout.write(JSON.stringify(o))")
    return json.loads(subprocess.check_output(['node', '-e', js], cwd=ROOT))

def kind(rx):
    rx = rx or ''
    if rx in ('구역 편집', '다시 그림', 'PIL'): return '그림'
    return '글'   # 글 · 얹는 고리 · 기호 일감

def cost(rs):
    """줄 묶음 → 분. 그림 줄은 구간마다 구역 편집 40분(전체 구간의 「다시 그림」 이 있거나 구역이 여섯을 넘으면 다시 그림 240분으로 묶음)
    + 그림을 바꾸면 눈 검사 셋 15분 · 글 줄이 있으면 6+1(글) 한 번 25분."""
    pic = [r for r in rs if kind(r.get('처방')) == '그림']
    regions = {r['구간'] for r in pic}
    redraw = any(r.get('처방') == '다시 그림' and r['구간'] == '전체' for r in pic) or len(regions) > 6
    m = (240 if redraw else 40 * len(regions)) + (15 if pic else 0)
    if any(kind(r.get('처방')) == '글' for r in rs): m += 25
    return m, redraw, len(regions)

def main():
    d = json.load(open(os.path.join(HERE, '덱감사.json'), encoding='utf-8'))
    ex = exam_counts(); lt = lesson_topics()
    rows = collections.defaultdict(list)
    for r in d['줄']: rows[r['과']].append(r)
    out = []
    for L in d['끝난 과']:
        tid, ttl = lt.get(L, ('?', '?'))
        keys = TOPIC.get(tid, [])
        w = sum(ex[k] for k in keys) / len(keys) if keys else 1
        rs = rows.get(L, [])
        base = sum((9 - r['급']) * max(r.get('카드') or 0, 1) for r in rs)
        codes = collections.Counter(r['부호'] for r in rs)
        mins, redraw, regions = cost(rs)
        nt = sum(1 for r in rs if kind(r.get('처방')) == '글')
        top = sum(codes[c] for c in ('C', 'D1'))
        nnk = sum(codes[c] for c in ('N', 'N′', 'K'))
        out.append(dict(과=L, 단원=ttl, 기출=round(w), 바탕=base, 점수=round(base * w), 줄=len(rs),
                        C_D1=top, N_K=nnk, 글=nt, 구역=regions, 다시=redraw, 분=mins, rs=rs,
                        부호=' '.join(f'{c}×{n}' for c, n in codes.most_common())))
    out.sort(key=lambda x: -x['점수'])
    ranks = sorted(ex.items(), key=lambda kv: -kv[1])
    upper = {k for k, _ in ranks[:8]}
    # 자를 선 셋
    def is_upper(o):
        tid = [t for t, (i, _) in [(x, lt[x]) for x in [o['과']]]]
        keys = TOPIC.get(lt[o['과']][0], [])
        return any(k in upper for k in keys)
    lineA = [o for o in out if o['C_D1'] > 0 and is_upper(o)]
    lineB = [o for o in out if (o['C_D1'] + o['N_K']) > 0]
    def days(lst, codes=None):
        m = 0
        for o in lst:
            rs = [r for r in o['rs'] if codes is None or r['부호'] in codes]
            m += cost(rs)[0]
        return m, m / 60 / 7   # 하루 7시간
    md = ['# 고침 순위 — 덱 감사 2026-11-23', '',
          f'덱감사.json 의 끝난 과 {len(out)} 개 · 줄 {sum(o["줄"] for o in out)}. 만든 것: `python3 tools/audit/2026-11-23/mkrank.py`.', '',
          '점수 = Σ(줄마다 (9 − 급) × 걸린 카드 수) × 그 단원의 기출 문항 수(1,475 문 가운데). 급은 C=1 · D1=2 · N/N′/K=3 · M/R=4 · W/T=5 · D2/D3=6 · X=7 · V=8.', '',
          '기출 상위 단원(가 선의 「상위」): ' + ' · '.join(f'{k} {n}' for k, n in ranks[:8]), '']
    for name, lst, only, desc in (('가', lineA, {'C', 'D1'}, '급 C · D1 줄이 있고 기출 상위 여덟 단원인 과 — 그 줄만'),
                                  ('나', lineB, {'C', 'D1', 'N', 'N′', 'K'}, '가 + N · N′ · K 줄이 있는 모든 과 — 그 줄까지'),
                                  ('다', out, None, '모든 과 · 모든 줄')):
        m, dd = days(lst, only)
        md.append(f'- **{name} 선** — {desc}: 과 {len(lst)} · 짐작 {m/60:.0f} 시간 ≈ {dd:.1f} 일(하루 7 시간)')
    top20 = [o for o in out if o in lineA][:20]
    m, dd = days(top20, {'C', 'D1'})
    md.append(f'- (참고) 가 선의 점수 위 20 과만: 짐작 {m/60:.0f} 시간 ≈ {dd:.1f} 일')
    md.append('- 짐작의 바탕: 그림 줄은 구간마다 구역 편집 40 분(구역이 여섯을 넘거나 「전체 · 다시 그림」 줄이 있으면 다시 그림 240 분) + 눈 검사 15 분 · 글 줄이 있으면 6+1 한 번 25 분. Gemini 대기 · 재시도는 넣지 않았다.')
    md += ['', '| 순 | 과 | 단원 | 기출 | 줄 | 부호 | C·D1 | N·N′·K | 글로 풀림 | 구역 편집 | 다시 그림 | 짐작 | 점수 |',
           '|---|---|---|---|---|---|---|---|---|---|---|---|---|']
    for i, o in enumerate(out, 1):
        md.append(f"| {i} | {o['과']} | {o['단원']} | {o['기출']} | {o['줄']} | {o['부호']} | {o['C_D1']} | {o['N_K']} | {o['글']} | {o['구역']} | {'예' if o['다시'] else ''} | {o['분']}분 | {o['점수']} |")
    open(os.path.join(HERE, '고침순위.md'), 'w', encoding='utf-8').write('\n'.join(md) + '\n')
    print('\n'.join(md[:12]))

if __name__ == '__main__':
    main()
