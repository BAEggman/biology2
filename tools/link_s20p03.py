#!/usr/bin/env python3
"""s20p03 — 이미 그려져 있는데 안 걸린 것을 건다.

s20p03(양면 스위치와 평형석) 아래쪽에 **뿌리 끝 단면**이 이미 그려져 있다 —
아래로 몰린 무거운 알갱이(평형석)와 아래로 휘는 뿌리 끝(굴중성 양성).
그런데 그 두 행에 카드가 하나도 안 걸려 있었고, P1-21(평형석)은 pc 에만 있었다.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pc_demote import demote
from link_cards import link
from pc_judge_batch5 import link_one   # P1-15 가 두 행에 걸린 판이라 link_cards 를 못 쓴다

LINK = [
    ('s20p03', '아래로 몰린 무거운 알갱이', ['P1-21'],
     '<b>평형석</b>(statolith) — 녹말이 든 <b>녹말체</b>가 무거워 <b>중력 방향으로 가라앉는다</b>. '
     '어느 쪽이 아래인지를 아는 방법이 이것이다'),

    ('s20p03', '아래로 휘는 뿌리 끝', ['P1-20#1'],
     '<b>뿌리는 굴중성 양성</b> — 중력 쪽(아래)으로 휜다. '
     '★ <b>줄기는 반대로 음성</b>이라 위로 휘는데, 그것은 옆 판(눕힌 화분)에 있다'),
]


def main():
    if demote('s20p03', {'P1-21'}): return 1
    for pid, needle, cards, extra in LINK:
        link_one(pid, needle, cards, extra)
    return 0


if __name__ == '__main__':
    sys.exit(main())
