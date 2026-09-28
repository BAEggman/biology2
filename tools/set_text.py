#!/usr/bin/env python3
"""set_text.py — 판의 br/bx 안에서 정확히 한 번 나오는 글을 바꾼다.
사용: python3 tools/set_text.py <edits.json> [--check]
  edits.json: [{"pid":"s18p01","old":"...","new":"..."}, ...]
범위는 {id:'pid' 부터 그 판의 f:[ 앞까지(t·br·bx). 0번이나 2번 이상 나오면 중단."""
import json, sys
SK='sketchy.html'
def die(m): print('❌ 중단 —', m); sys.exit(1)
edits=json.load(open(sys.argv[1],encoding='utf8')); CHECK='--check' in sys.argv
s=open(SK,encoding='utf8').read()
for ed in edits:
    pid=ed['pid']; i=s.find("{id:'%s'"%pid)
    if i<0: die('판 없음 '+pid)
    j=s.find('f:[',i); seg=s[i:j]; c=seg.count(ed['old'])
    if c!=1: die('%s 에서 %d번 나온다: %s'%(pid,c,ed['old'][:60]))
    s=s[:i]+seg.replace(ed['old'],ed['new'])+s[j:]
    print('✔',pid,'|',ed['old'][:50],'→',ed['new'][:60])
if CHECK: print('— 검사만'); sys.exit(0)
open(SK,'w',encoding='utf8').write(s); print('저장했다')
