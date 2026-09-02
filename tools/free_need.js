#!/usr/bin/env node
/* 면제가 실제로 필요한가 — 그 라벨을 「카드의 답」이 요구하는가, 아니면 사실 칸에만 있는가. */
const fs=require('fs'), path=require('path');
const R=f=>fs.readFileSync(path.join(__dirname,'..',f),'utf8');
const idx=R('index.html');
const CARDS=JSON.parse(idx.match(/id=["']CARDS["'][^>]*>([\s\S]*?)<\/script>/)[1]);
const h=JSON.parse(R('tools/hooks.json'));
const strip=x=>String(x==null?'':x).replace(/<[^>]+>/g,'');
const which=process.argv[2]||'_뜻이있는약어';
const v=h[which]; const list=Object.keys(v['목록']||v);
const s=R('sketchy.html');
const facts=[...s.matchAll(/\["[^"]*","((?:[^"\\]|\\.)*)"/g)].map(m=>strip(m[1])).join(' | ');
let needy=0, free=0;
const out=[];
for(const lab of list){
  const inAns = CARDS.some(c=>c&&c.a&&strip(c.a).includes(lab));
  const inQ   = CARDS.some(c=>c&&c.q&&strip(c.q).includes(lab));
  const inFact= facts.includes(lab);
  out.push({lab, ans:inAns, q:inQ, fact:inFact});
  if(inAns) needy++; else free++;
}
out.sort((a,b)=>(a.ans-b.ans)||(a.q-b.q)||a.lab.localeCompare(b.lab));
for(const o of out) console.log('%s %s  답%s 발문%s 사실칸%s', o.ans?' ':'○', o.lab.padEnd(20), o.ans?'O':'·', o.q?'O':'·', o.fact?'O':'·');
console.log('\n답이 요구함 %d · 답이 안 요구함 %d (○ = 면제가 없어도 될 수 있다)', needy, free);
