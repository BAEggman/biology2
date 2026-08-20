#!/usr/bin/env python3
"""사실표의 소품·사실 문구를 통째로 바꾸는 공용 도구 (카드는 안 건드린다).

    from hookedit import swap
    swap([('s34p01', '옛 소품 조각', '새 소품 문장', '덧붙일 사실 문장 또는 None'), ...])

· 조각이 그 패널에서 정확히 한 행에만 맞아야 한다
· 카드 배열은 손대지 않는다
· 쓰기 전에 DATA를 다시 파싱한다
"""
import os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from link_cards import _block, _rows, _endq, SK, CARD_RE


def swap(spec, quiet=False):
    src = open(SK, encoding='utf-8').read()
    for pid, needle, new_prop, add_fact in spec:
        i, j = _block(src, pid)
        blk = src[i:j]
        hits = [(a, b) for a, b in _rows(blk) if needle in blk[a:b]]
        if len(hits) != 1:
            print('✗ %s 에서 「%s」 가 %d행에 맞는다' % (pid, needle[:34], len(hits))); return 1
        a, b = hits[0]
        row = blk[a:b]
        cards_before = re.findall(CARD_RE, row)
        p0 = row.index('"'); p1 = _endq(row, p0)          # 소품 칸
        if new_prop is not None:
            assert '"' not in new_prop, new_prop
            row = row[:p0 + 1] + new_prop + row[p1:]
        if add_fact:
            assert '"' not in add_fact, add_fact
            q0 = _endq(row, row.index('"')) + 2           # 사실 칸 여는 따옴표
            q1 = _endq(row, q0)
            row = row[:q1] + add_fact + row[q1:]
        assert re.findall(CARD_RE, row) == cards_before, '카드가 바뀌었다'
        blk = blk[:a] + row + blk[b:]
        src = src[:i] + blk + src[j:]
        if not quiet:
            print('  %-8s ✎ 「%s」' % (pid, (new_prop or needle)[:44]))
    open(SK, 'w', encoding='utf-8').write(src)
    r = subprocess.run(['node', '-e',
        "const fs=require('fs');const s=fs.readFileSync('%s','utf8');"
        "const i=s.indexOf('[',s.indexOf('const DATA'));"
        "let d=0,q=null,e=false,end=0;"
        "for(let k=i;k<s.length;k++){const c=s[k];"
        "if(q){if(e){e=false;continue}if(c==='\\\\'){e=true;continue}"
        "if(c===q)q=null;continue}"
        "if(c==='\"'||c===\"'\"||c==='`'){q=c;continue}"
        "if(c==='[')d++;else if(c===']'){d--;if(!d){end=k+1;break}}}"
        "eval('('+s.slice(i,end)+')');console.log('DATA 재파싱 OK')" % SK],
        capture_output=True, text=True)
    print(r.stdout.strip() or r.stderr.strip()[:300])
    return r.returncode


if __name__ == '__main__':
    print(__doc__)
