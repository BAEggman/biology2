#!/usr/bin/env node
/* 미연결 카드 후보 뽑기 — 「미연결카드 훑기」 1단계 (2026-08-08 방법론).
 *   카드 ID 는 단원별로 연속이다. 어떤 판에 E1-58·E1-61 이 걸려 있으면
 *   사이의 59·60 도 같은 주제일 확률이 높다. ±GAP 안의 미연결 카드를 후보로 낸다.
 *   ★ 정밀도는 이 단계가 아니라 2단계(판정)에서 만든다. 후보의 절반 이상이 탈락하는 것이 정상이다.
 * 쓰기: node tools/link_candidates.js            → 판별 후보 수 순위
 *       node tools/link_candidates.js <패널id>   → 그 판의 행·이미 걸린 카드·후보 전체
 */
const fs=require('fs'), path=require('path');
const R=path.dirname(__dirname);
const sk=fs.readFileSync(path.join(R,'sketchy.html'),'utf8');
const i=sk.indexOf('[', sk.indexOf('const DATA'));
let d=0,q=null,e=false,end=0;
for(let k=i;k<sk.length;k++){const c=sk[k];
 if(q){if(e){e=false;continue}if(c==='\\'){e=true;continue}if(c===q)q=null;continue}
 if(c==='"'||c==="'"||c==='`'){q=c;continue}
 if(c==='[')d++;else if(c===']'){d--;if(!d){end=k+1;break}}}
