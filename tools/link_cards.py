#!/usr/bin/env python3
"""사실표 행에 카드를 다는 공용 도구.

손으로 앵커 문자열을 베끼는 대신 **소품 조각으로 행을 찾아** 카드를 덧붙인다.
앵커 오타로 죽는 일이 없고, 한 번에 여러 패널을 다룰 수 있다.

    from link_cards import link
    link([
      ('d05p01', '두 원이 같은 막대 위에', ['D1-93'], '덧붙일 사실 문장(없으면 빈 문자열)'),
      ...
    ])

안전장치
  · 소품 조각이 그 패널에서 정확히 한 행에만 맞아야 한다(0개·2개 이상이면 중단)
  · 카드 ID가 index.html의 CARDS에 실재해야 한다
  · 같은 패널 안에서 카드가 겹치면 중단
  · 쓰기 전에 DATA 배열을 다시 파싱해 문법이 살아 있는지 확인한다
"""
import json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SK = os.path.join(ROOT, 'sketchy.html')
IDX = os.path.join(ROOT, 'index.html')

CARD_RE = r'"([A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-[\w#]+)"'


def _block(s, pid):
    i = s.index("{id:'%s'" % pid)
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
            if d == 0: return i, k + 1
        k += 1
    raise SystemExit('%s 블록이 안 닫힌다' % pid)


def _rows(blk):
    """사실표의 각 행 [start, end) 위치를 돌려준다."""
    fi = blk.index(',f:[')
    out, d, q, st, k, esc = [], 0, None, None, fi + 3, False
    while k < len(blk):
        c = blk[k]
        if q:
            if esc: esc = False
            elif c == '\\': esc = True
            elif c == q: q = None
        elif c in '"\'`':
            q = c
        elif c == '[':
            d += 1
            if d == 2: st = k
        elif c == ']':
            d -= 1
            if d == 1 and st is not None:
                out.append((st, k + 1)); st = None
            elif d == 0:
                break
        k += 1
    return out


def _endq(s, i):
    """s[i]가 여는 따옴표일 때 닫는 따옴표의 위치를 돌려준다."""
    assert s[i] == '"', s[i:i + 20]
    k, esc = i + 1, False
    while k < len(s):
        if esc: esc = False
        elif s[k] == '\\': esc = True
        elif s[k] == '"': return k
        k += 1
    raise SystemExit('따옴표가 안 닫힌다')


def link(spec, quiet=False):
    src = open(SK, encoding='utf-8').read()
    cards_all = {c['id'] for c in json.loads(
        re.search(r'<script id="CARDS"[^>]*>([\s\S]*?)</script>',
                  open(IDX, encoding='utf-8').read()).group(1))}
    added = 0
    for pid, needle, cards, extra in spec:
        for c in cards:
            if c not in cards_all:
                print('✗ 없는 카드 ID: %s' % c); return 1
        i, j = _block(src, pid)
        blk = src[i:j]
        hits = [(a, b) for a, b in _rows(blk) if needle in blk[a:b]]
        if len(hits) != 1:
            print('✗ %s 에서 「%s」 가 %d행에 맞는다' % (pid, needle[:34], len(hits)))
            return 1
        a, b = hits[0]
        row = blk[a:b]
        have = re.findall(CARD_RE, row)
        new = [c for c in cards if c not in have]
        if extra:
            # 둘째 칸(사실)의 닫는 따옴표 바로 앞에 문장을 덧붙인다
            p = _endq(row, _endq(row, row.index('"')) + 2)   # 소품 닫음 → , → 사실 열음
            row = row[:p] + extra + row[p:]
        if new:
            if re.search(r',\["[A-Z][^\[\]]*"\]\]$', row):      # 이미 카드 배열이 있다
                row = row[:-2] + ',' + ','.join('"%s"' % c for c in new) + ']]'
            else:                                              # 카드 배열이 없다
                row = row[:-1] + ',[' + ','.join('"%s"' % c for c in new) + ']]'
            added += len(new)
        blk = blk[:a] + row + blk[b:]
        ids = re.findall(CARD_RE, blk)
        dup = [x for x in set(ids) if ids.count(x) > 1]
        if dup:
            print('✗ %s 카드 중복: %s' % (pid, dup)); return 1
        src = src[:i] + blk + src[j:]
        if not quiet:
            print('  %-8s ← %-2d장  「%s」' % (pid, len(new), needle[:30]))
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
    if r.returncode:
        return 1
    print('★ 모두 %d장 추가' % added)
    return 0


if __name__ == '__main__':
    print(__doc__)
