#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""isLoan 의 눈먼 자리 훑기 — 음차 감사가 아예 못 보는 이름을 찾는다.

★ 왜 만들었나 (2026-08-28, 사용자 지적에서 이어짐)
  `tools/audit_loanwords.js` 의 `isLoan()` 은 **ㅡ로 끝나는 무받침 음절**이나
  **외래어 전용 음절**이 있어야 음차로 본다. 그래서

      로돕신 · 랍도 · 필로 · 파라믹소 · 액틴 · 미오신 · 히스톤 · 콜라겐 …

  처럼 그 표지가 없는 음차는 **통째로 감사 밖**에 있었다. 실제로 s15p02 의
  로돕신이 그렇게 빠져 있었고, 사용자가 눈으로 먼저 잡았다.
  덱이 이미 「음차/임의 이름」이라 판정해 둔 246개로 재 보면
  **51개(21%)** 를 isLoan 이 놓친다.

★ 어떻게 찾는가 — 덱이 스스로 한 판정으로 탐지기를 학습시킨다
  양성 표본 = `_외래어면제` 의 한글 이름 + `hooks` 의 한글 키
             (= 덱이 「이건 인출해야 하는 임의 이름」이라 판정한 것들)
  부정 표본 = 덱 산문(br · 사실 칸)의 나머지 낱말 (거의 다 고유어·한자어)
  → 음절 단위 로그오즈를 내고, 낱말 점수를 그 평균으로 삼는다.

  ★ 여기에 **두음법칙**을 더한다. 한국어 고유어·한자어는 ㄹ로 시작하지 않는다.
    그래서 **초성 ㄹ 은 음차의 강한 표지**다 — 라미닌·랍도·로돕신·루피니·
    리간드·리보솜·리소좀이 전부 그 한 규칙으로 잡힌다.

⚠ 이것은 래칫이 아니다. 어림짐작이라 잡음이 섞인다(즉시·잠깐·훨씬 같은 부사).
  **사람이 한 줄씩 판정**해서 셋 중 하나로 보낸다:
    ① 진짜 음차/임의 이름 → 후크를 세운다
    ② 오탐(순 한국어·한자어)  → `_음차오탐`
    ③ 음차지만 면제           → `_외래어면제`
  ⚠ 후크가 있는 이름은 면제에 넣을 수 없다(verify_hooks.js 가 막는다).

★ 이 훑기가 처음 돌자마자 드러낸 것 (2026-08-28)
  **비타민의 한글 이름 여섯**이 후크는 그려져 있는데 사전에는 번호로만
  올라 있었다 — 티아민(넥타이) · 나이아신(나이 든 사람의 신발) ·
  코발라민(코발트빛 코) · 비오틴(양철과 빗방울) · 피리독신(피리) ·
  판토텐산(널빤지 다섯). 사실 칸은 여섯 다 「…가 곧 이름이다」라고
  적어 두었는데 감사는 이름을 **글자 그대로** 찾으므로 못 알아봤다.
  ★ 교훈: 사전과 사실 칸이 어긋나는 자리를 따로 봐야 한다.
