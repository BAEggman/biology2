#!/usr/bin/env node
/* report.js — 보류 보고(tools/audit/2026-11-20/보류_보고.md)를 대장 · 승급 쪽지 · 녹음 목록에서 뽑는다(지시서 §8 · 세션마다 다시 만든다).
   node tools/audit/2026-11-20/report.js [--write]   — 그냥 돌리면 요약만, --write 면 파일을 고쳐 쓴다. */
const fs=require('fs'), path=require('path');
const ROOT=path.resolve(__dirname,'../../..'), A=__dirname;
const I=fs.readFileSync(path.join(A,'issues.json'),'utf8').split('\n').filter(l=>l.startsWith('{')).map(l=>JSON.parse(l.replace(/,$/,'')));
const LS=JSON.parse(fs.readFileSync(path.join(A,'lessons.json'),'utf8'));
const lessons=Array.isArray(LS)?LS:(LS.lessons||Object.values(LS));
const verdict={}; for(const x of lessons){ const id=x.id||x.lesson; verdict[id]=x.verdict||x.v||x.judge||''; }
const man=JSON.parse(fs.readFileSync(path.join(ROOT,'lesson/audio/manifest.json'),'utf8')).lessons||{};
const lock=JSON.parse(fs.readFileSync(path.join(ROOT,'tools/audio/locked.json'),'utf8'));
const holdP=path.join(ROOT,'lesson/audio/hold.json'); const hold=fs.existsSync(holdP)?JSON.parse(fs.readFileSync(holdP,'utf8')):{};
const promoDir=path.join(A,'승급'); const promo={};
if(fs.existsSync(promoDir)) for(const f of fs.readdirSync(promoDir)){ const t=fs.readFileSync(path.join(promoDir,f),'utf8'); const m=t.match(/## 판정: \*\*([^*]+)\*\*/); promo[f.replace('.md','')]=m?m[1]:'?'; }
const OPEN=new Set(['open','reproduced','proposed','changed']);
const sevK={critical:'최우선',major:'중요',minor:'경미',user:'사용자'};
const byL={}; for(const it of I){ if(!OPEN.has(it.state)) continue; (byL[it.lesson]=byL[it.lesson]||[]).push(it); }
const cnt=(a,f)=>a.filter(f).length;
const today=new Date(Date.now()+9*3600e3).toISOString().slice(0,10);
let o=`# 보류 보고 — ${today}\n\n`+
`\`node tools/audit/2026-11-20/report.js --write\` 가 대장(issues.json) · 승급 쪽지(승급/) · 녹음 목록(lesson/audio/manifest.json · tools/audio/locked.json · lesson/audio/hold.json)에서 뽑은 것. 손으로 고치지 않는다.\n\n`;
const crit=I.filter(x=>x.sev==='critical'&&OPEN.has(x.state));
o+=`## 맨 위 — 공개 중인데 아직 못 고친 사실 오류\n`;
if(!crit.length) o+=`없음.\n\n`; else {
  o+=`| 항목 | 과 · 구간 | 녹음 | 지금 공개본 | 고칠 곳 |\n|---|---|---|---|---|\n`;
  for(const x of crit){ const rec=x.sids.some(s=>man[x.lesson]&&man[x.lesson][s]); const h=hold[x.lesson]&&x.sids.some(s=>(hold[x.lesson]||[]).includes(s));
    o+=`| ${x.id} | ${x.lesson} ${x.sids.join(' · ')} | ${rec?(h?'있음 · hold':'있음 ⚠'):'없음(기기 음성)'} | 옛 글 그대로 | ${x.scope||x.fix0} |\n`; }
  o+=`\n`; }
const st={}; for(const it of I) st[it.state]=(st[it.state]||0)+1;
o+=`## 수\n- 대장 ${I.length}줄 — `+Object.entries(st).map(([k,v])=>`${k} ${v}`).join(' · ')+`\n`;
o+=`- scope 확정(그림을 열어 범위를 정함) ${cnt(I,x=>x.scope)} / ${cnt(I,x=>OPEN.has(x.state))}\n`;
const nrec=Object.values(man).reduce((a,v)=>a+Object.keys(v).length,0);
o+=`- 녹음 공개 ${Object.keys(man).length}과 ${nrec} 구간 · 잠금 목록(녹음해도 되는 구간) ${Object.values(lock['잠김']||{}).reduce((a,v)=>a+((v.sids||v['구간']||[]).length),0)} 구간 · hold ${Object.values(hold).reduce((a,v)=>a+(Array.isArray(v)?v.length:0),0)} 구간\n`;
o+=`- 승급 검사한 과 ${Object.keys(promo).length} — `+Object.entries(promo).map(([k,v])=>`${k} ${v.split(/[ (]/)[0]}`).join(' · ')+`\n\n`;
o+=`## 과마다(열린 항목이 있거나 승급 검사를 한 과)\n| 과 | 감사 판정 | 열린 항목(최우선/중요/경미/사용자) | 그림이 있어야 닫힘 | 녹음 | 승급 | 지금 공개본 |\n|---|---|---|---|---:|---|---|\n`;
const ids=[...new Set([...Object.keys(byL),...Object.keys(promo)])].sort();
for(const L of ids){ const a=byL[L]||[];
  const img=cnt(a,x=>/그림/.test(x.scope||x.fix0||''));
  const rec=man[L]?Object.keys(man[L]).length:0;
  o+=`| ${L} | ${verdict[L]||''} | ${a.length}(${cnt(a,x=>x.sev==='critical')}/${cnt(a,x=>x.sev==='major')}/${cnt(a,x=>x.sev==='minor')}/${cnt(a,x=>x.sev==='user')}) | ${img} | ${rec} | ${promo[L]?promo[L].split(/[ (]/)[0]:'—'} | 글 · 그림 옛것${rec?' · Gemini 녹음(AI 검수)':' · 기기 음성'} |\n`; }
o+=`\n## 다음 수\n지시서 §9 — 1단계(글): 최우선 8 → 글만으로 닫히는 중요 → 「글→그림」의 글 쪽 → 경미 → L17e-01 한 문장 → hold.json 과 재생기의 보류 처리.\n`;
if(process.argv.includes('--write')){ fs.writeFileSync(path.join(A,'보류_보고.md'),o); console.log('→ 보류_보고.md'); }
else console.log(o.split('\n').slice(0,20).join('\n'));
