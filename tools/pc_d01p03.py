# -*- coding: utf-8 -*-
"""d01p03(광합성 Z 도식) pc 훑기 — 38장을 다섯 판정으로 갈랐다.

  ① 행으로 내림   14장 (순환 두 장은 그림에 까닭을 적어 준 뒤 내렸다)
  ④ 그림 고침 후 새 행 19장 (루멘·ATP 합성효소 확대 칸 다섯 장이 여기 들어 있다)
  ③ 폐기           5장

★ 도해는 Gemini 없이 내가 직접 고칠 수 있다. 그래서 그림 판이었으면 ③ 폐기였을 것이
   여기서는 ④ 그림 고침이 된다 — 판정이 판의 종류를 탄다.

폐기 다섯과 그 까닭
  C0-134 광계 하나만 가진 세균     — 세균이 이 도식에 없다
  C0-81  흡수 파장이 다른 까닭     — 단백질 환경은 그릴 것이 없다
  C0-85  두 광계의 공통점          — 집광복합체·반응중심복합체가 상자 안에 안 그려져 있다
  C0-184 캘빈에서 ADP·NADP⁺ 재생   — 되돌아오는 화살표가 없다
  C0-246 G3P 의 저장·수송 형태     — 전분도 자당도 없다 (캘빈회로는 원 하나로만 있다)
"""
import os, re, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SK = os.path.join(ROOT, 'sketchy.html')

def close_brace(t, i):
    op = t[i]; cl = {'{': '}', '[': ']'}[op]
    d, q, j, esc = 0, None, i, False
    while j < len(t):
        c = t[j]
        if q:
            if esc: esc = False
            elif c == '\\': esc = True
            elif c == q: q = None
        elif c in '"\'`': q = c
        elif c == op: d += 1
        elif c == cl:
            d -= 1
            if d == 0: return j
        j += 1
    raise SystemExit('괄호 안 닫힘')

def q2(s):
    assert '"' not in s and '\\' not in s, s
    return '"%s"' % s

# ── ① 기존 행에 내린다 — (바늘, 카드들) ─────────────────────────────
DEMOTE = [
 ('먼저 작동하는 광계', ['C0-80']),
 ('전자의 출발점',      ['C0-94']),
 # ⚠ 「순환적 경로」는 「비순환적 경로」 안에 통째로 들어 있다 — 행 여는 [ 부터 잡는다
 ('["순환적 경로"',     ['C0-127', 'C0-136']),
 ('["비순환적 경로"',   ['C0-8', 'C0-115', 'C0-115#1']),
 ('명반응 장소',        ['A0-107', 'C0-38', 'C0-238']),
 ('더미 밖으로 뻗은 낱장 주머니', ['C0-244', 'C0-244#1', 'C0-244#2']),
 ('도식 아래 — 깔개 위에 포개 쌓은 납작한 주머니 더미', ['C0-30']),
]

# ── ④ 그림에 있는데 행이 없던 것 — 새 행 일곱 ──────────────────────
NEW_ROWS = [
 ('★ 세로축이 <b>전자의 에너지</b>이고, 두 상자에서 <b>빨간 빛 화살표가 두 번</b> 위로 민다',
  '<b>광계 하나로는 모자라기 때문</b>이다 — 광계 II만으로는 전자를 NADP⁺를 환원할 만큼 '
  '높이 못 올린다. 그래서 광계 I이 한 번 더 밀어 올린다. ★ 두 번 미는 것이 이 도식의 Z 모양이다',
  ['C0-114']),

 ('두 상자에 붙은 이름표 — 왼쪽이 <b>P680</b>, 오른쪽이 <b>P700</b>',
  '<b>반응중심 엽록소</b>의 이름이고, 그것이 두 광계의 차이다 — 흡수 최대 파장이 다르고 '
  '<b>전자 흐름에서 놓인 자리</b>도 다르다(앞이냐 뒤냐). 광계 II 쪽이 P680이다',
  ['C0-76', 'C0-86']),

 ('가운데 회색 원 셋 — <b>PQ · Cyt · PC</b> · 그 아래 <b>H⁺ 퍼내기 → ATP</b>',
  '두 광계 사이의 <b>전자전달계</b>다. 광계 II 바로 다음이 <b>플라스토퀴논(PQ)</b>이고, '
  '내려가며 잃은 에너지로 H⁺를 퍼낸다',
  ['C0-100']),

 ('오른쪽 — <b>Fd</b> 다음 <b>NADP⁺</b> 상자에서 <b>「환원」</b> 화살표가 <b>NADPH 방패</b>로 간다',
  '<b>NADP⁺를 NADPH로 환원</b>하는 것이 그 화살표다. 광합성의 <b>환원력</b>이 저장되는 곳이 '
  'NADPH이고, 방패 아래 적힌 대로 <b>비순환에서만</b> 나온다',
  ['C0-107', 'C0-17', 'C0-115#2']),

 ('★ 아래 그림 — <b>ATP · NADPH</b> 화살표가 <b>깔개(스트로마) 위를 지나</b> '
  '<b>캘빈회로(CO₂ → 당)</b>로 들어간다',
  '두 반응을 잇는 것이 이 <b>두 분자</b>다. 캘빈회로는 빛을 직접 안 쓰지만 <b>ATP와 NADPH를 '
  '빛반응에서 받으므로</b> 빛과 무관하지 않다. ★ 화살표가 깔개 위를 지나는 것이 요점이다 — '
  '둘 다 <b>스트로마 쪽</b>에 있으니 바로 쓸 수 있다. 빛반응은 ATP·NADPH·O₂를 내고 '
  '캘빈회로는 CO₂를 붙잡는다',
  ['C0-10', 'C0-178', 'C0-18', 'C0-36', 'C0-239', 'C0-237']),

 ('도식 아래 한 줄 — <b>물 → 광계 II → 전달계 → 광계 I → NADP⁺</b>',
  '전자가 <b>물에서 출발해 NADP⁺까지 한 방향으로</b> 간다 — 그래서 <b>선형</b>이다. '
  '★ 번호가 아니라 흐름 순서로 읽는다',
  ['C0-116']),

 ('★ 맨 아래 확대 칸 — 주머니를 갈라 보면 <b>안쪽에 H⁺가 쌓여 있고</b>, '
  '테두리(막)에 박힌 <b>ATP 합성효소</b>를 지나 <b>아래쪽으로</b> 나온다',
  '갈라야 하는 공간이 셋이다 — <b>스트로마 · 틸라코이드막 · 틸라코이드 루멘</b>. '
  '<b>H⁺ 창고는 루멘</b>이고, 통과 방향은 <b>루멘 → 스트로마</b>다. '
  '★ 그래서 <b>ATP가 스트로마 쪽에서 난다</b> — 캘빈회로가 쓰는 바로 그 자리다',
  ['C0-138', 'C0-111', 'C0-112', 'C0-148', 'C0-37']),
]

