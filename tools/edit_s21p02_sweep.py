#!/usr/bin/env python3
"""s21p02 「분기도 읽기」 — 공유파생형질 카드 하나를 건다 (그림 무수정).

  #2 「갈림점의 배지를 아래 전원이 공유」 ← X-EV-4
     포유류의 털처럼 특정 분기군에만 있는 신형질 = 공유파생형질. 계통 추론에 쓰는 쪽이다.

★ 같은 패널에 걸릴 뻔했으나 그림을 보고 걸지 않은 둘
    X-EV-3 「척추처럼 모두가 가져 분류군을 못 가르는 형질 = 공유조상형질」
    X-EV-5 「외군과 내군이 함께 가진 형질 = 조상형질」
  둘 다 「외군까지 포함해 전원이 단 배지」가 있어야 성립하는데,
  확대해 보니 외군(맨 오른쪽 홀로 매달린 인물)의 배지는 **무늬가 없는 빈 배지**이고
  갈림점 배지들과 다르다. 전원 공유 배지가 그림에 없다 → 걸지 않는다.
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SK = os.path.join(ROOT, 'sketchy.html')

OLD = '["갈림점의 배지를 아래 전원이 공유","공유파생형질",["K2-17","K2-16","K2-16#1"]]'
NEW = ('["갈림점에 걸린 배지 · 그 갈림점 아래 인물 전원이 같은 배지를 달았다",'
       '"<b>공유파생형질</b>. 포유류의 털처럼 <b>특정 분기군에만</b> 새로 생긴 형질이고, '
       '계통을 추론할 때 쓰는 쪽이 이것이다. 갈림점보다 위에 있는 인물은 안 달았다는 것이 '
       '「그 무리에만 있다」이다",["K2-17","K2-16","K2-16#1","X-EV-4"]]')


def main():
    s = open(SK, encoding='utf-8').read()
    n = s.count(OLD)
    if n != 1:
        print('✗ 앵커가 %d회' % n)
        return 1
    s = s.replace(OLD, NEW)
    i = s.index("{id:'s21p02'")
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
    ids = re.findall(r'"([A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-[\w#]+)"', s[i:k + 1])
    assert len(ids) == len(set(ids)), '카드 중복'
    open(SK, 'w', encoding='utf-8').write(s)
    print('s21p02 카드 %d장 (새로 1장: X-EV-4)' % len(ids))
    return 0


if __name__ == '__main__':
    sys.exit(main())
