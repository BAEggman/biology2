#!/usr/bin/env python3
# put.py <과> <결정.json> — 본 세션이 그림을 보고 확정한 줄을 덱감사.json 에 넣는다(그 과의 앞 줄은 바꿔 씀) · 이름 장부의 갈래를 가름.json 에 단다 · 「끝난 과」에 올린다.
#   결정.json: {"받음": "all" | [번호…], "버림": {"번호": "까닭"}, "고침": {"번호": {"부호": …, "근거": …, "처방": …}}, "보탬": [{구간, 부호, 근거, 걸린, 처방}],
#              "이름": {"낱말": ["갈래", "근거"]}  (없으면 대역의 갈래를 받음) , "이름버림": [낱말…] (대역 갈래를 쓰지 않음 · 장부 그대로), "메모": "본 세션 한 줄"}
import json, os, re, sys, subprocess
R = '/tmp/b2'; A = f'{R}/tools/audit/2026-11-23'; F = f'{A}/덱감사.json'
ORDER = {'C': 1, 'D1': 2, 'N': 3, 'N′': 3, 'K': 3, 'M': 4, 'R': 4, 'W': 5, 'T': 5, 'D2': 6, 'D3': 6, 'X': 7, 'V': 8}
RX = {'글', '얹는 고리', '구역 편집', '다시 그림', '기호 일감', 'PIL'}
STATE = {'㉮?': '군더더기 후보 — 채점표 §3 의 1 · 2 에 맞는지 확인 뒤 답 열쇠에서 뺌(면제 통 밖이면 사용자에게)', '㉯': '대기 — 새 독자 ㄴ 로 다시 재기', '㉰': '대기 — 사전의 소품을 이 과에(얹을 수 있으면 ㉱ · 아니면 ㉲)', '㉱': '대기 — 6+1(글) → 새 독자 ㄴ', '㉲': '대기 — 6+1 → 구역 편집(이름 4 · 그림)'}
def main():
    L, dec = sys.argv[1], json.load(open(sys.argv[2], encoding='utf-8'))
    dr = json.load(open(f'{A}/과/{L}/초안.json', encoding='utf-8'))
    sc = json.loads(subprocess.check_output(['node', f'{R}/tools/cue/names/stopcards.js'], cwd=R)).get(L, {})
    db = json.load(open(F, encoding='utf-8')) if os.path.exists(F) else {'_뜻': '', '끝난 과': [], '줄': [], '과': {}}
    take = range(1, len(dr['줄']) + 1) if dec.get('받음', 'all') == 'all' else dec['받음']
    drop = {int(k): v for k, v in (dec.get('버림') or {}).items()}; ed = {int(k): v for k, v in (dec.get('고침') or {}).items()}
    out = []
    for i in take:
        if i in drop: continue
        x = dict(dr['줄'][i - 1]); x.update(ed.get(i, {})); x['출처'] = '대역 → 본 세션 확인' + (' · 고침' if i in ed else '')
        out.append(x)
    for x in dec.get('보탬') or []: x = dict(x); x['출처'] = x.get('출처') or '본 세션'; out.append(x)
    sp = []
    for x in out:
        for c in [c.strip() for c in x['부호'].replace("'", '′').replace('/', '·').split('·') if c.strip()]:
            y = dict(x); y['부호'] = c; sp.append(y)
    out = sp
    for x in out:
        x['과'] = L; x['부호'] = x['부호'].replace("'", '′').strip()
        assert x['부호'] in ORDER, (L, x)
        if x.get('처방') not in RX: x['처방'] = next((r for r in RX if r in (x.get('처방') or '')), '글')
        x['급'] = ORDER[x['부호']]
        sids = re.findall(r's\d+', x.get('구간', ''))
        x['카드'] = sum(len(sc.get(s, [])) for s in sids) if sids else sum(len(v) for v in sc.values())
        x['상태'] = x.get('상태') or '열림'
        x.pop('확신', None)
    db['줄'] = [y for y in db['줄'] if y['과'] != L] + out
    db['과'][L] = {'총평': dr.get('총평', ''), '지킬 것': dr.get('지킬 것', ''), '과학 의심': dr.get('과학 의심', ''), '버린 줄': {str(k): v for k, v in drop.items()}, '메모': dec.get('메모', ''), '눈': dr.get('눈', [])}
    if L not in db['끝난 과']: db['끝난 과'].append(L)
    db['_뜻'] = '덱 감사(상시 요청 지시서 §4 · 2026-11-23 ~). 줄 = 과 · 구간 · 부호(채점표 §8) · 근거 · 걸린 · 카드(그 구간에 걸린 카드 수) · 처방 · 급(1 = C … 8 = V) · 출처 · 상태. 「과」 = 과마다 총평 · 지킬 것 · 과학 의심 · 본 세션이 버린 대역 줄과 까닭. 만드는 연장: mkaudit.py → (독자) → draft.py → put.py.'
    json.dump(db, open(F, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    # 이름 장부 — 가름.json
    GP = f'{R}/tools/cue/names/가름.json'; G = json.load(open(GP, encoding='utf-8'))
    LED = json.load(open(f'{R}/tools/cue/names/장부.json', encoding='utf-8'))
    prop = {n['낱말']: (n['갈래'][:1], n['근거']) for n in dr.get('이름', []) if n.get('갈래')}
    for w in dec.get('이름버림') or []: prop.pop(w, None)
    for w, v in (dec.get('이름') or {}).items(): prop[w] = (v[0], v[1])
    n = 0
    for k, e in LED.items():
        if e['과'] != L: continue
        g = G.get(k) or {}
        if g.get('갈래') and g.get('상태'): continue  # 앞 세션이 가른 줄은 그대로
        w = e['낱말']; p = prop.get(w)
        if not p:
            p = next(((v[0], v[1]) for kk, v in prop.items() if kk.replace(' ', '') == w.replace(' ', '')), None)
        if not p: p = ('㉲', '대역 독자의 갈래 없음 — 본 세션 기본값(고리 없음으로 봄)')
        if p[0] == '㉮': p = ('㉮?', p[1])  # 군더더기 「후보」 — 답 열쇠에서 빼는 것(㉮)은 채점표 §3 의 1 · 2 를 본 세션이 따로 확인한 뒤(지시서_Opus_이름고리 §2)
        g.update({'갈래': p[0], '근거': f'덱 감사 2026-11-23 · {p[1]}', '처방': {'㉮?': '답 열쇠 · 면제 후보', '㉯': '새 독자 ㄴ', '㉰': '사전 소품', '㉱': '6+1(글)', '㉲': '6+1 → 그림(이름 4)'}.get(p[0], ''), '상태': STATE.get(p[0], '대기'), '일감': g.get('일감') or f'덱감사 {L}'})
        G[k] = g; n += 1
    json.dump(G, open(GP, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print(f'{L}: 줄 {len(out)} · 버림 {len(drop)} · 장부 갈래 {n}')
main()
