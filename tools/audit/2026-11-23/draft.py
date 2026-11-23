#!/usr/bin/env python3
# draft.py <과> — 대역 독자의 표(과/<과>/대역_결과.md)와 새 눈 검사(눈검사/<과>/)를 읽어 번호 붙은 초안을 짧게 보인다(본 세션이 그림을 보며 받고 · 고치고 · 버린다 → put.py).
#   초안은 과/<과>/초안.json 에 남는다(줄마다 번호 · 출처).
import json, os, re, sys
R = '/tmp/b2'; A = f'{R}/tools/audit/2026-11-23'
def table(md, head):
    m = re.search(r'^## ' + head + r'\s*\n(.*?)(?=^## |\Z)', md, re.S | re.M)
    if not m: return []
    rows = []
    for l in m.group(1).splitlines():
        if not l.startswith('|') or re.match(r'^\|\s*-', l) or '근거' in l and '구간' in l and '부호' in l or ('낱말' in l and '갈래' in l and '근거' in l): continue
        c = [x.strip() for x in l.strip().strip('|').split('|')]
        if any(c): rows.append(c)
    return rows
def sect(md, head):
    m = re.search(r'^## ' + head + r'\s*\n(.*?)(?=^## |\Z)', md, re.S | re.M)
    return m.group(1).strip() if m else ''
def eye(L):
    d = f'{A}/눈검사/{L}'; out = []
    if not os.path.isdir(d): return out
    for f in ('ㄱ_결과.md', 'ㄴㄷ_결과.md'):
        p = f'{d}/{f}'
        if not os.path.exists(p): out.append(f'(없음 {f})'); continue
        t = open(p, encoding='utf-8').read()
        tail = [l for l in t.splitlines() if re.search(r'○\s*\d+\s*·\s*△', l)]
        out.append(f"{f[:-6]} 합계: {' / '.join(x.strip() for x in tail[-2:]) or '?'}")
        if f.startswith('ㄴㄷ'):
            for l in t.splitlines():
                c = [x.strip() for x in l.strip().strip('|').split('|')] if l.startswith('|') else []
                if len(c) >= 4 and re.search(r'하는 일로 짐작|남은 것|모름', ' '.join(c[2:5])) and not re.match(r'^-+$', c[0]):
                    out.append('  ㄴ △✕ ' + ' | '.join(c[:5])[:150])
                if len(c) >= 3 and re.search(r'✕|끊김|어긋남', c[2] if len(c) > 2 else '') and re.match(r'^s\d', c[0]):
                    out.append('  ㄷ ' + ' | '.join(c[:4])[:170])
        else:
            for l in t.splitlines():
                c = [x.strip() for x in l.strip().strip('|').split('|')] if l.startswith('|') else []
                if len(c) >= 3 and re.match(r'^s\d', c[0]) and c[2].startswith('✕'): out.append('  ㄱ ' + ' | '.join(c[:4])[:170])
    return out
if __name__ == '__main__':
    L = sys.argv[1]; p = f'{A}/과/{L}/대역_결과.md'
    md = open(p, encoding='utf-8').read() if os.path.exists(p) else ''
    lines = []
    for c in table(md, '지적'):
        c += [''] * (6 - len(c))
        lines.append({'구간': c[0], '부호': c[1], '근거': c[2], '걸린': c[3], '처방': c[4], '확신': c[5], '출처': '대역'})
    names = [{'낱말': c[0], '구간': c[1] if len(c) > 1 else '', '갈래': c[2] if len(c) > 2 else '', '근거': c[3] if len(c) > 3 else ''} for c in table(md, '이름 갈래')]
    dr = {'과': L, '줄': lines, '이름': names, '지킬 것': sect(md, '지킬 것'), '과학 의심': sect(md, '과학 의심'), '총평': sect(md, '총평'), '눈': eye(L)}
    json.dump(dr, open(f'{A}/과/{L}/초안.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'== {L} 지적 {len(lines)} · 이름 {len(names)}')
    for i, x in enumerate(lines, 1): print(f"{i}. {x['구간']} {x['부호']} [{x['확신']}] {x['근거'][:150]} ‖ {x['걸린'][:50]} → {x['처방']}")
    print('이름:', ' · '.join(f"{n['낱말']}{n['갈래'][:1]}" for n in names))
    print('과학:', dr['과학 의심'][:200].replace('\n', ' '))
    print('총평:', dr['총평'][:300].replace('\n', ' '))
    for e in dr['눈']: print(e)
