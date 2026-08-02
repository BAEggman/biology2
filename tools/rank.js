#!/usr/bin/env node
/* ═══════════════════════════════════════════════════════════════════
   rank.js — 실패율로 태깅 순서를 정한다 (제안 3)

   5,531장을 다 붙일 이유가 없다. 자주 틀리는 카드에만 그림이 필요하다.
   앱의 wrongRange() 와 같은 순서를 쓴다:  rich → lap → 최근 오답 → 등급

   사용: node rank.js <export.json> [상위N=400]
   출력: outputs/rank_*.md / *.json
   ═══════════════════════════════════════════════════════════════════ */
const fs=require('fs'), path=require('path');
const REPO=process.env.REPO||'/tmp/b2';
const EXPORT=process.argv[2];
const TOPN=parseInt(process.argv[3]||'400',10);
if(!EXPORT){ console.error('사용: node rank.js <export.json> [상위N]'); process.exit(1); }

const ix=fs.readFileSync(path.join(REPO,'index.html'),'utf8');
const CARDS=JSON.parse(ix.match(/id=["']CARDS["'][^>]*>([\s\S]*?)<\/script>/)[1]);
const IDX=new Map(CARDS.map(c=>[c.id,c]));
const PMAP=JSON.parse(ix.match(/var PMAP=(\{.*?\});/s)[1]);
const PTIT=JSON.parse(ix.match(/var PTIT=(\{.*?\});/s)[1]);
const PFACT=JSON.parse(ix.match(/var PFACT=(\{.*?\});/s)[1]);

const DB=JSON.parse(fs.readFileSync(EXPORT,'utf8'));
if(!DB.states) { console.error('states가 없다 — 올바른 export가 맞나?'); process.exit(1); }

/* ── 1. 카드별 실패 지표 ───────────────────────────────────────── */
const ev={};                                     // 카드 → 등급 이력
for(const d in (DB.log||{})) for(const e of DB.log[d]||[]){
  (ev[e.i]=ev[e.i]||[]).push({d, g:e.g});
}
const rows=[];
for(const id in DB.states){
  const s=DB.states[id], c=IDX.get(id);
  if(!c || !s || !s.seen) continue;
  const h=ev[id]||[];
  const n=h.length;
  const wrong=h.filter(x=>x.g<=1).length;        // 그냥 틀림 + 아는 줄 알았는데
  const shaky=h.filter(x=>x.g<=3).length;        // + 찍음 + 되짚음
  rows.push({
    id, g:c.g, gn:c.gn, ch:c.ch, t:c.t,
    q:(c.q||'').replace(/\s+/g,' '), a:(c.a||'').replace(/\s+/g,' '),
    rich:s.rich||0,                              // 확신 배신 (등급 0) 누적
    lap:s.lap||0,                                // 무너진 횟수
    box:s.box||1, ef:+(s.ef||0).toFixed(2), reps:s.reps||0,
    sus:s.sus?1:0,                               // leech 격리
    n, wrong, shaky,
    wr: n? +(wrong/n).toFixed(3) : 0,
    sr: n? +(shaky/n).toFixed(3) : 0,
    linked: !!PMAP[id],
  });
}

/* 앱의 wrongRange() 정렬과 동일하게 — rich → lap → 오답수 → 낮은 상자 */
rows.sort((a,b)=> b.rich-a.rich || b.lap-a.lap || b.wrong-a.wrong || a.box-b.box || b.sr-a.sr);

/* ── 2. 후보 패널 찾기 (연결 안 된 카드에 한해) ─────────────────── */
const chNum = s => (String(s||'').match(/^[\d·]+/)||[''])[0].split('·').filter(Boolean);
const PAN=[];                                     // 패널 → 게이트·챕터·용어
{
  const sk=fs.readFileSync(path.join(REPO,'sketchy.html'),'utf8');
  const st=sk.indexOf('[', sk.indexOf('const DATA'));
  let d=0,q=null,esc=false,DATA=null;
  for(let k=st;k<sk.length;k++){ const ch=sk[k];
    if(q){ if(esc){esc=false;continue} if(ch==='\\'){esc=true;continue} if(ch===q)q=null; continue }
    if(ch==='"'||ch==="'"||ch==='`'){ q=ch; continue }
    if(ch==='[')d++; else if(ch===']'){ d--; if(!d){ DATA=eval('('+sk.slice(st,k+1)+')'); break; } } }
  {
    const strip=t=>String(t||'').replace(/<[^>]*>/g,' ');
    for(const sc of DATA) for(const p of sc.panels)
      PAN.push({pid:p.id, gate:(sc.gate||'').split('·'), ch:chNum(sc.unit),
        title:sc.t+' · '+p.t,
        /* 사실표만 보면 재현율이 안 나온다. 다리 본문(br·bx)에 「최종 전자수용체」 같은
           말이 다 들어 있다 — 106패널 86,473자. 이걸 안 쓸 이유가 없다. */
        facts:(p.f||[]).map(r=>r[0]+' '+r[1]).join(' ')+' '+strip(p.br)+' '+strip(p.bx)+' '+p.t});
  }
}
/* 한국어라 토큰 비교가 안 된다 — 「전자전달계의」는 「전자전달계」와 다른 말로 잡힌다.
   그래서 사실표에서 용어 사전을 만들고, 카드 본문에 그 용어가 들어 있는지를 본다(부분일치).
   방향이 사실표 → 카드라 조사·어미가 붙어도 걸린다. */
const STRIP=/(으로써|으로서|에게서|이라는|라는|에서|에게|한테|처럼|같이|부터|까지|보다|으로|이나|이란|과의|와의|의|은|는|이|가|을|를|와|과|도|만|로|에|랑|나)$/;
const terms=t=>{
  const out=new Set();
  for(const w of String(t).match(/[가-힣]{2,}/g)||[]){
    out.add(w); const b=w.replace(STRIP,''); if(b.length>=2) out.add(b);
  }
  for(const w of String(t).match(/[A-Za-z][A-Za-z0-9₀-₉\-]{1,}/g)||[]) out.add(w);
  return out;
};
/* 사실표에 흔한 빈 말 — 소품 서술이 위치·수량·모양으로 되어 있어 이런 말이 많다.
   DF만으로는 안 걸러진다. 106패널 중 2~3곳에만 나오면 오히려 높은 가중을 받는다. */
const STOP=new Set(('마지막 처음 하나 둘 셋 넷 다섯 여섯 사람 사람이 인부 작업 오른쪽 왼쪽 가운데 '
 +'아래 위쪽 아래쪽 바깥 안쪽 모양 같은 다른 전부 각각 여럿 자리 방향 크기 색깔 그대로 '
 +'되는 하는 하고 있는 없는 만든 들고 나가는 들어 이것 저것 경우 상태 부분 전체 통째로 '
 +'개씩 개가 개를 번째 쪽으로 위에 밑에 옆에 안에 밖에 그림 표시 이름 서로 함께 다시 '
 +'무엇 에서 에게 으로 이나 하나씩 무슨 어떤 어느 얼마 언제 그것').split(' '));
const PTERM=new Map(PAN.map(p=>[p.pid,
  [...terms(p.facts)].filter(w=>w.length>=2 && !STOP.has(w))]));

/* 몇 개 패널에 등장하는 말인가 — 흔한 말은 값을 낮춘다 */
const DF={};
for(const p of PAN) for(const w of new Set(PTERM.get(p.pid))) DF[w]=(DF[w]||0)+1;
const weight=w=>Math.pow(w.length,0.9)/2.4 / Math.log2(2+(DF[w]||0));  // 긴 용어일수록 세게

/* ── 후보는 「패널」이 아니라 「장면」 단위로 낸다 ──────────────────
   패널을 단어 겹침으로 찍는 건 안 된다. 「전자전달계의 마지막에서 전자가
   무엇과 반응하는가」의 정답은 s32p02(최종 전자수용체 산소)인데, 가방-of-words로는
   s31p03·s31p04가 먼저 뜬다. 의미를 모르니 당연하다.

   그런데 「장면」은 게이트+챕터로 거의 항상 맞는다. 그리고 장면 안에서 어느 패널인지는
   제목만 봐도 사람이 3초에 안다 — 자기가 설계한 장면이니까.
   그래서 장면을 고르고 그 안의 패널을 전부 펼친다. 기계가 잘하는 일과
   사람이 잘하는 일을 갈랐다. */
function candidates(card){
  const text=(card.q||'')+' '+(card.a||'');
  const cch=chNum(card.ch);
  const pool=PAN.filter(p=>p.gate.includes(card.g) || cch.some(n=>p.ch.includes(n)));
  if(!pool.length) return [];

  const byScene={};
  for(const p of pool){
    const sid=p.pid.replace(/p\d+[ab]?$/,'');
    const hit=[...new Set(PTERM.get(p.pid))].filter(w=>text.includes(w));
    const sc=hit.reduce((a,w)=>a+weight(w),0);
    const S=byScene[sid]=byScene[sid]||{sid, scene:p.title.split(' · ')[0], best:0, panels:[], hits:new Set()};
    S.best=Math.max(S.best, sc);
    hit.forEach(w=>S.hits.add(w));
    S.panels.push({pid:p.pid, t:p.title.split(' · ').slice(1).join(' · '),
                   s:+sc.toFixed(2), linked:!!Object.values(PMAP).flat().includes(p.pid)});
  }
  return Object.values(byScene)
    .filter(S=>S.best>=0.8)
    .sort((a,b)=>b.best-a.best).slice(0,2)
    .map(S=>({...S, hits:(hs=>hs.filter(w=>!hs.some(v=>v!==w&&w.startsWith(v))))   /* 전자전달계의/전자전달계 중복 제거 */
                       ([...S.hits]).sort((x,y)=>weight(y)-weight(x)).slice(0,6),
              panels:S.panels.sort((a,b)=>a.pid.localeCompare(b.pid))}));
}

/* ── 3. 3분류 ──────────────────────────────────────────────────── */
const top=rows.slice(0, TOPN);
const A=[], B=[], C=[];                            // 이미 연결 / 후보 있음 / 후보 없음
for(const r of top){
  if(r.linked){ A.push(r); continue; }
  const cand=candidates(r);
  if(cand.length){ r.cand=cand; B.push(r); } else C.push(r);
}

/* ── 4. 출력 ───────────────────────────────────────────────────── */
const OUT=path.join(REPO,'outputs'); fs.mkdirSync(OUT,{recursive:true});
const pct=(x,y)=>y?((x/y*100).toFixed(1)+'%'):'—';

let md=`# 실패율 상위 ${TOPN}장 — 태깅 우선순위\n\n`;
md+=`학습한 카드 **${rows.length}**장 · 채점 이력 **${Object.values(ev).reduce((a,b)=>a+b.length,0)}**회\n\n`;
md+=`정렬은 앱의 \`wrongRange()\`와 같다 — **확신 배신(rich) → 무너짐(lap) → 오답수 → 낮은 상자**.\n\n`;
md+=`| 분류 | 장수 | 뜻 |\n|---|---|---|\n`;
md+=`| **A 이미 연결됨** | ${A.length} (${pct(A.length,top.length)}) | 그림이 이미 걸려 있다. 복구 화면이 이미 뜬다 |\n`;
md+=`| **B 후보 있음** | ${B.length} (${pct(B.length,top.length)}) | 붙일 그림 후보가 있다 → **승인만 하면 된다** |\n`;
md+=`| **C 후보 없음** | ${C.length} (${pct(C.length,top.length)}) | 대응할 그림이 없다 → **다음에 그릴 목록** |\n\n`;

// 게이트별 C(그림 없는 고실패) 집계 = 제작 우선순위
const cg={}; C.forEach(r=>{ cg[r.g]=cg[r.g]||{n:0,gn:r.gn,ch:{}}; cg[r.g].n++;
  cg[r.g].ch[r.ch]=(cg[r.g].ch[r.ch]||0)+1; });
md+=`## 그림 제작 우선순위 (C를 게이트별로)\n\n`;
md+=`고실패인데 그림이 없는 카드가 많은 곳이다. **지금까지는 흥미로운 주제부터 그렸다** — 여기가 데이터가 말하는 순서다.\n\n`;
md+=`| 게이트 | 고실패·무그림 | 몰려 있는 단원 |\n|---|---|---|\n`;
Object.entries(cg).sort((a,b)=>b[1].n-a[1].n).forEach(([g,v])=>{
  const chs=Object.entries(v.ch).sort((a,b)=>b[1]-a[1]).slice(0,3).map(([k,n])=>`${k}(${n})`).join(' · ');
  md+=`| ${g} ${v.gn} | **${v.n}** | ${chs} |\n`; });

md+=`\n## B — 승인 큐 (${B.length}장)\n\n`;
md+=`카드마다 **후보 장면 최대 2개**와 그 안의 패널을 전부 편다. 맞는 패널에 체크하면 된다.\n장면은 게이트+챕터로 거의 항상 맞는다. 어느 패널인지는 제목만 봐도 3초에 안다.\n`;
md+=`승인된 것만 \`pc\`에 넣고 \`npm run build\` 한다.\n\n`;
B.forEach((r,i)=>{
  md+=`### ${i+1}. \`${r.id}\`  ·  🔴${r.rich} 💥${r.lap} ✗${r.wrong}/${r.n}${r.sus?' · 🧊격리':''}\n`;
  md+=`**Q** ${r.q}\n**A** ${r.a}\n_${r.g} ${r.gn} · ${r.ch}_\n\n`;
  r.cand.forEach(S=>{
    md+=`**${S.sid} ${S.scene}**  _(겹친 말: ${S.hits.join(' · ')})_\n`;
    S.panels.forEach(p=>md+=`- [ ] \`${p.pid}\` ${p.t}\n`);
  });
  md+=`\n`;
});

md+=`\n## C — 그림 없음 (${C.length}장)\n\n`;
C.forEach(r=>md+=`- \`${r.id}\` 🔴${r.rich} 💥${r.lap} — ${r.q}  _(${r.g} · ${r.ch})_\n`);

md+=`\n## A — 이미 연결됨 (${A.length}장, 참고용)\n\n`;
A.forEach(r=>{ const p=Array.isArray(PMAP[r.id])?PMAP[r.id]:[PMAP[r.id]];
  md+=`- \`${r.id}\` 🔴${r.rich} 💥${r.lap} → ${p.map(x=>PTIT[x]||x).join(' + ')}\n`; });

const stamp=EXPORT.replace(/.*\//,'').replace(/\.json$/,'');
fs.writeFileSync(path.join(OUT,'rank.md'), md);
fs.writeFileSync(path.join(OUT,'rank.json'), JSON.stringify({top:TOPN,A,B,C},null,1));

console.log(`학습 ${rows.length}장 · 상위 ${TOPN} 분류 → A(연결됨) ${A.length} · B(후보있음) ${B.length} · C(그림없음) ${C.length}`);
console.log(`전체 연결률 ${rows.filter(r=>r.linked).length}/${rows.length} (${pct(rows.filter(r=>r.linked).length,rows.length)}) — 학습한 카드 기준`);
console.log(`→ ${path.join(OUT,'rank.md')}  (${(Buffer.byteLength(md)/1024).toFixed(0)}KB)`);