"""
import re, json, collections, math, os, sys

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
strip = lambda x: re.sub('<[^>]+>', '', x or '')
KOR = re.compile(r'[가-힣]{2,}')
# ⚠ audit_loanwords.js 의 JOSA 를 그대로 쓰면 **과하게 깎인다** — 「로·나·고·며·성·째·한」을 떼면
#   레트로→레트 · 코로나→코로 · 피코르나→피코르 처럼 이름이 토막 난다(2026-08-28 에 실제로 그랬다).
#   저쪽은 그 토막을 isLoan 이 어차피 잡아 주어 티가 안 났을 뿐이다. 여기서는 뺀다.
#   ★ 2026-08-31 — 「이란·이라는」만 더했다(스플라이싱이란→스플라이싱). ⚠ 「인」은 절대 넣지 마라 — 헤파린→헤파, 팔로이딘→팔로이드로 토막 난다.
JOSA = re.compile(r'(은|는|이|가|을|를|의|에|에서|와|과|도|만|부터|까지|보다|처럼|이라|라고|이고|면서|하고|하는|된|되는|들|만이|에는|에도|이나|이란|이라는)$')
PID = r"\{id:'([a-z]\d+p\d+[a-z]?)'"
CID = r'"([A-Za-z0-9]+(?:-[A-Za-z0-9]+)+(?:#\d+)?)"'

# ── audit_loanwords.js 의 isLoan 을 그대로 옮긴다 (둘이 갈리면 안 된다) ──
EU = set('프브트드크그스즈츠르므느흐쁘뜨쓰쯔플블틀들클글슬즐츨를믈늘흘')
STRONG = set('플블틀캐퍼쉬셰뷰퓨츄쥬뜨쁘랄뤼웨왁펩렌롤린틴딘')
TAIL = re.compile(r'[다서면지고며는은을어아게나자라도만까므든거져야니죠데때수것쪽뒤곳덜뿐임함됨직채중앞옆위밑끝셋넷둘록보]$')
DEMO = re.compile(r'^(그|이|저|여기|거기|우리|서로|모두|각각|다시|아주|매우|거의|바로|전자|연관)')

def isLoan(t):
    if len(t) < 3: return False
    if TAIL.search(t) or DEMO.match(t): return False
    eu = sum(1 for c in t if c in EU); st = sum(1 for c in t if c in STRONG)
    return st > 0 or eu >= 2 or (eu >= 1 and len(t) >= 4)

def load():
    s = open(os.path.join(R, 'sketchy.html'), encoding='utf-8').read()
    cards = json.loads(re.search(r'id=["\']CARDS["\'][^>]*>([\s\S]*?)</script>',
            open(os.path.join(R, 'index.html'), encoding='utf-8').read()).group(1))
    H = json.load(open(os.path.join(R, 'tools/hooks.json'), encoding='utf-8'))
    return s, {c['id']: c for c in cards}, H

def build(s, H):
    L = lambda k: set((H.get(k) or {}).get('목록', {}))
    hooks = H['hooks']
    exempt = (L('_외래어면제') | L('_음차오탐') | L('_뜻이있는약어') | L('_답면제')
              | L('_인명면제') | L('_표기별칭') | set(H.get('_인명오탐') or []) | set(hooks))
    pj = open(os.path.join(R, 'tools/audit_phonetics.js'), encoding='utf-8').read()
    exempt |= set(re.search(r'const KNOWN = new Set\(`([\s\S]*?)`', pj).group(1).split())
    # ── 점수기 학습 ──
    pos = {w for w in L('_외래어면제') if KOR.fullmatch(w)} | {k for k in hooks if KOR.fullmatch(k)}
    prose = [strip(m.group(1)) for m in re.finditer(r"br:'((?:[^'\\]|\\.)*)'", s)]
    prose += [strip(a) + ' ' + strip(b) for a, b in re.findall(r'\["([^"]*)"\s*,\s*"([^"]*)"', s)]
    neg = collections.Counter()
    for t in prose:
        for w in KOR.findall(t):
            if w not in pos: neg[w] += 1
    cp = collections.Counter(); cn = collections.Counter()
    for w in pos: cp.update(w)
    for w, k in neg.items(): cn.update({c: k for c in w})
    tp, tn = sum(cp.values()), sum(cn.values())
    lo = lambda c: math.log(((cp[c] + .5) / (tp + .5 * len(cp))) / ((cn[c] + .5) / (tn + .5 * len(cn))))
    CHO = 'ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ'
    cho = lambda c: CHO[(ord(c) - 0xAC00) // 588] if '가' <= c <= '힣' else ''
    def score(w):
        v = sum(lo(c) for c in w) / len(w)
        return v + 1.6 if cho(w[0]) == 'ㄹ' else v      # ★ 두음법칙
    # ── 판 증거 ──
    ms = list(re.finditer(PID, s)); ev = {}; c2p = collections.defaultdict(set)
    for k, m in enumerate(ms):
        end = ms[k + 1].start() if k + 1 < len(ms) else len(s)
        blk = s[m.start():end]
        props = ' '.join(strip(a) for a, _ in re.findall(r'\["([^"]*)"\s*,\s*"([^"]*)"', blk))
        svg = ' '.join(strip(t) for t in re.findall(r'<text\b[^>]*>([\s\S]*?)</text>', blk))
        ev[m.group(1)] = props + ' ' + svg
        for c in re.findall(CID, blk): c2p[c].add(m.group(1))
    return exempt, score, ev, c2p, hooks

def sweep(th=1.2):
    s, A, H = load()
    exempt, score, EV, C2P, hooks = build(s, H)
    def carries(e, w):
        if w in e: return True
        hk = hooks.get(w)
        return bool(hk and any(p in e for p in hk.get('props', [])))
    cand = collections.defaultdict(lambda: {'cards': set(), 'panels': set()})
    for cid, c in A.items():
        if cid not in C2P: continue
        q, a = strip(c.get('q', '')), strip(c.get('a', ''))
        e = ' '.join(EV.get(p, '') for p in C2P[cid])
        for t in KOR.findall(a):
            t = JOSA.sub('', t)
            if len(t) < 2 or isLoan(t) or t in exempt: continue
            if t in q: continue                     # ★ 발문이 주면 인출 대상이 아니다
            if score(t) < th: continue
            if carries(e, t): continue
            cand[t]['cards'].add(cid); cand[t]['panels'] |= C2P[cid]
    return A, score, sorted(cand.items(), key=lambda kv: (-len(kv[1]['cards']), -score(kv[0])))

if __name__ == '__main__':
    th = float(os.environ.get('TH', '1.2'))
    A, score, out = sweep(th)
    n = len({c for _, v in out for c in v['cards']})
    if '--sum' in sys.argv:
        print(f'isLoan 눈먼 자리 후보 {len(out)}개 · 카드 {n}장 (문턱 {th})'); sys.exit(0)
    print(f'★ isLoan 이 못 보는 후보 {len(out)}개 · 카드 {n}장 (문턱 {th})\n')
    for w, v in out:
        print(f'{score(w):+5.2f} {w:14s} {len(v["cards"]):3d}장  판 {sorted(v["panels"])[:4]}')
