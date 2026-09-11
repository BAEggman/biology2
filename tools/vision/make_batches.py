#!/usr/bin/env python3
"""그림 인출력 감사 — 묶음 파일 만들기.
manifest.json(그림 있는 192판 · label=짧은 사실)에서 판당 소품·짧은사실·긴사실을 뽑아
6판씩 묶음 파일을 만든다. 그림 경로는 저장소 안(tools/blind/png)이라 컨테이너가 바뀌어도 산다.
쓰는 법:  python3 tools/vision/make_batches.py   → tools/vision/batches/bNN.md
"""
import json, os, sys
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
m=json.load(open(os.path.join(R,'tools/blind/manifest.json'),encoding='utf-8'))
N=int(sys.argv[1]) if len(sys.argv)>1 else 6
out=os.path.join(R,'tools/vision/batches'); os.makedirs(out,exist_ok=True)
for f in os.listdir(out): os.remove(os.path.join(out,f))
panels=[x for x in m if os.path.exists(os.path.join(R,'tools/blind/png',x['pid']+'.png'))]
for bi,i in enumerate(range(0,len(panels),N),1):
    L=['# 묶음 b%02d — 판 %d개\n'%(bi,len(panels[i:i+N]))]
    for x in panels[i:i+N]:
        L.append('## %s\n그림: tools/blind/png/%s.png\n'%(x['pid'],x['pid']))
        for r in x['rows']:
            L.append('  %d행\n    소품: %s\n    짧은사실(인출 대상): %s\n'%(r['n'],r['prop'],r.get('label') or r['fact']))
        L.append('')
    open(os.path.join(out,'b%02d.md'%bi),'w',encoding='utf-8').write('\n'.join(L))
print('판 %d · 묶음 %d (판당 %d)'%(len(panels),(len(panels)+N-1)//N,N))
