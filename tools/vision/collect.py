#!/usr/bin/env python3
"""tools/vision/out/*.txt 를 모아 판정 집계와 고칠것 큐를 만든다.
쓰는 법: python3 tools/vision/collect.py  → outputs/그림감사_<날짜>.md + tools/vision/verdicts.json"""
import os,re,json,glob,collections,datetime
R=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
m={x['pid']:x for x in json.load(open(os.path.join(R,'tools/blind/manifest.json'),encoding='utf-8'))}
pat=re.compile(r'^(\S+)\s+(\d+)\s+(OK|F1|F2|F3)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*$')
V=[];bad=[]
for f in sorted(glob.glob(os.path.join(R,'tools/vision/out/*.txt'))):
    for ln in open(f,encoding='utf-8'):
        ln=ln.strip()
        if not ln or ln.startswith('#') or ln.startswith('끝'): continue
        g=pat.match(ln)
        if not g: bad.append((os.path.basename(f),ln)); continue
        pid,n,v,why,ph=g.groups(); n=int(n)
        row=next((r for r in m.get(pid,{}).get('rows',[]) if r['n']==n),None)
        V.append({'pid':pid,'n':n,'v':v,'why':why,'ph':ph if ph!='-' else '','cards':row['cards'] if row else 0,
                  'prop':row['prop'] if row else '','label':row.get('label','') if row else ''})
json.dump(V,open(os.path.join(R,'tools/vision/verdicts.json'),'w',encoding='utf-8'),ensure_ascii=False,indent=0)
c=collections.Counter(x['v'] for x in V); ph=[x for x in V if x['ph']]
pids=set(x['pid'] for x in V)
L=['# 그림 인출력 감사 — %s'%datetime.date.today(),'',
   '판 %d / 192 · 행 %d · OK %d · F1 %d · F2 %d · F3 %d · 음차없음 %d · 형식 안 맞는 줄 %d'%(len(pids),len(V),c['OK'],c['F1'],c['F2'],c['F3'],len(ph),len(bad)),'']
def sec(t,rows):
    L.append('## %s (%d)'%(t,len(rows))); L.append('| 판 | 행 | 카드 | 소품 | 인출 대상 | 근거 |'); L.append('|---|---|---|---|---|---|')
    for x in sorted(rows,key=lambda x:-x['cards']): L.append('| %s | %d | %d | %s | %s | %s |'%(x['pid'],x['n'],x['cards'],x['prop'][:60],x['label'][:40],x['why']))
    L.append('')
sec('F1 — 소품 칸이 말하는 것이 그림에 없다 (글이 거짓말한다 · 가장 급함)',[x for x in V if x['v']=='F1'])
sec('F2 — 물건은 있는데 고리가 없다 (딱지)',[x for x in V if x['v']=='F2'])
sec('F3 — 딴 판과 부딪히거나 반대로 그려졌다',[x for x in V if x['v']=='F3'])
L.append('## 음차없음 (%d)'%len(ph)); L.append('| 판 | 행 | 카드 | 이름 |'); L.append('|---|---|---|---|')
for x in sorted(ph,key=lambda x:-x['cards']): L.append('| %s | %d | %d | %s |'%(x['pid'],x['n'],x['cards'],x['ph']))
if bad: L.append(''); L.append('## 형식 안 맞는 줄'); L+=['- %s: %s'%b for b in bad]
os.makedirs(os.path.join(R,'outputs'),exist_ok=True)
p=os.path.join(R,'outputs','그림감사_%s.md'%datetime.date.today()); open(p,'w',encoding='utf-8').write('\n'.join(L)); print(p); print(L[2])
