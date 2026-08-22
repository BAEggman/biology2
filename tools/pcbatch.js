/* pc N~M장짜리 판을 한꺼번에 펼친다 — 행(소품/사실/카드수) + pc 카드 Q/A.
   판정은 이 출력만 보고 내릴 수 있다.   쓰기: node tools/pcbatch.js 5 9 [판ID접두어] */
const fs=require('fs'), path=require('path');
const R=path.join(__dirname,'..');
const ix=fs.readFileSync(path.join(R,'index.html'),'utf8');
const C={}; JSON.parse(ix.match(/<script id="CARDS"[^>]*>([\s\S]*?)<\/script>/)[1]).forEach(c=>C[c.id]=c);
const s=fs.readFileSync(path.join(R,'sketchy.html'),'utf8');
const i=s.indexOf('[', s.indexOf('const DATA'));
let d=0,q=null,e=false,end=0;
for(let k=i;k<s.length;k++){const c=s[k];
 if(q){if(e){e=false;continue}if(c==='\\'){e=true;continue}if(c===q)q=null;continue}
 if(c==='"'||c==="'"||c==='`'){q=c;continue}
 if(c==='[')d++;else if(c===']'){d--;if(!d){end=k+1;break}}}
const DATA=eval('('+s.slice(i,end)+')');
const st=x=>String(x==null?'':x).replace(/<[^>]+>/g,'');
const lo=+(process.argv[2]||1), hi=+(process.argv[3]||lo), only=process.argv[4];
for(const sc of DATA) for(const p of (sc.panels||[])){
  const n=(p.pc||[]).length; if(!n||n<lo||n>hi) continue;
  if(only && !p.id.startsWith(only)) continue;
  console.log('\n════ '+p.id+' 「'+sc.t+' · '+p.t+'」  pc '+n+'장'+(p.svg?' [도해]':''));
  (p.f||[]).forEach((r,k)=>console.log('  '+(k+1)+'. '+st(r[0]).slice(0,68)+'   → '+st(r[1]).slice(0,84)+'  ['+(r[2]||[]).length+']'));
  (p.pc||[]).forEach(id=>{const c=C[id]||{};
    console.log('   ● '+id.padEnd(9)+st(c.q).slice(0,66));
    console.log('     '.padEnd(14)+'→ '+st(c.a).slice(0,94));});
}
