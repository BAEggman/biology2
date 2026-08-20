#!/usr/bin/env python3
"""pc(패널 단위) 카드를 빼서 행 단위로 내린다 — 대응 소품을 증거로 남기려고.

    from pc_demote import demote
    demote('s17p02', {'H1-100','H1-81'})   # pc에서만 뺀다. link는 따로 부른다.

pc는 증거가 없다. 그림에 그 소품이 있다면 행으로 내려야 「무엇을 보고 걸었는지」가 남는다.
"""
import os, re, sys
SK = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'sketchy.html')


def demote(pid, drop, quiet=False):
    s = open(SK, encoding='utf-8').read()
    i = s.index("{id:'%s'" % pid)
    m = re.search(r'pc:\[(.*?)\]', s[i:i + 6000])
    if not m:
        print('✗ %s 에 pc가 없다' % pid); return 1
    ids = [x.strip().strip('"') for x in m.group(1).split(',') if x.strip()]
    miss = [c for c in drop if c not in ids]
    if miss:
        print('✗ %s pc에 없는 카드: %s' % (pid, miss)); return 1
    keep = [x for x in ids if x not in drop]
    new = 'pc:[' + ','.join('"%s"' % x for x in keep) + ']' if keep else ''
    body = s[i:].replace(m.group(0) + (',' if not keep else ''), new + ('' if not keep else ''), 1)
    open(SK, 'w', encoding='utf-8').write(s[:i] + body)
    if not quiet:
        print('  %-8s pc에서 %d장 뺌 (남은 pc %d장)' % (pid, len(drop), len(keep)))
    return 0


if __name__ == '__main__':
    print(__doc__)