const DATA=eval('('+sk.slice(i,end)+')');
const ix=fs.readFileSync(path.join(R,'index.html'),'utf8');
const CARDS=JSON.parse(ix.match(/id=["']CARDS["'][^>]*>([\s\S]*?)<\/script>/)[1]);
const PMAP=JSON.parse(ix.match(/var PMAP=(\{[\s\S]*?\});/)[1]);
const strip=x=>String(x==null?'':x).replace(/<[^>]+>/g,'');
const GAP=Number(process.env.GAP||3);

/* 카드 ID 를 접두어 + 번호로 가른다 — B1-51 → {p:'B1', n:51}, B1-51#2 → 분할본은 뺀다 */
const parsed=[];
for(const c of CARDS){
  const m=String(c.id).match(/^([A-Z]\d?[A-Z-]*)-(\d+)(#\d+)?$/);
  if(!m) continue;
  parsed.push({id:c.id, p:m[1], n:Number(m[2]), split:!!m[3], q:strip(c.q||''), a:strip(c.a||'')});
}
const byPrefix={}; for(const c of parsed) (byPrefix[c.p]=byPrefix[c.p]||[]).push(c);
const linked=new Set(Object.keys(PMAP));

/* ── 공통 글자 그램 ─────────────────────────────────────────────────────────
   [보강 2026-08-25] 지금까지 후보는 **판에 이미 걸린 카드의 접두어**에서만 나왔다.
   그래서 앵커가 1~2장뿐인 판은 엉뚱한 접두어만 훑고, 정작 맞는 단원은 통째로
   안 보였다 (s33p02 가 EZ-062·EZ-063 을, s17p05 가 H1-1~H1-5 를 놓친 것이 그것).
   접두어를 아예 안 보고 **미연결 카드 전부**를 행 글자와 겹치는 순으로 훑는 갈래를
   하나 더 둔다. 문턱을 높여(HITG) 잡음을 막고, 판정은 여전히 2단계가 한다. */
const STOP=new Set(['이것','그것','하는','되는','에서','으로','이다','한다','된다','있다','없다','같은','다른','때문','경우','통해','만든','만들','무엇','어느','어떤','가지','대해','한다면','라고','것은','것이','에는','에서는','하면','하고','이나','또는','그리고']);
function GRAMS(t){
  const g=new Set();
  const w=String(t).replace(/[^가-힣A-Za-z0-9]/g,' ').split(/\s+/).filter(Boolean);
  for(const x of w){
    if(x.length>=2&&!STOP.has(x)) g.add(x);
    if(/[가-힣]/.test(x)) for(let k=0;k+2<=x.length;k++){const b=x.slice(k,k+2); if(!STOP.has(b)) g.add(b);}
  }
  return g;
}
const UNLINKED=parsed.filter(c=>!linked.has(c.id));
const UG=new Map();                                  /* 카드 → 그램 (한 번만) */
for(const c of UNLINKED) UG.set(c.id, GRAMS(c.q+' '+c.a));

const out=[];
for(const sc of DATA) for(const p of (sc.panels||[])){
  const rows=(p.f||[]).map((f,k)=>({k, prop:strip(f[0]), fact:strip(f[1]), ids:(f[2]||[])}));
  if(!rows.length) continue;
  let anchors=rows.flatMap(r=>r.ids).map(id=>parsed.find(c=>c.id===id)).filter(Boolean);
  /* ★ 걸린 카드가 하나도 없는 판은 앵커가 없어 후보도 0장이 된다 — 정작 가장 비어 있는 판인데.
     같은 장면의 형제 판에서 접두어를 빌린다(번호 이웃은 못 쓰고 글자 겹침만 쓴다). */
  if(!anchors.length){
    const sib=(sc.panels||[]).flatMap(x=>(x.f||[]).flatMap(f=>f[2]||[])).map(id=>parsed.find(c=>c.id===id)).filter(Boolean);
    if(!sib.length) continue;
    anchors=sib.map(c=>({...c, n:-999}));      /* n 을 멀리 두어 번호 이웃은 안 걸리게 */
  }
  const cand=new Map();
  for(const a of anchors) for(const c of (byPrefix[a.p]||[])){
    if(linked.has(c.id)) continue;
    if(Math.abs(c.n-a.n)>GAP) continue;
    cand.set(c.id,c);
  }
  /* ★ [보강 2026-08-22] 번호 이웃만으로는 **이미 걸린 카드가 적은 판**에서 후보가 안 나온다.
     s18p02 는 걸린 카드가 0장이라 후보도 0장이었다 — 정작 가장 비어 있는 판인데.
     그래서 같은 접두어의 미연결 카드를 전부 모으고 **행의 사실 문장과 글자가 겹치는 순**으로
     추린다. 겹침은 순위를 매기는 데만 쓴다 — 판정은 여전히 2단계 사람(에이전트)이 한다. */
  const TOPN=Number(process.env.TOPN||40);
  const stop=new Set(['이것','그것','하는','되는','에서','으로','이다','한다','된다','있다','없다','같은','다른','때문','경우','통해','만든','만들']);
  const grams=t=>{const g=new Set();const w=String(t).replace(/[^가-힣A-Za-z0-9]/g,' ').split(/\s+/).filter(Boolean);
    for(const x of w){ if(x.length>=2&&!stop.has(x)) g.add(x);
      if(/[가-힣]/.test(x)) for(let k=0;k+2<=x.length;k++){const b=x.slice(k,k+2); if(!stop.has(b)) g.add(b);} }
    return g;};
  const rowG=rows.map(r=>grams(r.prop+' '+r.fact));
  const allG=new Set(); for(const g of rowG) for(const x of g) allG.add(x);
  const scored=[];
  for(const a of new Set(anchors.map(x=>x.p))) for(const c of (byPrefix[a]||[])){
    if(linked.has(c.id)||cand.has(c.id)) continue;
    const cg=grams(c.q+' '+c.a); let hit=0; for(const x of cg) if(allG.has(x)) hit++;
    if(hit>=3) scored.push({c,hit});
  }
  scored.sort((x,y)=>y.hit-x.hit);
  for(const {c} of scored.slice(0,TOPN)) cand.set(c.id,c);

  /* ★ 갈래 4 — 접두어를 안 보고 덱 전체의 미연결 카드를 훑는다.
     겹침이 HITG 이상인 것만, 그중 위 TOPG 장. 앵커가 적은 판을 살리는 갈래다. */
  const TOPG=Number(process.env.TOPG||25), HITG=Number(process.env.HITG||6);
  /* NEWONLY=1 — 갈래 1~3(접두어 기반)의 후보를 **버리고** 이 갈래만 남긴다.
     1~5차에서 이미 훑은 판을 다시 넘길 때 쓴다. 그 판들의 접두어 후보는 이미
     탈락 판정을 받았으므로 다시 보여 주면 판정자의 눈만 흐려진다. */
  if(process.env.NEWONLY) cand.clear();
  const gsc=[];
  for(const c of UNLINKED){
    if(cand.has(c.id)) continue;
    const cg=UG.get(c.id); let hit=0;
    for(const x of cg) if(allG.has(x)) hit++;
    if(hit>=HITG) gsc.push({c,hit});
  }
  gsc.sort((x,y)=>y.hit-x.hit);
  for(const {c} of gsc.slice(0,TOPG)) cand.set(c.id,c);
  out.push({id:p.id, scene:sc.id, gate:sc.gate, title:strip(p.t||''), rows,
            empty:rows.filter(r=>!r.ids.length).length, cards:rows.reduce((s,r)=>s+r.ids.length,0),
            cand:[...cand.values()].sort((x,y)=>x.p===y.p?x.n-y.n:x.p<y.p?-1:1)});
}
/* ── 여러 판을 한 번에 — DUMPDIR 이 있으면 인자로 준 판들을 파일로 쏟는다.
      13.7MB 를 판마다 다시 읽으면 63판에 2분이 넘는다. */
if(process.env.DUMPDIR){
  const dir=process.env.DUMPDIR;
  const ids=process.argv.slice(2);
  fs.mkdirSync(dir,{recursive:true});
  let tot=0;
  for(const id of ids){
    const p=out.find(x=>x.id===id);
    if(!p){ fs.writeFileSync(path.join(dir,id+'.txt'), id+' — 후보 없음\n'); continue; }
    const L=['══ '+p.id+'  '+p.title+'   ['+p.gate+']  '+p.rows.length+'행 · 빈 행 '+p.empty+' · 걸린 카드 '+p.cards];
    for(const r of p.rows) L.push('  '+String(r.k).padStart(2)+'. '+r.prop.slice(0,54)+'\n       → '+r.fact.slice(0,96)+(r.ids.length?'\n       ['+r.ids.join(' ')+']':''));
    L.push('','── 후보 '+p.cand.length+'장 ──');
    for(const c of p.cand) L.push('  '+c.id.padEnd(10)+' '+c.q.slice(0,60)+'  →  '+c.a.slice(0,74));
    fs.writeFileSync(path.join(dir,id+'.txt'), L.join('\n')+'\n');
    tot+=p.cand.length;
  }
  console.log(ids.length+'판 · 후보 연인원 '+tot+'장 → '+dir);
  process.exit(0);
}

const arg=process.argv[2];
if(arg){
  const p=out.find(x=>x.id===arg);
  if(!p){ console.log(arg+' — 후보 없음(걸린 카드가 하나도 없는 판이거나 없는 판)'); process.exit(0); }
  console.log('══ '+p.id+'  '+p.title+'   ['+p.gate+']  '+p.rows.length+'행 · 빈 행 '+p.empty+' · 걸린 카드 '+p.cards);
  for(const r of p.rows) console.log('  '+String(r.k).padStart(2)+'. '+r.prop.slice(0,54)+'\n       → '+r.fact.slice(0,96)+(r.ids.length?'\n       ['+r.ids.join(' ')+']':''));
  console.log('\n── 후보 '+p.cand.length+'장 ──');
  for(const c of p.cand) console.log('  '+c.id.padEnd(10)+' '+c.q.slice(0,60)+'  →  '+c.a.slice(0,74));
}else{
  out.sort((a,b)=>(b.cand.length-a.cand.length));
  const tot=out.reduce((s,p)=>s+p.cand.length,0);
  console.log('후보를 가진 판 '+out.filter(p=>p.cand.length).length+'개 · 후보 연인원 '+tot+'장 (GAP=±'+GAP+')');
  console.log('빈 행이 있고 후보가 많은 판 30:');
  for(const p of out.slice(0,30))
    console.log('  '+p.id.padEnd(9)+' 후보 '+String(p.cand.length).padStart(3)+'  빈행 '+String(p.empty).padStart(2)+'/'+String(p.rows.length).padStart(2)+'  걸림 '+String(p.cards).padStart(3)+'  '+p.title.slice(0,26));
}
