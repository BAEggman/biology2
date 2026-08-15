#!/usr/bin/env python3
"""d05p03 「성결정 네 체계」 — 그림에 이미 그려져 있는데 안 걸려 있던 카드 넷을 건다.

★ 그린 것만 건다 — SVG를 열어 실측한 결과만 반영한다.
  · Z-W 열 윗줄(암)에 굵은 주황 테두리 + 「hetero = 암컷」 배지가 있다      → E0-139
  · X-Y·X-O 두 열의 배지가 둘 다 「hetero = 수컷」이다                      → E0-140
  · X-O 열 칸 속: 암은 긴 막대 하나, 수는 긴 막대 하나 + 점선 하나(O)      → E0-147 (새 행)
  · Z-W 열 칸 속: 암은 보라 긴 것과 보라 짧은 것 둘, 수는 보라 긴 것 하나  → E0-146 (새 행)

★ 걸지 않은 것 — E0-181(바소체 수 = X 수 − 1).
  그림에는 「두 X 중 하나를 끈다 → 바소체」까지만 있고 공식도 예시(XXX=2 등)도 없다.
  d05p09를 그릴 때 거기 건다.

DATA 재직렬화 없이 문자열 치환만 한다. 앵커는 전부 정확히 1회여야 한다.
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SK = os.path.join(ROOT, 'sketchy.html')

ROW_XO = ('["X-O 열의 칸 속 — 암 칸에는 긴 막대 하나뿐이고, 수 칸 둘에는 긴 막대 하나와 점선 하나다",'
          '"<b>X-O의 배우자 생산</b> — 암컷은 X만 내고, 수컷은 X를 담은 것과 '
          '성염색체를 못 받은 것(O) 두 가지를 낸다. 점선이 그 <b>없음</b>이다",'
          '["E0-147"]]')

ROW_ZW = ('["Z-W 열의 칸 속 — 암 칸 둘에는 보라 긴 막대와 보라 짧은 막대가 하나씩, '
          '수 칸 하나에는 보라 긴 막대다",'
          '"<b>Z-W의 배우자 생산</b> — 수컷은 Z만 내고, 암컷은 Z 또는 W 두 가지를 낸다. '
          'X-Y와 견주면 내는 쪽이 뒤집혀 있다",'
          '["E0-146"]]')

EDITS = [
    # ① Z-W 윗줄(암) — 「암컷이 hetero인 체계는?」의 답이 바로 이 자리다
    ('"Z-W 체계에서 <b>heterogametic sex는 암컷</b>이다",["E0-81"]]',
     '"Z-W 체계에서 <b>heterogametic sex는 암컷</b>이다",["E0-81","E0-139"]]'),

    # ② X-Y·X-O 공통 — 「수컷이 hetero인 체계는?」의 답
    ('"X-O와 X-Y의 공통점은 <b>둘 다 수컷이 heterogametic sex</b>라는 것이다",["E0-92"]]',
     '"X-O와 X-Y의 공통점은 <b>둘 다 수컷이 heterogametic sex</b>라는 것이다",["E0-92","E0-140"]]'),

    # ③ X-O 배우자 생산 — X-O 두 줄 바로 뒤에 새 행
    ('"X-O 체계에서 <b>homogametic sex는 암컷</b>이다",["E0-80"]],',
     '"X-O 체계에서 <b>homogametic sex는 암컷</b>이다",["E0-80"]],\n     ' + ROW_XO + ','),

    # ④ Z-W 배우자 생산 — Z-W 두 줄 바로 뒤에 새 행
    ('"Z-W 체계에서 <b>homogametic sex는 수컷</b>이다",["E0-82"]],',
     '"Z-W 체계에서 <b>homogametic sex는 수컷</b>이다",["E0-82"]],\n     ' + ROW_ZW + ','),
]


def main():
    s = open(SK, encoding='utf-8').read()
    for old, new in EDITS:
        n = s.count(old)
        if n != 1:
            print('✗ 앵커가 %d회: %s…' % (n, old[:70]))
            return 1
        s = s.replace(old, new)

    # 카드 중복 검사 — d05p03 블록 안에서
    i = s.index("{id:'d05p03'")
    d, q, k, esc = 0, None, i, False
    while k < len(s):
        c = s[k]
        if q:
            if esc: esc = False
            elif c == '\\': esc = True
            elif c == q: q = None
        elif c in '"\'`':
            q = c
        elif c == '{':
            d += 1
        elif c == '}':
            d -= 1
            if d == 0:
                break
        k += 1
    blk = s[i:k + 1]
    cards = re.findall(r'"(E0-[\w#]+)"', blk)
    assert len(cards) == len(set(cards)), '카드 중복'
    open(SK, 'w', encoding='utf-8').write(s)
    print('d05p03 카드 %d장 (새로 넷: E0-139 · E0-140 · E0-146 · E0-147)' % len(cards))
    return 0


if __name__ == '__main__':
    sys.exit(main())
