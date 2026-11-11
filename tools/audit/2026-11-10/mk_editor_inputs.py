import json,re,glob,collections
SP='/tmp/claude-0/-home-claude/adba3dea-fd2a-5075-a226-d8c1b6963879/scratchpad'
D=json.load(open(SP+'/audit/findings.json')); G=json.load(open(SP+'/audit/groups.json'))['T']
GPT=json.load(open(SP+'/gpt/items.json'))
done=set()
for f in glob.glob('/tmp/b2/tools/audit/2026-11-10/patch/*.json'):
    P=json.load(open(f))
    for o in P.get('ops',[])+P.get('cards',[]):
        for m in re.findall(r'T(\d+)',str(o.get('from',''))): done.add(int(m))
done|={155,157,311,316,372,374,382,413,416,435,489,516,525,538,547,10,97,117,144,217,283,95,96}
# 그림을 고칠 예정인 정거장(글을 그림에 맞추지 말 것)
PIC={'L19d':[7,12,2,6],'L34b':[11,12],'L12d':[5],'L17a':[8],'L45d':[4],'L45b':[5],'L11d':[4,6,7],'L17f':[8],'L03b':[3,4],'L19e':[4],'L04d':[4],'L04c':[8],'L16a':[3],'L03c':[6],'L38a':[10,11],'L31a':[0],'L07a':[7]}
byT=collections.defaultdict(list); byV=collections.defaultdict(list)
for d in D['T']:
    if d['_n'] in done: continue
    byT[d['lesson']].append(d)
for d in D['V']:
    if d['kind'].startswith('BOX'): continue
    byV[d['lesson']].append(d)
byG=collections.defaultdict(list)
for it in GPT:
    for m in set(re.findall(r'L\d{2}[a-z]',it.get('lesson',''))): byG[m].append(it)
tot=collections.Counter()
for g,les in G.items():
    out=[f'# 편집 묶음 {g} — 과 {", ".join(les)}','']
    for L in les:
        out.append(f'\n## {L}')
        if L in PIC: out.append(f'⚠ 이 과의 정거장 {PIC[L]} 은 **그림을 고칠 예정**이다. 그 정거장의 「그림 ↔ 글」 지적은 판정하지 말고 건너뛴다(글을 그림에 맞추지 않는다). 그 밖의 지적은 평소대로.')
        out.append('\n### 글 감사 지적(T)')
        for d in sorted(byT[L],key=lambda d:(d['stop'],d['_n'])):
            tot['T']+=1
            out.append(f"- [T{d['_n']}] 정거장 {d['stop']} · {d['kind']} · {d['sev']} · {d.get('conf','')} · 칸 {d.get('where','')}" + (f" · 카드 {d['card']}" if d.get('card') else '') + f"\n  - 구절: {d['quote']}\n  - 까닭: {d['why']}\n  - 감사원 제안: {d['fix']}")
        if not byT[L]: out.append('- (없음)')
        out.append('\n### 그림 감사 지적 가운데 상자 말고(V)')
        for d in sorted(byV[L],key=lambda d:(str(d['stop']),d['_n'])):
            tot['V']+=1
            out.append(f"- [V{d['_n']}] 정거장 {d['stop']} · 상자 {d.get('box','')} · {d['kind']} · {d['sev']}\n  - 문제: {d['what']}\n  - 감사원이 본 것: {d['seen']}\n  - 감사원 제안: {d['fix']}")
        if not byV[L]: out.append('- (없음)')
        out.append('\n### GPT 감사가 이 과에 건 기본서 대조항목(참고 — 넣을지는 지시서의 규칙대로)')
        for it in byG[L]:
            tot['G']+=1
            miss=' / '.join(x for x in it.get('rest',[]) if not re.match(r'^S\d+ ',x))
            out.append(f"- [{it['id']}] {it['head']} — {it['verdict']} · 레슨 칸: {it['lesson']}\n  - 기본서에는 있는데 과에 없다고 본 것: {miss}\n  - GPT 메모: {it.get('note','')}")
        if not byG[L]: out.append('- (없음)')
    open(f'{SP}/audit/in/E_{g}.md','w').write('\n'.join(out))
print(dict(tot),'처리된 T',len(done))
import os; print(sorted((os.path.getsize(f)//1024,os.path.basename(f)) for f in glob.glob(SP+'/audit/in/E_*.md'))[-3:])
