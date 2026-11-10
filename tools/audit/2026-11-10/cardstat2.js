const fs=require('fs'); const ROOT='/tmp/b2';
const {deck,lessons}=require(ROOT+'/tools/lesson_lib');
const ix=fs.readFileSync(ROOT+'/index.html','utf8');
const CARDS=JSON.parse(ix.match(/id=["']CARDS["'][^>]*>([\s\S]*?)<\/script>/)[1]);
const byId=new Map(CARDS.map(c=>[c.id,c]));
const covered=new Set(); for(const L of lessons()) for(const st of L.stops) for(const r of (st.src||[])) covered.add(r);
const where={};
for(const sc of deck()) for(const P of sc.panels){ if(P.retired) continue;
  P.f.forEach((row,i)=>{ for(const c0 of (row[2]||[])){ const c=c0.replace(/#\d+$/,''); const w=(where[c]=where[c]||new Set());
    if(covered.has(P.id+'#'+i)) w.add('built'); else if(sc.id[0]==='d') w.add('d'); else w.add('pendS'); } }); }
const cls=id=>{ const w=where[id]; if(!w) return null; return w.has('built')?'built':w.has('pendS')?'pendS':'d'; };
// 부모(p) 기준: 자기 자신이 안 걸려 있어도 부모가 걸려 있으면 그 자리로 친다
const stat=c=>cls(c.id)||(c.p&&c.p!==c.id?cls(c.p):null)||'none';
const by={},ty={};
let sample=[];
for(const c of CARDS){ const s=stat(c); const ch=c.ch||'?';
  const b=(by[ch]=by[ch]||{tot:0,built:0,pendS:0,d:0,none:0,noneBase:0}); b.tot++; b[s]++; if(s==='none'&&c.t==='base') b.noneBase++;
  const t=(ty[c.t]=ty[c.t]||{tot:0,built:0,pendS:0,d:0,none:0}); t.tot++; t[s]++;
  if(s==='none'&&c.t==='base'&&sample.length<0) sample.push(c); }
console.log('종류별',JSON.stringify(ty));
const keys=Object.keys(by).sort((a,b)=>(parseInt(a)||999)-(parseInt(b)||999)||a.localeCompare(b));
let T={tot:0,built:0,pendS:0,d:0,none:0,noneBase:0};
console.log('장 | 전체 | 지은 과 | 남은 s | d | 그림 없음 | (그중 base)');
for(const k of keys){ const b=by[k]; for(const f in T) T[f]+=b[f]; console.log(`${k} | ${b.tot} | ${b.built} | ${b.pendS} | ${b.d} | ${b.none} | ${b.noneBase}`); }
console.log('합계',JSON.stringify(T));
// 부모가 다른 카드 수 / ru · 그 밖의 필드 표본
console.log('p!=id',CARDS.filter(c=>c.p&&c.p!==c.id).length, '필드',Object.keys(CARDS[0]).join(','), 'ru 분포',JSON.stringify(CARDS.reduce((a,c)=>(a[c.ru]=(a[c.ru]||0)+1,a),{})));
// 그림 없는 base 카드 가운데 8장(세포막) 표본 12개
const ex=CARDS.filter(c=>stat(c)==='none'&&c.t==='base'&&/^8 /.test(c.ch)).slice(0,12).map(c=>c.id+' | '+c.q.replace(/<[^>]+>/g,'').slice(0,60)+' → '+c.a.replace(/<[^>]+>/g,'').slice(0,50));
console.log(ex.join('\n'));
fs.writeFileSync('/tmp/claude-0/-home-claude/adba3dea-fd2a-5075-a226-d8c1b6963879/scratchpad/gpt/cardstat2.json',JSON.stringify({by,ty,T}));
