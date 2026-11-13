// tally.js — 계획(G1~G5)의 부모 카드가 지금 덱에서 어떤 상태인지 센다: 걸림(새 과) · 옛 s 판만 · 그림 없음. 사용: node tools/plan/tally.js [ch|pic|att|ids <그림 이름 조각>]
const fs=require('fs'),path=require('path');
const {deck,lessons}=require(path.join(__dirname,'..','lesson_lib'));
const s=fs.readFileSync(path.join(__dirname,'..','..','index.html'),'utf8');
const CARDS=JSON.parse(s.match(/<script[^>]*id=["']CARDS["'][^>]*>([\s\S]*?)<\/script>/)[1]);
const all=lessons();
const covered=new Set(); for(const L of all) for(const st of L.stops) for(const r of (st.src||[])) covered.add(r);
const direct=new Set(); for(const L of all) for(const st of L.stops) for(const c of (Array.isArray(st.cards)?st.cards:[])) direct.add(c.replace(/#\d+$/,''));
const where={};
for(const sc of deck()) for(const P of sc.panels){ if(P.retired) continue; P.f.forEach((row,i)=>{ for(const c0 of (row[2]||[])){ const c=c0.replace(/#\d+$/,''); const w=(where[c]=where[c]||new Set()); w.add(covered.has(P.id+'#'+i)?'built':sc.id[0]==='d'?'d':'pendS'); } }); }
for(const c of direct) (where[c]=where[c]||new Set()).add('built');
const cls=id=>{const w=where[id]; if(!w) return 'none'; return w.has('built')?'built':w.has('pendS')?'pendS':w.has('d')?'d':'none';};
const dir=path.join(__dirname,'2026-11-11');
const pics={}; const chs=[]; const att={};
for(const f of fs.readdirSync(dir).filter(f=>/^G\d.*\.json$/.test(f)).sort()){
  const G=JSON.parse(fs.readFileSync(path.join(dir,f),'utf8'));
  for(const ch of G.chapters){
    const byName={}; for(const c of ch.clusters) byName[c.name]=c;
    const t={built:0,pendS:0,d:0,none:0}; const seen=new Set();
    for(const c of ch.clusters) for(const id of c.ids){ if(seen.has(id)) continue; seen.add(id); t[cls(id)]++; }
    chs.push({g:f.slice(0,2),ch:ch.ch,n:seen.size,...t});
    const inPic=new Set();
    for(const p of (ch.pictures||[])){ const P=(pics[p.title]=pics[p.title]||{title:p.title,chs:[],built:0,pendS:0,d:0,none:0,n:0,noneIds:[]});
      P.chs.push(ch.ch.split(' ')[0]);
      for(const nm of p.clusters){ const c=byName[nm]; if(!c){ console.error('? cluster',nm); continue; } for(const id of c.ids){ inPic.add(id); const k=cls(id); P[k]++; P.n++; if(k!=='built') P.noneIds.push(id); } } }
    for(const a of (ch.attach||[])){ const A=(att[a.lesson]=att[a.lesson]||{lesson:a.lesson,n:0,left:0,items:[]}); let left=0; for(const id of a.ids){ A.n++; if(cls(id)!=='built'){ A.left++; left++; } } if(left) A.items.push(`${ch.ch.split(' ')[0]}장 ${a.what.slice(0,40)} (${left})`); }
  }
}
const mode=process.argv[2]||'all';
if(mode==='all'||mode==='ch'){ console.log('== 장별 =='); let T={n:0,built:0,pendS:0,d:0,none:0}; for(const c of chs){ console.log(`${c.ch} | 부모 ${c.n} | 걸림 ${c.built} | 옛 s 판만 ${c.pendS} | 그림 없음 ${c.none}${c.d?` | d ${c.d}`:''}`); for(const k in T) T[k]+=c[k]; } console.log('합', JSON.stringify(T)); }
if(mode==='all'||mode==='pic'){ console.log('== 새 그림별(남은 것 많은 순) =='); const L=Object.values(pics).sort((a,b)=>(b.none+b.pendS)-(a.none+a.pendS)); for(const p of L) console.log(`${p.none+p.pendS===0?'✅':'  '} ${p.title.split(' — ')[0]} [${[...new Set(p.chs)].join('·')}] 카드 ${p.n} · 그림 없음 ${p.none} · 옛 s 판만 ${p.pendS} · 걸림 ${p.built}`); }
if(mode==='all'||mode==='att'){ console.log('== 덧붙임(남은 것 많은 순) =='); const L=Object.values(att).filter(a=>a.left).sort((a,b)=>b.left-a.left); let tot=0; for(const a of L){ tot+=a.left; console.log(`${a.lesson} 남음 ${a.left}/${a.n}`); } console.log('덧붙임 남은 합', tot, '· 과', L.length); }
if(mode==='ids'){ const p=pics[Object.keys(pics).find(k=>k.includes(process.argv[3]))]; console.log(p.title, p.noneIds.join(' ')); }
