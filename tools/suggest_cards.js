// 미연결 카드 ↔ 이미 있는 패널 후보 짝짓기.
// 사람이 검토할 「볼 값어치 있는 짝」만 추려 준다. 최종 판정은 언제나 그림을 보고 한다.
const fs=require('fs');
const s=fs.readFileSync('/tmp/b2/sketchy.html','utf8');
const st=s.indexOf('[',s.indexOf('const DATA')); let d=0,q=null,e=false,end=0;
for(let k=st;k<s.length;k++){const c=s[k];
  if(q){if(e){e=false;continue}if(c==='\\'){e=true;continue}if(c===q)q=null;continue}
  if(c==='"'||c==="'"||c==='`'){q=c;continue}
  if(c==='[')d++;else if(c===']'){d--;if(!d){end=k+1;break}}}
const DATA=eval('('+s.slice(st,end)+')');
const h=fs.readFileSync('/tmp/b2/index.html','utf8');
const CARDS=JSON.parse(h.match(/<script id="CARDS"[^>]*>([\s\S]*?)<\/script>/)[1]);
const PMAP=JSON.parse(h.match(/var PMAP=(\{.*?\});/s)[1]);

const strip=t=>String(t||'').replace(/<[^>]*>/g,' ');
// 2글자 이상 한글/영문 토큰
const tok=t=>{
  const out=new Set();
  for(const m of strip(t).matchAll(/[가-힣]{2,}|[A-Za-z][A-Za-z0-9']{1,}/g)){
    let w=m[0];
    if(/^[가-힣]+$/.test(w)) for(let L=Math.min(w.length,5);L>=2;L--)
      for(let i=0;i+L<=w.length;i++) out.add(w.slice(i,i+L));
    else out.add(w.toLowerCase());
  }
  return out;
};

const GATE=process.argv[2]||'*';
const MINSC=parseFloat(process.argv[3]||'3.5');

// 패널 색인 (해당 게이트만)
const panels=[];
for(const sc of DATA){
  if(GATE!=='*' && sc.gate!==GATE) continue;
  for(const p of sc.panels||[]){
    const txt=[p.t,p.br,p.bx,...(p.f||[]).map(r=>r[0]+' '+r[1])].join(' ');
    panels.push({id:p.id,gate:sc.gate,scene:sc.t,title:p.t,toks:tok(txt),
      rows:(p.f||[]).map(r=>strip(r[0]).replace(/\s+/g,' ').trim())});
  }
}
// 문서빈도 → 흔한 토큰은 값을 깎는다
const df=new Map();
for(const p of panels) for(const t of p.toks) df.set(t,(df.get(t)||0)+1);
const idf=t=>Math.log((panels.length+1)/((df.get(t)||0)+1));

// 이 게이트에 이미 쓰인 카드 접두어만 후보로 본다
const pre=new Set();
for(const sc of DATA){ if(GATE!=='*'&&sc.gate!==GATE)continue;
  for(const p of sc.panels||[]) for(const r of p.f||[]) for(const c of r[2]||[]) pre.add(c.replace(/-.*/,''));
  for(const c of (function(){const o=[];for(const p of sc.panels||[])for(const x of p.pc||[])o.push(x);return o})()) pre.add(c.replace(/-.*/,''));
}
const out=[];
for(const c of CARDS){
  if(PMAP[c.id]) continue;
  if(!pre.has(c.id.replace(/-.*/,''))) continue;
  const ct=tok((c.q||'')+' '+(c.a||''));
  let best=null;
  for(const p of panels){
    let sc=0;
    for(const t of ct) if(p.toks.has(t)) sc+=idf(t)*Math.min(t.length,4)/4;
    if(!best||sc>best.sc) best={sc,p};
  }
  if(best&&best.sc>=MINSC) out.push({id:c.id,q:strip(c.q).replace(/\s+/g,' ').trim(),
    a:strip(c.a).replace(/\s+/g,' ').trim(),pid:best.p.id,title:best.p.title,sc:best.sc});
}
out.sort((a,b)=>b.sc-a.sc);
console.log('게이트 '+GATE+' · 패널 '+panels.length+' · 후보 '+out.length+'건 (점수 '+MINSC+' 이상)\n');
const byp={};
for(const o of out){ (byp[o.pid]=byp[o.pid]||[]).push(o); }
for(const pid of Object.keys(byp).sort((a,b)=>byp[b].length-byp[a].length)){
  const g=byp[pid];
  console.log('■ '+pid+'  「'+g[0].title+'」  '+g.length+'장');
  for(const o of g.slice(0,12)) console.log('    '+o.sc.toFixed(1).padStart(5)+'  '+o.id+' | '+o.q.slice(0,58)+' → '+o.a.slice(0,48));
  console.log();
}
