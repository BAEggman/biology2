# -*- coding: utf-8 -*-
"""도해 pc 훑기 공용 도구 — 판정표를 받아 한 번에 옮긴다.

판정 다섯 가지를 그대로 표현한다.
  DEMOTE  ① 같은 판의 행으로 내림      (바늘, [카드])
  MOVE    ⑤ 다른 판의 행으로 옮김      (판, 바늘, [카드])  ← 배열이 아니라 이사다
  NEWROW  ④ 그림엔 있는데 행이 없던 것  (소품, 사실, [카드])
  DROP    ③ 폐기                        [카드]  (근거는 baseline.pmapRemoved 에 따로 적는다)

★ 바늘 함정 — 「순환적 경로」는 「비순환적 경로」 안에 통째로 들어 있다.
   겹치면 행 여는 [ 부터 잡는다:  '["순환적 경로"'
★ 바늘은 반드시 f:[ 뒤에서 찾는다 — bx 산문과 SVG 글자에 같은 말이 있다.

쓰는 법: 이 파일을 import 해서 sweep(pid, DEMOTE=…, MOVE=…, NEWROW=…, DROP=…) 를 부른다.
"""
import os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SK = os.path.join(ROOT, 'sketchy.html')


def close_brace(t, i):
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


def q2(s):
    assert '"' not in s and '\\' not in s, s
    return '"%s"' % s


def _panel(src, pid):
    i = src.index("{id:'%s'" % pid)
    return i, close_brace(src, i)


def _add_to_row(blk, needle, cards):
    """판 블록 안에서 바늘이 든 행에 카드를 덧붙인다."""
    fi = blk.index('f:[')
    n = blk.count(needle, fi)
    assert n == 1, '바늘이 %d번 (1 기대): %s' % (n, needle)
    k = blk.index(needle, fi)
    a = k if blk[k] == '[' else blk.rindex('[', fi, k)
    b = close_brace(blk, a)
    row = blk[a:b + 1]
    # ⚠ 사실표의 행은 큰따옴표로 쓴 것도 있고 **작은따옴표**로 쓴 것도 있다
    #    (s34p05·s34p06 이 그렇다). 여는 따옴표를 보고 맞춘다.
    qc = row[1]
    assert qc in '"\'', '행이 따옴표로 시작하지 않는다: ' + row[:40]

    def _endq(t, i):                      # i = 여는 따옴표 자리, 닫는 따옴표 자리를 준다
        k = i + 1
        while k < len(t):
            if t[k] == '\\': k += 2; continue
            if t[k] == qc: return k
            k += 1
        raise AssertionError('닫는 따옴표를 못 찾음')

    p1 = 1; p2 = _endq(row, p1)
    f1 = row.index(qc, p2 + 1); f2 = _endq(row, f1)
    rest = row[f2 + 1:-1].strip()
    old = [x.strip().strip('"') for x in rest.strip(',').strip('[]').split(',') if x.strip()]
    for c in cards:
        assert c not in old, '%s 가 그 행에 이미 있다' % c
        assert '"%s"' % c not in blk, '%s 가 그 판의 다른 행에 이미 있다' % c
    new = ('[' + row[p1:p2 + 1] + ',' + row[f1:f2 + 1] + ','
           + '[' + ','.join('"%s"' % c for c in old + list(cards)) + ']]')
    return blk[:a] + new + blk[b + 1:]


def sweep(pid, DEMOTE=(), MOVE=(), NEWROW=(), DROP=()):
    src = open(SK, encoding='utf-8').read()
    i, e = _panel(src, pid)
    blk = src[i:e + 1]

    m = re.search(r"pc:\[([^\]]*)\]", blk)
    assert m, pid + ' 에 pc 가 없다'
    pcs = [x.strip().strip('"') for x in m.group(1).split(',') if x.strip()]
    planned = set(DROP)
    for _, cs in DEMOTE: planned |= set(cs)
    for _, _, cs in MOVE: planned |= set(cs)
    for _, _, cs in NEWROW: planned |= set(cs)
    assert set(pcs) == planned, ('판정 안 한 것 %s · pc 에 없는 것 %s'
                                 % (sorted(set(pcs) - planned), sorted(planned - set(pcs))))

    # ⚠ pc 를 먼저 지운다. 안 그러면 「그 판의 다른 행에 이미 있다」 검사가
    #    아직 남아 있는 pc 목록을 보고 잘못 걸린다.
    blk = re.sub(r"pc:\[[^\]]*\],", '', blk, count=1)

    for needle, cards in DEMOTE:
        blk = _add_to_row(blk, needle, cards)
    for prop, fact, cards in NEWROW:
        fi = blk.index('f:[')
        fe = close_brace(blk, fi + 2)
        row = '[' + q2(prop) + ',' + q2(fact) + ',[' + ','.join(q2(c) for c in cards) + ']]'
        blk = blk[:fe] + ',\n     ' + row + blk[fe:]

    out = src[:i] + blk + src[e + 1:]

    # ⑤ 다른 판으로 이사 — pc 를 지운 뒤라야 중복 검사가 통한다
    for tgt, needle, cards in MOVE:
        ti, te = _panel(out, tgt)
        tb = _add_to_row(out[ti:te + 1], needle, cards)
        out = out[:ti] + tb + out[te + 1:]

    b2 = out[out.index("{id:'%s'" % pid):]
    b2 = b2[:close_brace(b2, 0) + 1]
    cs = re.findall(r'"([A-Z]\d?[A-Z0-9]*(?:-[A-Z0-9]+)*-[\w#]+)"', b2)
    dup = sorted({c for c in cs if cs.count(c) > 1})
    # ⚠ 원래부터 한 카드가 두 행에 걸친 판이 있다 (s04p01·d02p03·s22p01·s34p01·s34p02·s20p03).
    #    d02p03 의 Q1-16 은 「1차 정지」와 「2차 정지」 두 행에 일부러 걸려 있다 —
    #    「두 번 멈춘다」가 두 행에 나뉘어 있기 때문이다. 그런 것까지 잡으면 안 된다.
    #    내가 이번에 얹은 것 때문에 생긴 중복만 잡는다.
    added = set(DROP)
    for _, c in DEMOTE: added |= set(c)
    for _, _, c in NEWROW: added |= set(c)
    bad = sorted(d for d in dup if d in added)
    assert not bad, '카드 중복(이번에 얹은 것): ' + str(bad)
    if dup: print('  (원래부터 두 행에 걸친 카드: %s)' % ' '.join(dup))

    open(SK, 'w', encoding='utf-8').write(out)
    print('%s  pc %d → 0 · 내림 %d · 이사 %d · 새 행 %d개(%d장) · 폐기 %d · 이 판 %d장'
          % (pid, len(pcs),
             sum(len(c) for _, c in DEMOTE),
             sum(len(c) for _, _, c in MOVE),
             len(NEWROW), sum(len(c) for _, _, c in NEWROW),
             len(DROP), len(cs)))
