#!/usr/bin/env node
/* 미연결 카드를 낱말로 찾는다 — 훑기용.  node tools/findcards.js 낱말 [낱말...] */
const fs=require('fs'), path=require('path');
const R=f=>fs.readFileSync(path.join(__dirname,'..',f),'utf8');
const idx=R('index.html');
const CARDS=JSON.parse(idx.match(/id=["']CARDS["'][^>]*>([\s\S]*?)<\/script>/)[1]);
const pm=idx.match(/var PMAP=(\{[\s\S]*?\});/); const PMAP=JSON.parse(pm[1]);
const words=process.argv.slice(2);
const strip=x=>String(x==null?'':x).replace(/<[^>]+>/g,'');
let n=0;
for(const c of CARDS){
  if(!c||!c.id) continue;
  if(PMAP[c.id]) continue;
  const t=strip(c.q)+' || '+strip(c.a);
  if(words.some(w=>t.includes(w))){ console.log('○ '+c.id+' | '+t); n++; }
}
console.error('미연결 일치 '+n+'장');
