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

const out=[];
for(const sc of DATA) for(const p of (sc.panels||[])){
  const rows=(p.f||[]).map((f,k)=>({k, prop:strip(f[0]), fact:strip(f[1]), ids:(f[2]||[])}));
  if(!rows.length) continue;
  const anchors=rows.flatMap(r=>r.ids).map(id=>parsed.find(c=>c.id===id)).filter(Boolean);
  if(!anchors.length) continue;
  const cand=new Map();
  for(const a of anchors) for(const c of (byPrefix[a.p]||[])){
    if(linked.has(c.id)) continue;
    if(Math.abs(c.n-a.n)>GAP) continue;
    cand.set(c.id,c);
  }
  out.push({id:p.id, scene:sc.id, gate:sc.gate, title:strip(p.t||''), rows,
            empty:rows.filter(r=>!r.ids.length).length, cards:rows.reduce((s,r)=>s+r.ids.length,0),
            cand:[...cand.values()].sort((x,y)=>x.p===y.p?x.n-y.n:x.p<y.p?-1:1)});
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
