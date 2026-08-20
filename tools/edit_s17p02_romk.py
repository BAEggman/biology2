#!/usr/bin/env python3
"""s17p02 — 굵은 상행각에 ROMK 를 더한다 (2026-08-20).

pc 접지 3차에서 S-RN-4·X-RN-15 를 폐기했었다. 사유가 「굵은 상행각 수송체 2종 중
NKCC2 만 그려졌고 ROMK 가 없다」였고, 「로마 투구와 칼을 하나 더 붙이면 걸린다」라고 적어 두었다.
그림을 그렇게 고쳤으므로 되살린다. 폐기는 회귀가 아니라 정정이었고, 정정의 정정도 마찬가지다.

★ 후크는 s17p03 것을 그대로 쓴다 — 로마 투구가 ROM, 칼이 K(칼륨).
  ⚠ 이 판에는 NKCC2 의 「칼 하나」가 이미 있는데, 둘 다 K(칼륨)이라 충돌이 아니라 일관이다
    (점검표 ④ — 같은 상징이 같은 사실).
★ 방향이 급소다. s17p03 의 ROMK 는 알갱이를 관강으로 쏟는데, 여기서도 **관 안쪽으로** 쏟는다.
  굵은 상행각의 ROMK 는 NKCC2 를 돌리려고 K 를 관강으로 되돌려 보내는 것이기 때문이다.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pc_judge_batch1 import add_row

NEWROW = ('s17p02',
          '★ 굵은 부분 벽 위쪽 — <b>로마 병정 투구</b>를 쓴 사람이 <b>칼</b>로 작은 문을 비틀어 열자 '
          '알갱이가 <b>관 안쪽으로</b> 쏟아진다',
          '<b>ROMK</b>. 로마 투구가 <b>ROM</b>, 칼이 <b>K</b>(칼륨)다 — s17p03의 그 사람과 같다. '
          '굵은 상행각의 관강막 수송체는 <b>둘</b>이다 — 소금·칼·염소를 <b>들이는</b> NKCC2와, '
          'K를 <b>관강으로 되돌려 보내는</b> ROMK. '
          '★ 되돌려 보내는 까닭은 <b>NKCC2를 계속 돌리려면 관강 쪽에 K가 있어야</b> 하기 때문이다 — '
          '이 <b>K 순환</b>이 주세포의 K 분비와 헷갈리는 자리다',
          ['S-RN-4', 'X-RN-15'])


def main():
    add_row(*NEWROW)
    print('★ baseline.pmapRemoved 에서 S-RN-4 · X-RN-15 를 지워야 한다')
    return 0


if __name__ == '__main__':
    sys.exit(main())
