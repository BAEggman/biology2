# -*- coding: utf-8 -*-
"""면제 재검토 — 면제 라벨이 어느 판의 사실 칸에 쓰이는지, 그 판에 그림이 있는지, 후크가 설 자리가 있는지."""
import sys, io, os, json, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rowlib import get_rows, panel_span

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
s = io.open(os.path.join(ROOT,'sketchy.html'), encoding='utf-8').read()
h = json.load(open(os.path.join(ROOT,'tools/hooks.json'), encoding='utf-8'))
strip = lambda t: re.sub(r'<[^>]+>','',t)

# 판 목록
pids = re.findall(r"\{id:'([sd]\d+p\d+[a-z]?)'", s)
PANEL = {}
for pid in pids:
    try: rows = get_rows(s, pid)
    except Exception: continue
    props, facts = [], []
    for r in rows:
        try: a = json.loads(r)
        except Exception: continue
        props.append(strip(a[0])); facts.append(strip(a[1]))
    i,j = panel_span(s,pid); blk = s[i:j+1]
    svgt = ' '.join(re.sub(r'<[^>]+>','',t) for t in re.findall(r'<text\b[^>]*>([\s\S]*?)</text>', blk))
    PANEL[pid] = {'props':' | '.join(props), 'facts':' | '.join(facts), 'svg':svgt,
                  'img': os.path.exists(os.path.join(ROOT,'img',pid+'.webp')) or ('svg:`' in blk)}

def where(label):
    out=[]
    for pid,d in PANEL.items():
        if label in d['facts']: out.append(pid)
    return out

which = sys.argv[1] if len(sys.argv)>1 else '_뜻이있는약어'
v = h[which]; lst = v.get('목록', v) if isinstance(v,dict) else v
H = h['hooks']
rows=[]
for label in lst:
    ps = where(label)
    rows.append((len(ps), label, ps))
rows.sort(key=lambda x:(-x[0], x[1]))
for n,label,ps in rows:
    mark = '★후크있음' if label in H else ''
    print('%-22s 사실칸 %d판 %s %s' % (label, n, ','.join(ps[:5]) + (' …' if len(ps)>5 else ''), mark))
