#!/usr/bin/env node
/* pmapRemoved 를 「그릴 것의 목록」으로 읽는다 — 아직도 미연결인 것만, 판별로 묶어서. */
const fs=require('fs'), path=require('path');
const R=f=>fs.readFileSync(path.join(__dirname,'..',f),'utf8');
const idx=R('index.html');
const CARDS={}; for(const c of JSON.parse(idx.match(/id=["']CARDS["'][^>]*>([\s\S]*?)<\/script>/)[1])) if(c&&c.id) CARDS[c.id]=c;
const PMAP=JSON.parse(idx.match(/var PMAP=(\{[\s\S]*?\});/)[1]);
const b=JSON.parse(R('test/baseline.json'));
const rm=b.pmapRemoved||{};
const strip=x=>String(x==null?'':x).replace(/<[^>]+>/g,'');
const by={};
let still=0, back=0;
for(const [cid,v] of Object.entries(rm)){
  if(PMAP[cid]){ back++; continue; }
  still++;
  const k=v.from||'?';
  (by[k]=by[k]||[]).push({cid, why:strip(v.why||''), q:CARDS[cid]?strip(CARDS[cid].q):'(카드없음)', a:CARDS[cid]?strip(CARDS[cid].a):''});
}
const keys=Object.keys(by).sort((a,c)=>by[c].length-by[a].length);
for(const k of keys){
  console.log('\n■ '+k+'  '+by[k].length+'장');
  for(const e of by[k]) console.log('   '+e.cid+' | '+e.q.slice(0,58)+' → '+e.a.slice(0,44)+'\n        ↳ '+e.why.slice(0,120));
}
console.log('\n아직 미연결 %d · 그 뒤 다시 걸린 것 %d', still, back);
