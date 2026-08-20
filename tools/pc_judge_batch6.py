#!/usr/bin/env python3
"""pc 접지 감사 6차 — ★ 다섯째 판정 「여러 판에 걸기」를 쓴다.

★ 이번에 알아낸 것
  PMAP 값은 **배열이 될 수 있다.** 한 카드를 여러 판에 걸면 앱의 「그림으로 복구」가
  그 판들을 **전부 차례로 보여 준다**(index.html: pidList(PMAP[id]).forEach).
  test/verify_links.js 의 「걸친 2장은 배열」이 그 설계를 이미 못 박아 두었다.

  그러므로 **목록 카드의 답은 폐기도 종합 도해도 아니다** — 항목이 전부 그려져만 있다면
  **그 판들에 나눠 걸면 된다.** 그러면 카드를 뽑았을 때 세 그림이 함께 뜬다.

  ⚠ 단, 항목 중 **하나라도 덱에 안 그려져 있으면** 여전히 폐기다. 그것이 「그린 것만 건다」다.

★ 이번 판정
  G0-184 (2차 전달자 5종)  cAMP=s16p02 · Ca²⁺·DAG·IP₃=s16p02b · cGMP=s15p02  → 배열 셋
  S-SG-6 (전령별 표적 넷)  PKA=s16p02 · PKC·ER방출=s16p02b · 칼모듈린=s08p03   → 배열 셋
  S-PL-14                  5차에서 잘못 뗐다 — 원래부터 s20p01a|s20p01b 배열이다 → 복원
  S-SG-5 (생성 효소 셋)    구아닐산 고리화효소가 덱에 없다 → s16p02 에서도 뗀다
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pc_demote import demote
from link_cards import link

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SK = os.path.join(ROOT, 'sketchy.html')

DEMOTE = {
    's16p02': ['G0-184', 'S-SG-6', 'S-SG-5'],
}

LINK = [
    ('s16p02', '왼쪽 기계 — ', ['G0-184'],
     '★ 2차 전달자 다섯 중 <b>cAMP</b>가 이 방이다. 나머지는 옆방의 <b>Ca²⁺·DAG·IP₃</b>와 '
     '시각 편의 <b>cGMP</b>다 — 이 카드는 그 판들에 함께 걸려 있어 그림이 차례로 뜬다'),
    ('s16p02b', '기계에 통째로 들어가는 ', ['G0-184'],
     '★ 2차 전달자 다섯 중 <b>IP₃ · DAG</b>가 여기서 갈라져 나오고 '
     '금고에서 쏟아지는 자갈이 <b>Ca²⁺</b>다 — 셋이 이 한 방에 있다'),
    ('s15p02', '텅 빈 천장 통', ['G0-184'],
     '★ 2차 전달자 다섯 중 <b>cGMP</b>가 이것이다 — 신호 전달의 방이 아니라 '
     '<b>시각</b>에서 나오는 것이 이 하나뿐이라 자주 빠뜨린다'),

    ('s16p02', ' 꼭대기에서 조는 감독을', ['S-SG-6'],
     '★ 전령별 표적 넷 중 <b>cAMP → PKA</b>가 이것이다. '
     '나머지는 DAG → PKC · IP₃ → 소포체 Ca²⁺ 방출 · Ca²⁺ → 칼모듈린이다'),
    ('s16p02b', '구멍 없는 민 조각은 작업대에 그대로', ['S-SG-6'],
     '★ 전령별 표적 넷 중 둘이 이 방에 있다 — <b>DAG → PKC</b>(C자 갈고리)와 '
     '<b>IP₃ → 소포체 Ca²⁺ 방출</b>(금고 문)이다'),
    ('s08p03', '조수를 데려오는 인물', ['S-SG-6'],
     '★ 전령별 표적 넷 중 <b>Ca²⁺ → 칼모듈린</b>이 이것이다 — '
     '2차 전달자 편이 아니라 평활근 편에 있어 놓치기 쉽다'),
]

RESTORE = {'s20p01a': ['S-PL-14']}   # 5차 오판 되돌리기


def restore_pc(pid, cards):
    s = open(SK, encoding='utf-8').read()
    i = s.index("{id:'%s'" % pid)
    m = re.search(r'pc:\[(.*?)\]', s[i:i + 6000])
    ids = [x.strip().strip('"') for x in m.group(1).split(',') if x.strip()]
    for c in cards:
        assert c not in ids, c
    ids = sorted(set(ids + list(cards)))
    new = 'pc:[' + ','.join('"%s"' % x for x in ids) + ']'
    s = s[:i] + s[i:].replace(m.group(0), new, 1)
    open(SK, 'w', encoding='utf-8').write(s)
    print('  %-8s pc에 %d장 되돌림 (pc %d장)' % (pid, len(cards), len(ids)))


def main():
    for pid, ids in DEMOTE.items():
        if demote(pid, set(ids)): return 1
    if link(LINK): return 1
    for pid, cards in RESTORE.items():
        restore_pc(pid, cards)
    print('\n판정 — 배열로 살린 것 2장(판 6곳) · 복원 1장 · 추가 폐기 1장(S-SG-5)')
    return 0


if __name__ == '__main__':
    sys.exit(main())
