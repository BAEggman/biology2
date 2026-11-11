// where.js — 카드 id 가 지금 어느 과 · 정거장에 걸렸는지(src 행 + 곧장 건 cards)
const fs=require('fs'),path=require('path');
const {panelIndex,stopCards}=require('/tmp/b2/tools/lesson_lib');
const idx=panelIndex();
const want=new Set(process.argv.slice(2));
const dir='/tmp/b2/lessons'; const hit={};
for(const f of fs.readdirSync(dir).filter(f=>/^L.*\.json$/.test(f))){
  const L=JSON.parse(fs.readFileSync(path.join(dir,f),'utf8'));
  L.stops.forEach((s,i)=>{ for(const c of stopCards(s,idx)) if(want.has(c)) (hit[c]=hit[c]||[]).push(`${L.id}#${i}(${s.sid})`); });
}
for(const c of want) console.log(c, hit[c]?hit[c].join(' '):'— 없음');
