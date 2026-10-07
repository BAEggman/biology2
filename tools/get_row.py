#!/usr/bin/env python3
"""get_row.py — 사실표 행의 원문(태그 포함)을 그대로 찍는다. 사용: python3 tools/get_row.py s19p02g:2 s20p07:8 ..."""
import json, sys
sys.path.insert(0,'tools')
SK='sketchy.html'
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
    raise SystemExit('괄호가 안 맞는다 @%d'%st)
def rows_spans(src, fst):
    en=match(src, fst); spans=[]; k=fst+1
    while k<en:
        c=src[k]
        if c=='[':
            e=match(src,k); spans.append((k,e)); k=e+1
        else: k+=1
    return spans
s=open(SK,encoding='utf8').read()
for a in sys.argv[1:]:
    pid,n=a.split(':'); n=int(n)
    i=s.find("{id:'%s'"%pid); fi=s.find('f:[',i); sp=rows_spans(s, fi+2)
    a0,b0=sp[n-1]
    try: row=json.loads(s[a0:b0+1])
    except Exception as e: row=[s[a0:b0+1],'(JSON 아님 — 작은따옴표 행)']
    print('%s #%d\n  P: %s\n  F: %s'%(pid,n,row[0],row[1][:160]))
