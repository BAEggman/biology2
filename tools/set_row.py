#!/usr/bin/env python3
"""set_row.py — 사실표 한 행의 소품·사실 칸을 바꾸고 blind/manifest.json 도 맞춘다.
사용: python3 tools/set_row.py <edits.json> [--check]
  edits.json: [{"pid":"s18p01","n":6,"prop":"...","fact":"..."}, ...]
  prop/fact 중 하나만 줘도 된다. 카드 목록(셋째 원소)은 절대 건드리지 않는다.
  부분 고침: "prop_replace":[["옛 글","새 글"],...] · "fact_replace":[...] — 옛 글은 태그 포함 원문에서 정확히 한 번 나와야 한다.
안전장치: 행 번호가 없거나, 행이 JSON 으로 안 읽히면 중단. 저장은 맨 끝에 한 번."""
import json, re, sys
SK='sketchy.html'; MF='tools/blind/manifest.json'
def die(m): print('❌ 중단 —', m); sys.exit(1)
def match(src, st):
    op=src[st]; cl={'[':']','{':'}'}[op]; d=0; q=None; esc=False
    for k in range(st, len(src)):
        c=src[k]
        if q:
            if esc: esc=False; continue
            if c=='\\': esc=True; continue
            if c==q: q=None
            continue
        if c in '"\'`': q=c; continue
        if c==op: d+=1
        elif c==cl:
            d-=1
            if d==0: return k
    die('괄호가 안 맞는다 @%d'%st)
def rows_spans(src, fst):
    # fst = index of '[' of f:[ ; returns list of (start,end) of each row array
    en=match(src, fst); spans=[]; k=fst+1
    while k<en:
        c=src[k]
        if c=='[':
            e=match(src,k); spans.append((k,e)); k=e+1
        else: k+=1
    return spans
strip=lambda x: re.sub(r'<[^>]+>','',x)
edits=json.load(open(sys.argv[1],encoding='utf8')); CHECK='--check' in sys.argv
s=open(SK,encoding='utf8').read(); m=json.load(open(MF,encoding='utf8'))
for ed in edits:
    pid=ed['pid']; n=ed['n']
    i=s.find("{id:'%s'"%pid)
    if i<0: die('판 없음 '+pid)
    pe=match(s,i); fi=s.find('f:[',i)
    if fi<0 or fi>pe: die('f 없음 '+pid)
    sp=rows_spans(s, fi+2)
    if not (1<=n<=len(sp)): die('%s 행 %d 없음 (행 %d개)'%(pid,n,len(sp)))
    a,b=sp[n-1]
    try: row=json.loads(s[a:b+1])
    except Exception as e: die('%s %d행 JSON 아님: %s'%(pid,n,e))
    old=list(row)
    if 'prop' in ed: row[0]=ed['prop']
    if 'fact' in ed: row[1]=ed['fact']
    if 'prop_append' in ed: row[0]=row[0]+ed['prop_append']
    if 'fact_append' in ed: row[1]=row[1]+ed['fact_append']
    for key,ix in (('prop_replace',0),('fact_replace',1)):
        for o,nw in ed.get(key,[]):
            c=row[ix].count(o)
            if c!=1: die('%s %d행 %s: 「%s」가 %d번 나온다 (1 기대)'%(pid,n,key,o,c))
            row[ix]=row[ix].replace(o,nw)
    new=json.dumps(row,ensure_ascii=False,separators=(',',':'))
    s=s[:a]+new+s[b+1:]
    print('✔ %s %d행\n   전 [%s] → %s\n   후 [%s] → %s'%(pid,n,strip(old[0])[:70],strip(old[1])[:90],strip(row[0])[:70],strip(row[1])[:90]))
    ent=[e for e in m if e['pid']==pid]
    if ent:
        rr=[r for r in ent[0]['rows'] if r['n']==n]
        if rr:
            rr[0]['prop']=strip(row[0]); rr[0]['fact']=strip(row[1])
        else: print('   (manifest 에 %d행 없음)'%n)
    else: print('   (manifest 에 판 없음)')
if CHECK: print('— 검사만, 저장 안 함'); sys.exit(0)
open(SK,'w',encoding='utf8').write(s)
json.dump(m,open(MF,'w',encoding='utf8'),ensure_ascii=False,indent=1)
print('저장했다')
