#!/usr/bin/env python3
"""s04p05 「후구 구역」 — 극피=후구 카드 하나를 건다 (그림 무수정).

  별 간판이 걸린 넷째 가게는 앞벽이 벽돌로 막혀 있어 모퉁이를 돌아 옆으로 들어간다.
  극피(별)와 후구(옆문)가 **한 가게**에 겹쳐 있는 것이 이 카드 그대로다.
      ← X-AN-2  극피동물은 선구인가 후구인가? → 후구동물

★ 같은 패널에서 걸지 않은 셋 — 그림에 없다
    X-AN-4 장체강(원장 벽이 주머니로 떨어짐)   — 체강 만드는 방식이 안 그려졌다
    X-AN-5 부정난할(4세포기 할구를 떼어도 완전) — 난할이 안 그려졌다
    X-AN-9 2배엽성 = 자포·유즐                 — 배엽 수가 안 그려졌다
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SK = os.path.join(ROOT, 'sketchy.html')

EDITS = [
    ('["꼭짓점 다섯인 별 간판","극피 — 성체 5방사"]',
     '["꼭짓점 다섯인 별 간판 — 그 간판이 걸린 가게가 바로 앞벽이 막힌 넷째 가게다",'
     '"<b>극피</b> — 성체 5방사. ★ 별(극피)과 옆문(후구)이 <b>같은 가게</b>에 걸려 있는 것이 '
     '요점이다. <b>극피동물은 후구동물</b>이고, 무척추동물이라는 이유로 선구로 고르면 틀린다",'
     '["X-AN-2"]]'),
]


def main():
    s = open(SK, encoding='utf-8').read()
    for old, new in EDITS:
        n = s.count(old)
        if n != 1:
            print('✗ 앵커가 %d회' % n)
            return 1
        s = s.replace(old, new)
    i = s.index("{id:'s04p05'")
    d, q, k, esc = 0, None, i, False
    while k < len(s):
        c = s[k]
        if q:
            if esc: esc = False
            elif c == '\\': esc = True
            elif c == q: q = None
        elif c in '"\'`': q = c
        elif c == '{': d += 1
        elif c == '}':
            d -= 1
            if d == 0: break
        k += 1
    blk = s[i:k + 1]
    ids = re.findall(r'"([A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-[\w#]+)"', blk)
    assert len(ids) == len(set(ids)), '카드 중복'
    assert '앞벽이 막혀 옆으로 돌아 들어가는 넷째 가게' in blk, '넷째 가게 행이 있어야 말이 된다'
    open(SK, 'w', encoding='utf-8').write(s)
    print('s04p05 카드 %d장 (새로 1장: X-AN-2)' % len(ids))
    return 0


if __name__ == '__main__':
    sys.exit(main())
