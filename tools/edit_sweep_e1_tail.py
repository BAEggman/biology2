#!/usr/bin/env python3
"""d01p02 · s11p04 — E1 꼬리 세 장을 이미 그려진 것에 건다 (그림 무수정).

  d01p02 「세포분열 수치 격자」 — SVG 안에 G₁ · S · G₂ 눈금과 DNA량 곡선이 이미 있다
      S 칸(DNA만 4→8)        ← E1-44   복제가 일어나는 시기 = S기
      간기 왼쪽 끝 G₁(곡선 4) ← E1-115  DNA 함량이 가장 적은 때 = G₁

  s11p04 「담장 안과 담장 밖」 — 담장 안은 곧은 띠, 굴뚝집은 끝없는 고리다
      #7 고리에는 빈 자락이 없다 ← E1-116#2  세균 = 원형, 사람 = 선형

★ 걸지 않은 것 — 그림에 없다
    E1-116#1 「둘 다 DNA+단백질·슈퍼코일」 — 실(DNA)과 실패(단백질)는 s37에 있지만
             슈퍼코일은 어디에도 없다. 셋 중 둘만 그려져 있으면 걸지 않는다
    E1-116   위 둘을 합친 카드라 같은 이유로 보류
    E1-114   간기 염색질의 영토 — 핵 안 배치를 그린 그림이 없다
    E1-88    돌연변이의 해로움 — 「돌연변이」가 덱 전체에 소품으로 없다
    E1-117   단원 한 줄 요약 — 특정 소품에 걸 것이 아니다
"""
import os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SK = os.path.join(ROOT, 'sketchy.html')

EDITS = [
    # ── d01p02 S기 : 소품을 곡선 위 자리로 구체화하고 E1-44를 건다
    ('["S기","DNA량만 2배 — 동원체가 안 늘어 염색체 수는 그대로"]',
     '["가로축 간기 구간의 S 칸 — 여기서 <b>DNA량 곡선만</b> 4에서 8로 뛴다",'
     '"<b>DNA 복제가 일어나는 때가 S기</b>다. DNA량만 2배가 되고 동원체는 안 늘어 '
     '염색체 수는 그대로다 — 두 곡선이 여기서 갈라지는 것이 그 뜻이다",["E1-44"]],\n'
     '       ["간기 구간 왼쪽 끝 G₁ — DNA량 곡선이 4로 가장 낮게 시작한다",'
     '"<b>세포 당 DNA 함량이 가장 적은 때가 G₁</b>이다. S에서 복제하기 전이라서다 — '
     '곡선이 왼쪽 끝에서 제일 낮은 것이 그대로 답이다",["E1-115"]]'),

    # ── s11p04 #7 : 원형과 선형이 한 그림 안에 있다
    ('"<b>환형 DNA에는 말단이 없어</b> 이 문제가 생기지 않는다. '
     '세균의 염색체도 같은 이유로 겪지 않는다",["E1-91"]]',
     '"<b>환형 DNA에는 말단이 없어</b> 이 문제가 생기지 않는다. '
     '세균의 염색체도 같은 이유로 겪지 않는다. '
     '★ 담장 안의 띠는 <b>곧은 선형</b>이고 굴뚝집 것은 <b>끝이 없는 원형</b>이다 — '
     '<b>사람 염색체는 선형, 세균 염색체는 원형</b>이라는 대비가 이 한 그림 안에 있다",'
     '["E1-91","E1-116#2"]]'),
]


def main():
    s = open(SK, encoding='utf-8').read()
    for old, new in EDITS:
        n = s.count(old)
        if n != 1:
            print('✗ 앵커가 %d회: %s…' % (n, old[:70]))
            return 1
        s = s.replace(old, new)

    # ★ 그린 것만 건다 — d01p02 SVG 안에 G₁·S 눈금이 실제로 있는지 확인한다
    i = s.index("{id:'d01p02'")
    svg = re.search(r'svg:`([\s\S]*?)`', s[i:]).group(1)
    for need in ('G₁', '>S<', 'DNA만 2배 (4→8)', 'DNA량'):
        assert need in svg, '★ d01p02 그림에 %s 가 없다' % need

    for pid in ('d01p02', 's11p04'):
        j = s.index("{id:'%s'" % pid)
        d, q, k, esc = 0, None, j, False
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
        blk = s[j:k + 1]
        cards = re.findall(r'"([A-Z]\d?-[\w#]+)"', blk)
        assert len(cards) == len(set(cards)), '%s 카드 중복' % pid
        print('%s 카드 %d장' % (pid, len(cards)))
    open(SK, 'w', encoding='utf-8').write(s)
    print('그림 무수정 세 장: E1-44 · E1-115 · E1-116#2')
    return 0


if __name__ == '__main__':
    sys.exit(main())
