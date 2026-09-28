#!/usr/bin/env node
// card.js <id> [<id> ...] — 카드 앞뒤를 찍는다 (#n 붙은 id는 본 카드로)
const fs=require('fs'),path=require('path');
const idx=fs.readFileSync(path.join(__dirname,'..','index.html'),'utf8');
const CARDS=JSON.parse(idx.match(/id=["']CARDS["'][^>]*>([\s\S]*?)<\/script>/)[1]);
const strip=x=>String(x==null?'':x).replace(/<[^>]+>/g,'');
for(const id of process.argv.slice(2)){const base=id.split('#')[0];const c=CARDS.find(c=>c&&c.id===base);
 console.log(c?`● ${id}\n  Q: ${strip(c.q)}\n  A: ${strip(c.a)}`:`○ ${id} 없음`);}
