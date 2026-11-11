// prep.js — 과마다 감사 묶음(정거장 글 + 옛 행 + 카드 Q/A)과 기계 지표를 만든다
const fs=require('fs'),path=require('path');
const ROOT='/tmp/b2', OUT=process.argv[2];
const {deck,strip,panelIndex,resolveRef,lessons}=require(ROOT+'/tools/lesson_lib');
const ix=fs.readFileSync(ROOT+'/index.html','utf8');
const CARDS=JSON.parse(ix.match(/id=["']CARDS["'][^>]*>([\s\S]*?)<\/script>/)[1]);
const CMAP=new Map(CARDS.map(c=>[c.id,c]));
// 카드 한 줄 — 화면에 실제로 뜨는 칸까지: 빈칸(cz) · 목록(it) · 덧말(n) · 종류(t) · 부모(p) · 자식(dep)
function card(id){ const c=CMAP.get(id); if(!c) return null;
  return {q:strip(c.q),a:strip(c.a),t:c.t,p:(c.p&&c.p!==c.id)?c.p:'',cz:c.cz?strip(c.cz):'',it:c.it||null,n:c.n?strip(c.n):'',dep:c.dep||null}; }
const idx=panelIndex();
const metrics=[]; const hookRows=[];
const RISK=/[⁺⁻⁰¹²³⁴⁵⁶⁷⁸⁹₀₁₂₃₄₅₆₇₈₉′″→←↑↓↔≈≠≤≥αβγδεκλμσωΔ=+%]/g;
for(const L of lessons()){
  let pk=`# ${L.id} — ${L.title}\n(묶음 ${L.scene} · 그림 ${L.w}×${L.h})\n요약(sub): ${L.sub||''}\n`;
  const m={id:L.id,scene:L.scene,stops:L.stops.length,noBox:[],bigBox:[],smallBox:[],factMax:0,sayMin:1e9,sayMax:0,sayTot:0,cards:new Set(),noSrc:[],risk:{},boxes:0,missCard:[]};
  L.stops.forEach((s,k)=>{
    const bs=s.box?(Array.isArray(s.box[0])?s.box:[s.box]):[];
    if(!bs.length) m.noBox.push(k);
    for(const [x,y,w,h] of bs){ m.boxes++; const ar=w*h/(L.w*L.h); if(ar>0.5) m.bigBox.push(k+':'+ar.toFixed(2)); if(w<70||h<70) m.smallBox.push(k+':'+w+'x'+h); }
    m.factMax=Math.max(m.factMax,(s.fact||'').length); const sl=(s.say||'').length; m.sayMin=Math.min(m.sayMin,sl); m.sayMax=Math.max(m.sayMax,sl); m.sayTot+=sl;
    if(!(s.src||[]).length) m.noSrc.push(k);
    for(const ch of ((s.say||'').match(RISK)||[])) m.risk[ch]=(m.risk[ch]||0)+1;
    pk+=`\n## 정거장 ${k}  (sid ${s.sid})\n물건(obj): ${s.obj}\n사실(fact): ${s.fact}\n고리(hook): ${s.hook}\n말(say): ${s.say}\n상자: ${bs.length?JSON.stringify(bs):'없음(전체)'}\n`;
    const seen=new Set();
    for(const r of (s.src||[])){ let R; try{R=resolveRef(r,idx);}catch(e){ pk+=`옛 행 ${r}: (풀지 못함 ${e.message})\n`; continue; }
      pk+=`옛 행 ${r} — 소품: ${strip(R.row[0])} / 사실: ${strip(R.row[1])}\n`;
      for(const c of (R.row[2]||[])){ m.cards.add(c); if(seen.has(c)) continue; seen.add(c); const cd=card(c); if(!cd){ m.missCard.push(c); pk+=`  카드 ${c}: (본문 못 찾음)\n`; } else pk+=`  카드 ${c} [${cd.t}${cd.p?' · 부모 '+cd.p:''}${cd.dep?' · 자식 '+cd.dep.join(','):''}] | Q: ${cd.q}${cd.cz?' | 빈칸: '+cd.cz:''} | A: ${cd.a}${cd.it?' | 목록(화면에 뜨는 답): '+cd.it.join(' / '):''}${cd.n?' | 덧말: '+cd.n:''}\n`; }
    }
    const cline=(c)=>{ const cd=card(c); return !cd?`  카드 ${c}: (본문 못 찾음)\n`:`  카드 ${c} [${cd.t}${cd.p?' · 부모 '+cd.p:''}${cd.dep?' · 자식 '+cd.dep.join(','):''}] | Q: ${cd.q}${cd.cz?' | 빈칸: '+cd.cz:''} | A: ${cd.a}${cd.it?' | 목록(화면에 뜨는 답): '+cd.it.join(' / '):''}${cd.n?' | 덧말: '+cd.n:''}\n`; };
    if(Array.isArray(s.cards)&&s.cards.length){ pk+=`곧장 건 카드(cards):\n`; for(const c of s.cards){ m.cards.add(c); pk+=cline(c); } }
    if(Array.isArray(s.drop)&&s.drop.length){ pk+=`뗀 카드(drop — 옛 행에 딸려 왔지만 이 정거장 것이 아님): ${s.drop.join(', ')}\n`; for(const c of s.drop) m.cards.delete(c); }
    if(s.ask) pk+=`시험 물음(ask): ${s.ask}\n`;
    for(const part of String(s.hook||'').split(/ · /)){ const mm=part.split(/\s=\s/); if(mm.length>=2) hookRows.push({L:L.id,scene:L.scene,k,x:mm[0].trim(),y:mm.slice(1).join(' = ').trim()}); else hookRows.push({L:L.id,scene:L.scene,k,x:part.trim(),y:''}); }
  });
  m.cards=m.cards.size; fs.writeFileSync(path.join(OUT,'pk',L.id+'.txt'),pk);
  m.pkChars=pk.length; metrics.push(m);
}
fs.writeFileSync(path.join(OUT,'metrics.json'),JSON.stringify(metrics));
fs.writeFileSync(path.join(OUT,'hooks_rows.json'),JSON.stringify(hookRows));
console.log('lessons',metrics.length,'hook rows',hookRows.length,'packet chars',metrics.reduce((a,x)=>a+x.pkChars,0));
