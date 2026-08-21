# -*- coding: utf-8 -*-
"""s20 나머지 훑기 — 이미 그려졌는데 안 걸린 행 둘.

  P1-8#1「브라시노스테로이드 → 세포 신장·분열」
     s20p01b 4행 「부목 댄 줄기가 두 배 굵음」. 사실 칸이 이미
     「줄기가 굵어진 것이 신장과 분열이 함께 일어난 결과다」라고 적고 있었다.
  P1-3#1「옥신의 생산 부위 → 줄기 끝」
     s20p05 6행 「돌판은 안 통하고 젤리는 통한다 → 내려가는 것은 화학 신호(옥신)」.
     끝에서 만들어져 아래로 내려간다는 것이 그 행의 결론 그 자체다.
     (「어린 잎」은 안 그려졌지만 급소는 「끝」이고 어린 잎은 세부다)

★ 같이 살펴보고 안 건 것 — 급소가 그림에 없다
  P1-8#2 관속 분화      물관·체관이 그 판에 없다
  P1-6#1·#3·#4         ABA의 생장 억제·종자 휴면·건조 내성. 셔터는 기공만 나른다
  P1-5                 지베렐린 셋 중 발아만 그려졌다
  P1-12#5 팽압으로 물 유입  s20p01a에는 나가는 H⁺만 있고 들어오는 물이 없다
  P1-23 생물시계 24시간   회중시계는 「시계가 있다」까지만 나른다
  P1-27 중일식물         s20p06은 단일·장일만 그렸다
  P1-22 굴촉성 · P1-33·P1-34 방어 · P1-1·P1-2 정의   덱에 그림이 없다
"""
import os
SK = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'sketchy.html')

def _close(s, i):
    o = s[i]; c = {'{': '}', '[': ']'}[o]; d = 0; q = None; e = False
    for k in range(i, len(s)):
        ch = s[k]
        if q:
            if e: e = False; continue
            if ch == '\\': e = True; continue
            if ch == q: q = None
            continue
        if ch in '"\'`': q = ch; continue
        if ch == o: d += 1
        elif ch == c:
            d -= 1
            if not d: return k
    raise AssertionError('닫는 괄호를 못 찾음')

def link_one(pid, needle, cards):
    s = open(SK, encoding='utf-8').read()
    i = s.index("{id:'%s'" % pid)
    pe = _close(s, i); blk = s[i:pe + 1]
    for c in cards:
        assert '"%s"' % c not in blk, c + ' 가 이미 그 판에 있다'
    fi = blk.index('f:[')
    assert blk.count(needle, fi) == 1, '바늘이 %d번: %s' % (blk.count(needle, fi), needle)
    k = blk.index(needle, fi); a = blk.rindex('[', fi, k); b = _close(blk, a)
    row = blk[a:b + 1]
    p1 = 1; p2 = row.index('"', p1 + 1)
    f1 = row.index('"', p2 + 1); f2 = row.index('"', f1 + 1)
    prop, fact = row[p1:p2 + 1], row[f1:f2 + 1]
    rest = row[f2 + 1:-1].strip()
    old = [x.strip().strip('"') for x in rest.strip(',').strip('[]').split(',') if x.strip()] if rest.startswith(',') else []
    new_row = '[' + prop + ',' + fact + ',[' + ','.join('"%s"' % c for c in old + list(cards)) + ']]'
    s = s[:i + a] + new_row + s[i + b + 1:]
    open(SK, 'w', encoding='utf-8').write(s)
    print('  %-8s ← %-8s (행 %d → %d장)' % (pid, ','.join(cards), len(old), len(old) + len(cards)))

link_one('s20p01b', '부목 댄 줄기가', ['P1-8#1'])   # ★ 처음 돌릴 때 여기서 적용됨
link_one('s20p05', '회색 돌판</b>을 끼웠다', ['P1-3#1'])
