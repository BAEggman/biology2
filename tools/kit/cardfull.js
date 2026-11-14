#!/usr/bin/env node
// cardfull.js <id> [<id> …] — 카드의 모든 칸(q · a · it · cz · n · t · 자식)을 찍는다. 카드를 고치기 전에 「화면에 뜨는 칸」을 다 보려고 쓴다(tools/card.js 는 q · a 만).
const fs=require('fs'),path=require('path');
const idx=fs.readFileSync(path.join(__dirname,'..','..','index.html'),'utf8');
const CARDS=JSON.parse(idx.match(/id=["']CARDS["'][^>]*>([\s\S]*?)<\/script>/)[1]);
const strip=x=>String(x==null?'':x).replace(/<[^>]+>/g,'');
const by={}; for(const c of CARDS) if(c) by[c.id]=c;
for(const id of process.argv.slice(2)){ const c=by[id]; if(!c){ console.log('○',id,'없음'); continue; }
  const kids=CARDS.filter(x=>x&&x.p===id&&x.id!==id).map(x=>x.id);
  console.log(`● ${id} [${c.ch||''}] t=${c.t||''} ru=${c.ru||''}${kids.length?' · 자식 '+kids.join(','):''}\n  Q: ${strip(c.q)}\n  A: ${strip(c.a)}${c.it?'\n  it: '+JSON.stringify(c.it):''}${c.cz?'\n  cz: '+JSON.stringify(c.cz):''}${c.n?'\n  n: '+strip(c.n):''}`);
  for(const k of kids){ const x=by[k]; console.log(`    └ ${k} t=${x.t} Q: ${strip(x.q).slice(0,90)} | A: ${strip(x.a).slice(0,90)}`); } }
