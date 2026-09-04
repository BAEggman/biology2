#!/usr/bin/env node
/* 채점 결과 집계.  node tools/blind/report.js [--md]  */
const fs=require('fs'), path=require('path');
const man=JSON.parse(fs.readFileSync(path.join(__dirname,'manifest.json'),'utf8'));
const M=Object.fromEntries(man.map(m=>[m.pid,m]));
const outDir=path.join(__dirname,'out');
const files=fs.readdirSync(outDir).filter(f=>/^s\d+p\d+\w*\.json$/.test(f));
const R=[];
for(const f of files){ const d=JSON.parse(fs.readFileSync(path.join(outDir,f),'utf8')); if(d&&d.rows) R.push(d); }
const tot={rows:0,seenN:0,coldY:0,coldP:0,cuedY:0,cuedP:0,cuedN:0,cards:0,cardsSeenN:0,cardsCuedN:0};
const bad=[];   // seen=N 또는 cued=N 인 행
const weak=[];  // cued=P 인 행 — 물건은 있는데 고리가 엉성하다
const panels=[];
for(const d of R){ const m=M[d.pid]; if(!m) continue;
  let pn=0, pcued=0, pseenN=0;
  for(const r of d.rows){ const row=m.rows[r.n-1]; if(!row) continue; const nc=row.cards||0;
    tot.rows++; tot.cards+=nc; pn++;
    if(r.seen==='N'){ tot.seenN++; tot.cardsSeenN+=nc; pseenN++; }
    if(r.cold==='Y') tot.coldY++; else if(r.cold==='P') tot.coldP++;
    if(r.cued==='Y'){ tot.cuedY++; pcued++; } else if(r.cued==='P') tot.cuedP++; else { tot.cuedN++; tot.cardsCuedN+=nc; }
    if(r.seen==='N'||r.cued==='N') bad.push({pid:d.pid,n:r.n,cards:nc,seen:r.seen,cold:r.cold,cued:r.cued,prop:row.prop.slice(0,60),note:r.note});
    else if(r.cued==='P') weak.push({pid:d.pid,n:r.n,cards:nc,seen:r.seen,cold:r.cold,cued:r.cued,prop:row.prop.slice(0,60),note:r.note});
  }
  panels.push({pid:d.pid,title:m.title,rows:pn,cuedY:pcued,seenN:pseenN,note:d.panel_note||''});
}
const pct=(a,b)=>b?Math.round(100*a/b)+'%':'-';
const md=process.argv.includes('--md');
const L=[];
L.push(`# 블라인드 테스트 집계 — 판 ${R.length}개 · 행 ${tot.rows} · 카드 ${tot.cards}장`);
L.push('');
L.push(`| 재는 것 | 행 | 비율 |`); L.push('|---|---|---|');
L.push(`| **안 보인 물건** (seen=N) | ${tot.seenN} | ${pct(tot.seenN,tot.rows)} — 카드 ${tot.cardsSeenN}장 |`);
L.push(`| 차갑게도 짚임 (cold=Y) | ${tot.coldY} | ${pct(tot.coldY,tot.rows)} |`);
L.push(`| 차갑게 방향만 (cold=P) | ${tot.coldP} | ${pct(tot.coldP,tot.rows)} |`);
L.push(`| **이름 주면 되찾음** (cued=Y) | ${tot.cuedY} | ${pct(tot.cuedY,tot.rows)} |`);
L.push(`| 이름 줘도 엉성 (cued=P) | ${tot.cuedP} | ${pct(tot.cuedP,tot.rows)} |`);
L.push(`| **이름 줘도 못 찾음** (cued=N) | ${tot.cuedN} | ${pct(tot.cuedN,tot.rows)} — 카드 ${tot.cardsCuedN}장 |`);
L.push('');
L.push('## 판별 — 되찾은 행 / 전체 (안 보인 물건)');
L.push('');
L.push('| 판 | 제목 | 되찾음 | 안 보임 | 채점자 메모 |'); L.push('|---|---|---|---|---|');
for(const p of panels.sort((a,b)=>(a.cuedY/a.rows)-(b.cuedY/b.rows))) L.push(`| ${p.pid} | ${p.title.slice(0,28)} | ${p.cuedY}/${p.rows} | ${p.seenN} | ${p.note.slice(0,110).replace(/\|/g,'·')} |`);
L.push('');
L.push(`## 고쳐야 할 행 — seen=N 또는 cued=N (${bad.length}행 · 카드 순)`);
L.push('');
L.push('| 판 | 행 | 장 | seen | cold | cued | 소품 | 왜 |'); L.push('|---|---|---|---|---|---|---|---|');
for(const b of bad.sort((a,b)=>b.cards-a.cards)) L.push(`| ${b.pid} | ${b.n} | ${b.cards} | ${b.seen} | ${b.cold} | ${b.cued} | ${b.prop.replace(/\|/g,'·')} | ${String(b.note||'').slice(0,120).replace(/\|/g,'·')} |`);
L.push('');
L.push(`## 엉성한 행 — cued=P (${weak.length}행 · 카드 순) — 물건은 있는데 고리가 엉성하거나 다른 물건에 이었다`);
L.push('');
L.push('| 판 | 행 | 장 | cold | 소품 | 왜 |'); L.push('|---|---|---|---|---|---|');
for(const b of weak.sort((a,b)=>b.cards-a.cards)) L.push(`| ${b.pid} | ${b.n} | ${b.cards} | ${b.cold} | ${b.prop.replace(/\|/g,'·')} | ${String(b.note||'').slice(0,120).replace(/\|/g,'·')} |`);
const out=L.join('\n');
if(md){ const p=path.join(__dirname,'..','..','outputs','블라인드테스트_2026-09-04.md'); fs.writeFileSync(p,out); console.log('→',p); }
console.log(out);
