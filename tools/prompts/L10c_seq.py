#!/usr/bin/env python3
# L10c_seq.py — L10c 「조차장의 오타 열차」의 여섯 열차 검산: 창(염기)과 구슬(아미노산)이 실제 유전암호 그대로인지.
# 원본 mRNA: AUG GAG CAA ACC AUU UAA (Met · Glu · Gln · Thr · Ile · 종결). 다른 스크립트(L10c_trains.py)가 TRAINS 를 가져다 그린다.
B = 'UCAG'
AA = 'FFLLSSSSYY**CC*WLLLLPPPPHHQQRRRRIIIMTTTTNNKKSSRRVVVVAAAADDEEGGGG'
CODE = {a + b + c: AA[i * 16 + j * 4 + k] for i, a in enumerate(B) for j, b in enumerate(B) for k, c in enumerate(B)}
def tr(s): return [CODE[s[i:i + 3]] for i in range(0, len(s) - 2, 3)]
N = 'AUGGAGCAAACCAUUUAA'
TRAINS = [
    # (이름, 염기열, 고친 자리(0부터 · 결실은 빠진 자리), 종류)
    ('원본', N, None, None),
    ('침묵', N[:11] + 'U' + N[12:], 11, 'sub'),          # ACC → ACU (Thr 그대로)
    ('과오', N[:4] + 'U' + N[5:], 4, 'sub'),             # GAG → GUG (Glu → Val · 겸상적혈구)
    ('정지', N[:6] + 'U' + N[7:], 6, 'sub'),             # CAA → UAA (Gln → 종결)
    ('삽입', N[:3] + 'C' + N[3:], 3, 'ins'),             # AUG 뒤에 C 하나
    ('결실', N[:3] + N[4:], 3, 'del'),                   # GAG 의 첫 G 가 빠짐
]
def beads(s):
    """종결(*) 뒤는 번역하지 않는다."""
    out = []
    for a in tr(s):
        out.append(a)
        if a == '*': break
    return out
if __name__ == '__main__':
    nb = beads(N); assert ''.join(nb) == 'MEQTI*', nb
    for name, s, pos, kind in TRAINS:
        b = beads(s); print(f'{name}: {" ".join(s[i:i + 3] for i in range(0, len(s), 3))} → {"".join(b)}')
    b = {n: beads(s) for n, s, _, _ in TRAINS}
    assert b['침묵'] == nb                                              # 구슬 그대로
    assert [x != y for x, y in zip(b['과오'], nb)] == [False, True, False, False, False, False] and b['과오'][1] == 'V'
    assert b['정지'] == ['M', 'E', '*']                                  # 두 알 뒤 종결
    assert '*' not in b['삽입'] and '*' not in b['결실']                 # 종결 코돈이 사라진다
    for k in ('삽입', '결실'):
        assert b[k][0] == 'M' and all(x != y for x, y in zip(b[k][1:5], nb[1:5])), k       # 그 뒤 모조리 딴 구슬
        assert not (set(b[k][1:]) & set(nb)), k                          # 원본에 있던 빛깔은 하나도 없다
    assert not (set(b['삽입'][1:]) & set(b['결실'][1:])) and 'V' not in b['삽입'] + b['결실']
    assert len(TRAINS[4][1]) % 3 == 1 and len(TRAINS[5][1]) % 3 == 2      # 끝에 창 하나 / 둘짜리 토막
    print('ok')