DROP = ['C0-134', 'C0-81', 'C0-85', 'C0-184', 'C0-246']

def main():
    src = open(SK, encoding='utf-8').read()
    i = src.index("{id:'d01p03'")
    e = close_brace(src, i)
    blk = src[i:e + 1]
    assert '루멘' in blk, '그림 고침(edit_d01p03_lumen.py)을 먼저 돌려야 한다'

    pc = re.search(r"pc:\[([^\]]*)\]", blk).group(1)
    pcs = [x.strip().strip('"') for x in pc.split(',') if x.strip()]
    planned = set(DROP)
    for _, cs in DEMOTE: planned |= set(cs)
    for _, _, cs in NEW_ROWS: planned |= set(cs)
    assert set(pcs) == planned, ('판정 안 한 것: %s / 없는 것: %s'
                                 % (sorted(set(pcs) - planned), sorted(planned - set(pcs))))

    fi = blk.index('f:[')
    # ① 내림
    for needle, cards in DEMOTE:
        assert blk.count(needle, fi) == 1, '바늘이 %d번: %s' % (blk.count(needle, fi), needle)
        k = blk.index(needle, fi)
        a = k if blk[k] == '[' else blk.rindex('[', fi, k)
        b = close_brace(blk, a)
        row = blk[a:b + 1]
        p1 = 1; p2 = row.index('"', p1 + 1)
        f1 = row.index('"', p2 + 1); f2 = row.index('"', f1 + 1)
        rest = row[f2 + 1:-1].strip()
        old = [x.strip().strip('"') for x in rest.strip(',').strip('[]').split(',') if x.strip()]
        for c in cards: assert c not in old, c
        new = ('[' + row[p1:p2 + 1] + ',' + row[f1:f2 + 1] + ',['
               + ','.join('"%s"' % c for c in old + cards) + ']]')
        blk = blk[:a] + new + blk[b + 1:]
        fi = blk.index('f:[')

    # ④ 새 행 — 사실표 끝에 붙인다
    fe = close_brace(blk, fi + 2)
    rows = []
    for prop, fact, cards in NEW_ROWS:
        rows.append('[' + q2(prop) + ',' + q2(fact) + ',[' + ','.join(q2(c) for c in cards) + ']]')
    blk = blk[:fe] + ',\n     ' + ',\n     '.join(rows) + blk[fe:]

    # pc 를 비운다
    blk = re.sub(r"pc:\[[^\]]*\],", '', blk, count=1)

    out = src[:i] + blk + src[e + 1:]
    b2 = out[out.index("{id:'d01p03'"):]
    b2 = b2[:close_brace(b2, 0) + 1]
    cs = re.findall(r'"([A-Z]\d?[A-Z0-9]*(?:-[A-Z0-9]+)*-[\w#]+)"', b2)
    assert len(cs) == len(set(cs)), '카드 중복: ' + str([c for c in cs if cs.count(c) > 1])
    open(SK, 'w', encoding='utf-8').write(out)
    print('d01p03 pc 38 → 0 · 내림 %d장 · 새 행 %d개(%d장) · 폐기 %d장 · 이 판 카드 %d장'
          % (sum(len(c) for _, c in DEMOTE), len(NEW_ROWS),
             sum(len(c) for _, _, c in NEW_ROWS), len(DROP), len(cs)))
    return 0

if __name__ == '__main__':
    sys.exit(main())
