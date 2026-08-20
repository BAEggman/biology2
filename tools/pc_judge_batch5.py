#!/usr/bin/env python3
"""pc 접지 감사 5차 — 3장짜리 여덟 패널 (후보 24장).

s02p04 · s04p01 · s07p02 · s09p02 · s16p02b · s17p01 · s20p01a · d02p03
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pc_demote import demote
from link_cards import link

def _close(t, i):
    op = t[i]; cl = {'{': '}', '[': ']'}[op]
    d, q, j, esc = 0, None, i, False
    while j < len(t):
        c = t[j]
        if q:
            if esc: esc = False
            elif c == '\\': esc = True
            elif c == q: q = None
        elif c in '"\'`': q = c
        elif c == op: d += 1
        elif c == cl:
            d -= 1
            if d == 0: return j
        j += 1
    raise SystemExit('괄호 안 닫힘')


def link_one(pid, needle, cards, extra):
    """link_cards 의 패널 전체 중복 검사를 피해 한 행에만 붙인다.
    s04p01·d02p03 처럼 원래부터 한 카드가 두 행에 걸쳐 있는 판을 위한 것이다."""
    SK = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'sketchy.html')
    s = open(SK, encoding='utf-8').read()
    i = s.index("{id:'%s'" % pid)
    pe = _close(s, i)
    blk = s[i:pe + 1]
    for c in cards:
        assert '"%s"' % c not in blk, c + ' 가 이미 그 판에 있다'
    fi = blk.index('f:[')                    # ★ bx 산문·SVG desc 에도 같은 말이 있다
    assert blk.count(needle, fi) == 1, '%s 안 f 배열에서 %d번 맞는다' % (pid, blk.count(needle, fi))
    k = blk.index(needle, fi)
    a = blk.rindex('[', fi, k)
    b = _close(blk, a)
    row = blk[a:b + 1]

    # 행을 [prop, fact, cards?] 로 쪼갠다
    p1 = 1                                   # prop 여는 따옴표
    assert row[p1] == '"'
    p2 = row.index('"', p1 + 1)              # prop 닫는 따옴표 (본문에 " 없음이 전제)
    f1 = row.index('"', p2 + 1)
    f2 = row.index('"', f1 + 1)
    prop = row[p1:p2 + 1]
    fact = row[f1:f2 + 1]
    rest = row[f2 + 1:-1].strip()            # ',[ ... ]' 또는 ''
    old = []
    if rest.startswith(','):
        old = [x.strip().strip('"') for x in rest.strip(',').strip('[]').split(',') if x.strip()]
    if extra:
        fact = fact[:-1] + ' ' + extra + '"'
    ids = old + list(cards)
    new_row = '[' + prop + ',' + fact + ',[' + ','.join('"%s"' % c for c in ids) + ']]'
    blk = blk[:a] + new_row + blk[b + 1:]
    out = s[:i] + blk + s[pe + 1:]
    open(SK, 'w', encoding='utf-8').write(out)
    print('  %-8s \u2190 %d \uc7a5  \u300c%s\u300d (\uc9c1\uc811)' % (pid, len(cards), needle))


DEMOTE = {
    's02p04': ['I0-56', 'I0-58#2'],
    's04p01': ['N0-23'],
    's07p02': ['G0-155'],
    's09p02': ['I1-16', 'I1-18', 'I1-19'],
    's17p01': ['H1-54'],
    'd02p03': ['X-AN-23'],
}

LINK = [
    ('s02p04', '저울', ['I0-56'],
     'HIV가 <b>CD4⁺</b> 쪽만 깨뜨리기 때문이다 — 한쪽 접시만 가벼워지니 저울이 뒤집힌다'),

    ('s02p04', '금색 자물쇠', ['I0-58#2'],
     '★ 자물쇠가 <b>가위를 잠근다</b> — 프로테아제 억제제는 <b>조립 효소</b>를 막는다. '
     '띠를 못 자르니 인형이 안 만들어진다'),

    ('s07p02', '달걀 둘', ['G0-155'],
     '둘 다 <b>생식샘</b>을 향해 지시가 내려간다 — 표적이 곧 이름이다(gonado-tropin)'),

    ('s09p02', '자라는 배지', ['I1-16'],
     '외래 DNA를 <b>벡터의 유전자 안에 끼워 망가뜨리는 것</b>이 삽입 불활성화다. '
     '망가진 쪽이 어느 배지에서 못 자라는지로 재조합체를 고른다'),

    ('s09p02', '바닥에 흩어진 중간 조각', ['I1-18'],
     '세균에는 <b>스플라이싱 기구가 없어</b> 인트론을 못 자른다 — '
     '그래서 이미 잘린 성숙 mRNA를 역전사한 <b>cDNA</b>라야 한다'),

    ('s09p02', '앞끝에 꽂은 깃발', ['I1-19'],
     'cDNA만으로는 세균이 <b>읽기 시작할 자리</b>를 못 찾는다 — '
     '세균이 알아보는 프로모터와 리보솜 결합부위를 갖춘 <b>발현 벡터</b>가 있어야 한다'),

    ('s17p01', '짐이 더 실리는 배', ['H1-54'],
     '<b>여과된 데다 더 실린다</b>(분비) — 한 번 지나가면 거의 다 빠지므로 '
     '들어온 혈장의 양을 그대로 잰다'),

]

DROP = {
    's02p04': {
        'I0-59': '「칵테일 = 뉴클레오시드 유사체 2종 + 프로테아제 억제제」인데 그림에는 자물쇠 하나뿐이다. '
                 '역전사 자리에 가짜 벽돌 둘을 놓아야 셋이 찬다.',
    },
    's04p01': {
        'S-AN-1': '「기저 3분기: 해면 → 자포 → 좌우대칭」인데 그림은 한 구역을 나란히 늘어놓았을 뿐 '
                  '갈라진 순서가 없다. 계통수 가지로 그려야 순서가 생긴다.',
        'S-AN-9': '「편형=불꽃세포 / 환형·연체=후신관」인데 불꽃은 이 판, 후신관(깔때기 배수구)은 s04p03이다. '
                  '두 판에 흩어져 한 화면에 없다 — 목록 카드.',
    },
    's07p02': {
        'G0-211': '「GH의 대사 효과 — 지방 이화·단백질 동화·혈당↑」가 그림에 없다. '
                  '그림의 GH는 간을 거쳐 뼈를 키우는 쪽만 그려져 있다.',
        'Q0-29': '「수질=신경 즉각 / 피질=ACTH」인데 s07p04 에도 피질 세 층뿐이고 수질이 안 그려져 있다. '
                 '부신 속에 곧은 전선 하나가 곧장 꽂히게 그리면(신경=즉각) 대비가 선다.',
    },
    's16p02b': {
        'G0-184': '「2차 전달자 5종」이 세 판에 흩어져 있다 — cAMP는 s16p02, IP₃·DAG·Ca²⁺는 이 판, '
                  'cGMP는 s15p01·s15p02(시각)다. 다섯을 한 화면에 놓은 종합 도해라야 걸린다 — 목록 카드.',
        'S-SG-5': '「생성 효소 셋」 중 PLC만 이 판에 있고 아데닐산 고리화효소는 s16p02, '
                  '구아닐산 고리화효소는 어디에도 없다.',
        'S-SG-6': '「표적 넷」이 PKC(이 판) · ER Ca²⁺ 방출(이 판) · PKA(s16p02) · 칼모듈린(s08p03)으로 '
                  '세 판에 흩어져 있다 — 목록 카드.',
    },
    's17p01': {
        'S-RN-10': '「분절별 물 투과성 지도」는 근위(이 판) · 하행각/상행각(s17p02) · 집합관(s17p03)에 '
                   '흩어져 있다. 한 화면에 콩팥 단면을 세로로 세워야 지도가 된다 — 목록 카드.',
        'X-RN-28': '「이눌린·크레아티닌 → GFR / PAH → 신혈장유량」인데 크레아티닌 배가 없다. '
                   '그냥 지나가는 배를 나란히 두 척으로 그리면 산다 — 작은 고침 하나로 되살아난다.',
    },
    's20p01a': {
        'P1-3': '「옥신의 생산 부위와 기능」 중 굴광성·굴중성이 덱 어디에도 없고 생산 부위 표시도 없다. '
                '한쪽에서만 빛이 드는 창과 기울어진 화분을 그려야 굴성이 생긴다.',
        'P1-3#2': '같은 이유 — 신장과 정단우성은 그려져 있으나 굴광성·굴중성이 없다.',
        'S-PL-14': '「촉진 넷 / 억제·노화 둘」인데 이 판에는 촉진 셋만 있고 브라시노스테로이드·ABA·에틸렌이 '
                   '없다(억제 쪽은 s20p01b). 여섯을 두 줄로 세운 한 화면이라야 걸린다 — 목록 카드.',
    },
    'd02p03': {
        'D1-96': '「완전연관 / 불완전연관」은 연관 이야기인데 이 판은 정자·난자 형성이다. '
                 '교차는 d05p01(상인과 상반)에 있으니, 거기에 교차가 아예 없는 칸을 하나 더 그려 '
                 '완전연관과 짝지어야 한다.',
        'D1-96#2': '같은 이유 — 이 판에는 교차도 연관도 그려져 있지 않다.',
    },
}


def main():
    for pid, ids in DEMOTE.items():
        if demote(pid, set(ids)): return 1
    for pid, d in DROP.items():
        if demote(pid, set(d)): return 1
    if link(LINK): return 1
    link_one('s04p01', '노천 정수장', ['N0-23'],
             '벽도 지붕도 없다는 것이 <b>진정한 조직이 없다</b>는 뜻이다 — '
             '동물 중에서 가장 밑에서 갈라진 무리다')
    link_one('d02p03', 'LH 급증', ['X-AN-23'],
             '<b>양성 피드백</b>이다 — 에스트로겐이 높을수록 LH를 더 밀어 올린다')
    n_link = sum(len(v) for v in DEMOTE.values())
    n_drop = sum(len(v) for v in DROP.values())
    print('\n판정 — 내림 %d장 · 폐기 %d장 (합 %d장)' % (n_link, n_drop, n_link + n_drop))
    return 0


if __name__ == '__main__':
    sys.exit(main())
