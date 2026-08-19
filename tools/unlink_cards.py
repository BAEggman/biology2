#!/usr/bin/env python3
"""사실표 행에서 카드를 **떼는** 공용 도구.

「그린 것만 건다」를 어긴 행을 되돌릴 때 쓴다. link_cards.py의 반대다.

    from unlink_cards import unlink
    unlink([('s35p02', '거의 다 흰 구슬', ['J1-19','J1-19#1','J1-19#3'])])
"""
import os, re, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from link_cards import _block, _rows, SK, CARD_RE


def unlink(spec, quiet=False):
    src = open(SK, encoding='utf-8').read()
    removed = 0
    for pid, needle, cards in spec:
        i, j = _block(src, pid)
        blk = src[i:j]
        hits = [(a, b) for a, b in _rows(blk) if needle in blk[a:b]]
        if len(hits) != 1:
            print('✗ %s 에서 「%s」 가 %d행에 맞는다' % (pid, needle[:34], len(hits))); return 1
        a, b = hits[0]
        row = blk[a:b]
        have = re.findall(CARD_RE, row)
        miss = [c for c in cards if c not in have]
        if miss:
            print('✗ %s 행에 없는 카드: %s' % (pid, miss)); return 1
        keep = [c for c in have if c not in cards]
        if keep:
            new_arr = ',[' + ','.join('"%s"' % c for c in keep) + ']]'
        else:
            new_arr = ']'
        row = re.sub(r',\["[A-Z][^\[\]]*"\]\]$', new_arr, row)
        assert re.findall(CARD_RE, row) == keep, row[-160:]
        removed += len(cards)
        blk = blk[:a] + row + blk[b:]
        src = src[:i] + blk + src[j:]
        if not quiet:
            print('  %-8s ✂ %d장 뗌 → 남은 %d장  「%s」'
                  % (pid, len(cards), len(keep), needle[:28]))
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
    if r.returncode: return 1
    print('★ 모두 %d장 뗌' % removed)
    return 0


if __name__ == '__main__':
    print(__doc__)
