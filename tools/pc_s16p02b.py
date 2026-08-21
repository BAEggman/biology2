# -*- coding: utf-8 -*-
"""s16p02b(전화국 · 판과 자갈 창고) pc 훑기 — 8장. ★ 폐기가 한 장도 없다.

넷은 s16p02 의 pc 에도 **똑같이 얹혀 있던 것**이다(B0-95·B0-115·B0-191·B0-96).
양쪽 행으로 내리면 그대로 배열이 된다 — pc 가 두 판에 겹쳐 얹히는 것도 pc 의 흔한 모습이고,
그 상태로는 「두 판에 걸쳐 있다」인지 「어느 쪽인지 몰라 둘 다 얹었다」인지 구별되지 않는다.
행으로 내려야 그 둘이 갈린다.
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pc_sweep import sweep

PIZZA = '둥근 피자 한 판'          # 1행 PIP₂ → IP₃ + DAG
SAFE  = '["구멍 셋 뚫린 조각을'    # 2행 IP₃ 가 Ca²⁺ 채널을 연다
CHICK = '["구멍 없는 민 조각은'    # 3행 DAG → PKC
PEBB  = '["금고 열쇠구멍에서 쏟아지는 작은 자갈"'   # 4행 Ca²⁺ 방출

sweep('s16p02b',
  DEMOTE=[
    (PIZZA, ['B0-193', 'S-SG-7', 'X-SG-8', 'B0-96']),
    (PEBB,  ['B0-95', 'B0-115', 'B0-191']),
    (SAFE,  ['X-SG-27']),
  ])
