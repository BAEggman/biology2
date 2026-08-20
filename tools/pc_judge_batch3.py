#!/usr/bin/env python3
"""pc 접지 판정 3차 — s19p02 · s17p02

① 행으로 내림 (2장)
 s19p02  C1-25   행 「파수꾼을 화로에 던짐 → APC/C가 시큐린을 분해」 — 분해되는 것이 곧 시큐린이다
 s19p02  C1-123  같은 행 — 화로가 APC/C다. (Cdc20은 아직 안 그려져 있다.
                 화로에 손잡이를 하나 달아 「이것을 잡아야 불이 붙는다」로 그리면 더 낫다)

② 폐기 (3장)
 s19p02  C1-148  사이토칼라신 B는 수축환·액틴 이야기인데 이 판에는 고리와 커터뿐이다.
                 → s19p03 세포질분열 판을 만들 때 걸린다.
 s17p02  S-RN-4  굵은 상행각 수송체 2종 중 NKCC2만 그려졌다. ROMK(로마 투구+칼)가 없다.
                 → 고칠 그림: 굵은 부분 벽에 로마 투구와 칼을 하나 더 붙인다.
 s17p02  X-RN-15 K+가 관강으로 되새는 것이 그려져 있지 않다. 같은 그림 수정으로 함께 풀린다.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pc_demote import demote
from link_cards import link

DOWN = {'s19p02': ['C1-25', 'C1-123']}
DROP = {'s19p02': ['C1-148'], 's17p02': ['S-RN-4', 'X-RN-15']}
LINK = [('s19p02', '파수꾼을 화로에 던짐', ['C1-25', 'C1-123'],
         ' 던져지는 파수꾼이 <b>시큐린</b>이고 화로가 <b>APC/C(후기촉진복합체)</b>다 — '
         '억제자를 <b>없애서</b> 억제를 푸는 이중 부정이다')]


def main():
    rc = 0
    print('① 행으로 내림')
    for pid, cs in DOWN.items(): rc |= demote(pid, set(cs))
    print('② 폐기')
    for pid, cs in DROP.items(): rc |= demote(pid, set(cs))
    if rc: return rc
    print('③ 행에 달기'); rc |= link(LINK)
    print('\n내림 2 · 폐기 3 = pc에서 5장 뺌')
    return rc


if __name__ == '__main__':
    sys.exit(main())
