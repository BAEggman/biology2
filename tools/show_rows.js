#!/usr/bin/env node
// show_rows.js <pid> [<pid> ...] — 판의 f 행(소품|사실|카드)을 번호와 함께 찍는다
const fs=require('fs'),path=require('path');
const sk=fs.readFileSync(path.join(__dirname,'..','sketchy.html'),'utf8');
function matchAt(src,st){const open=src[st],close={'[':']','{':'}'}[open];let d=0,q=null,esc=false;
 for(let k=st;k<src.length;k++){const c=src[k];
  if(q){if(esc){esc=false;continue}if(c==='\\'){esc=true;continue}if(c===q)q=null;continue}
  if(c==='"'||c==="'"||c==='`'){q=c;continue}
  if(c===open)d++;else if(c===close){d--;if(!d)return k;}}throw new Error('unbalanced');}
const i=sk.indexOf('const DATA = [');const st=sk.indexOf('[',i);const en=matchAt(sk,st);
const DATA=eval('('+sk.slice(st,en+1)+')');
const want=process.argv.slice(2);const full=want.includes('--br');
for(const pid of want.filter(x=>!x.startsWith('--'))){
 const p=DATA.flatMap(sc=>sc.panels||[]).find(x=>x.id===pid); if(!p){console.log('없음',pid);continue}
 console.log(`\n=== ${pid} ${p.t}`); if(full) console.log('br:',p.br.replace(/<[^>]+>/g,''));
 (p.f||[]).forEach((r,k)=>console.log(`${k+1}. [${r[0]}] → ${r[1]}${r[2]?'  {'+r[2].join(',')+'}':''}`));
}
