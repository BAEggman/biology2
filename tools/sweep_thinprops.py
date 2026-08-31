#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""얇은 소품 칸 훑기 — 「소품 칸이 그림보다 덜 적힌 자리」를 찾는다.

★ 왜 만들었나 (2026-08-31)
  s07p03 의 칼시토닌이 그렇게 나왔다. 소품 칸은 「레버를 내리는 손」 아홉 글자뿐인데
  그림에는 **도르래에 매달린 바구니와 그 안의 흰 자갈**이 멀쩡히 그려져 있었다.
  자갈은 이 덱에서 Ca²⁺ 예약이므로 「칼시(칼슘)」가 이미 그림에 있었던 셈이다.

  ★ 소품 칸이 **증거**이므로, 소품 칸이 그림보다 덜 적히면 감사가 못 본다.
  ⚠ 이 갈래는 **도구로 확정할 수 없다** — 그림을 눈으로 봐야 한다.
    그래서 이 훑기는 **어느 판의 어느 행을 먼저 열어 볼지**만 정해 준다.

★ 신호
  ① 소품 칸이 짧다 (기본 16자 이하) — 덜 적혔을 자리다
  ② 그 행에 카드가 걸려 있다 — 증거가 링크를 지고 있으니 값이 크다
  ③ 사실 칸은 긴데 소품 칸만 짧다 — 아는 것에 비해 그린 것을 덜 적었다는 뜻이다
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rowlib import get_rows

R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
strip = lambda x: re.sub('<[^>]+>', '', x or '')
PID = re.compile(r"\{id:'([a-z]\d+p\d+[a-z]?)'")


def sweep(maxlen=16):
    s = open(os.path.join(R, 'sketchy.html'), encoding='utf-8').read()
    out = []
    for m in PID.finditer(s):
        pid = m.group(1)
        try:
            rows = get_rows(s, pid)
        except Exception:
            continue
        if not os.path.exists(os.path.join(R, 'img', pid + '.webp')):
            continue                      # 도해(svg) 판은 그림이 곧 글이라 뺀다
        for i, r in enumerate(rows):
            mm = re.match(r'\["((?:[^"\\]|\\.)*)"\s*,\s*"((?:[^"\\]|\\.)*)"(?:\s*,\s*\[([^\]]*)\])?', r)
            if not mm:
                continue
            prop, fact = strip(mm.group(1)), strip(mm.group(2))
            cards = [c.strip().strip('"') for c in (mm.group(3) or '').split(',') if c.strip()]
            if len(prop) <= maxlen:
                out.append((len(cards), len(fact), pid, i, prop, fact, len(prop)))
    out.sort(key=lambda x: (-x[0], -x[1]))
    return out


if __name__ == '__main__':
    n = int(os.environ.get('LEN', '16'))
    out = sweep(n)
    top = int(os.environ.get('TOP', '30'))
    print(f'★ 소품 칸이 {n}자 이하인 행 {len(out)}개 — 카드 수·사실 길이 순\n')
    for c, fl, pid, i, prop, fact, pl in out[:top]:
        print(f'  {pid:9} [{i}] 카드{c:2}  소품{pl:2}자 「{prop}」')
        print(f'  {"":9}      사실 {fact[:110]}')
