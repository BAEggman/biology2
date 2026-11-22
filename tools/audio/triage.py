#!/usr/bin/env python3
# triage.py <판 폴더> <답 열쇠 폴더> L... — 독자 ㄱ·ㄴ·ㄷ 결과 + 감사 대장 + 기호 묶음(grp)을 읽어 구간마다 「넘음 / 볼 것 / 안 됨」.
# 분류일 뿐 판정이 아니다 — 잠금은 사람이(⑤ 글 · 과학 읽기 포함) 정한다. 표는 stdout(마크다운).
# 규칙은 stoprules.py 하나에(2026-11-22 — ① 은 과 전체가 아니라 항목이 닿는 구간만 · grp 는 과 전체 ②).
#   판 폴더 대신 「-」 를 주면 대장 규칙(① ② · 다시 그릴 구역)만 본다 — 눈 검사 전에 어느 구간을 볼지 고를 때.
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from stoprules import classify

eye, keys, Ls = sys.argv[1], sys.argv[2], sys.argv[3:]
for L in Ls:
    if eye == '-': res = classify(L)
    else: res = classify(L, f'{eye}/{L}', f'{keys}/{L}.key.json')
    print(f'### {L}\n\n| 구간 | 분류 | 까닭 |\n|---|---|---|')
    for s, (k, no, see) in res.items():
        print(f"| {s} | {k} | {' / '.join(no + see)[:300] or '—'} |")
    print()
