#!/usr/bin/env node
/* ═══════════════════════════════════════════════════════════════════════
   build.js — sketchy.html(사실표)에서 index.html(SRS)의 연결 지도를 생성한다.

   왜 있는가: PMAP을 손으로 관리하던 동안 v9에서 멈췄다. 그 사이 패널을 쪼개고
   장면을 12장 더 그렸는데 지도는 그대로였고, 16장이 없는 패널을 가리켰다.
   이제 지도는 손으로 고치는 물건이 아니다. 사실표가 유일한 소스이고 여기서 생성된다.

   단일 소스 (sketchy.html의 DATA)
     panels[].pc : ['G1-31', ...]           패널 단위 링크
     panels[].f  : [소품, 사실, ['G1-44']]   셋째 자리 = 행 단위 링크 (선택)

   생성물 (index.html의 BUILD 구간)
     PMAP  카드 → 패널(문자열 또는 배열)     — 「그림으로 보기」와 복구 화면 발동
     PROW  카드 → {패널: [행번호,...]}        — 복구 화면에서 해당 행을 강조
     PTIT  패널 → 제목
     PBR   패널 → 요약
     PFACT 패널 → 사실표
     PNOIMG 이미지 없는 패널(도해)

   검증에 걸리면 아무것도 안 쓰고 죽는다. 조용히 썩지 않는 게 목적이다.
   사용: node build.js [--check]      --check 는 쓰지 않고 검사만
   ═══════════════════════════════════════════════════════════════════════ */
const fs=require('fs'), path=require('path');
const ROOT=__dirname;
const SK=path.join(ROOT,'sketchy.html'), IX=path.join(ROOT,'index.html');
const REPORT=path.join(ROOT,'links_report.md'), IMGDIR=path.join(ROOT,'img');
const CHECK=process.argv.includes('--check');

const die=m=>{ console.error('\n❌ 빌드 중단 — '+m); process.exit(1); };
const log=m=>console.log(m);

/* ── 1. 원본 읽기 ──────────────────────────────────────────────────── */
const sk=fs.readFileSync(SK,'utf8'), ix=fs.readFileSync(IX,'utf8');

function balanced(src, from, open, close){
  const st=src.indexOf(open, from); let d=0,q=null,esc=false;
  for(let k=st;k<src.length;k++){ const c=src[k];
    if(q){ if(esc){esc=false;continue} if(c==='\\'){esc=true;continue} if(c===q)q=null; continue }
    if(c==='"'||c==="'"||c==='`'){ q=c; continue }
    if(c===open)d++; else if(c===close){ d--; if(!d) return src.slice(st,k+1); } }
  die('DATA 괄호가 안 맞는다');
}
let DATA;
try { DATA = eval('('+balanced(sk, sk.indexOf('const DATA'), '[', ']')+')'); }
catch(e){ die('DATA 파싱 실패: '+e.message); }

let CARDS;
try { CARDS = JSON.parse(ix.match(/id=["']CARDS["'][^>]*>([\s\S]*?)<\/script>/)[1]); }
catch(e){ die('CARDS 파싱 실패: '+e.message); }
const CARD=new Map(CARDS.map(c=>[c.id,c]));

/* ── 2. 순회하며 지도 생성 + 검증 ──────────────────────────────────── */
const PMAP={}, PROW={}, PTIT={}, PBR={}, PFACT={};
const errs=[], warns=[], report=[];
const seenPanel=new Set();
let nRowLinks=0, nPanelLinks=0, nRows=0;

for(const sc of DATA){
  for(const p of sc.panels){
    if(seenPanel.has(p.id)) errs.push('패널 ID 중복: '+p.id);
    seenPanel.add(p.id);
    PTIT[p.id]=sc.t+' · '+p.t;
    if(p.br) PBR[p.id]=p.br;
    const f=p.f||[];
    if(f.length) PFACT[p.id]=f.map(r=>[r[0],r[1]]);
    nRows+=f.length;

    const lines=[];
    const attach=(cid, rowIdx)=>{
      if(!CARD.has(cid)){ errs.push(`${p.id}: 없는 카드 ID "${cid}"`); return; }
      if(!PMAP[cid]) PMAP[cid]=[];
      if(!PMAP[cid].includes(p.id)) PMAP[cid].push(p.id);
      if(rowIdx!=null){
        (PROW[cid]=PROW[cid]||{});
        (PROW[cid][p.id]=PROW[cid][p.id]||[]);
        if(!PROW[cid][p.id].includes(rowIdx)) PROW[cid][p.id].push(rowIdx);
        nRowLinks++;
      } else nPanelLinks++;
      const c=CARD.get(cid);
      lines.push({ rowIdx, cid, prop: rowIdx!=null ? f[rowIdx][0] : null, q:(c.q||'').replace(/\s+/g,' ') });
    };

    // 소품명 유일성 — 행 단위 링크의 안전장치
    const props=f.map(r=>r[0]), dup=props.filter((x,i)=>props.indexOf(x)!==i);
    if(dup.length) warns.push(`${p.id}: 소품명 중복 [${[...new Set(dup)].join(' / ')}]`);

    (p.pc||[]).forEach(cid=>attach(cid,null));
    f.forEach((r,i)=>{
      if(r.length>3) errs.push(`${p.id} 행${i}: 요소가 ${r.length}개다 (최대 3)`);
      if(r[2]!=null){
        if(!Array.isArray(r[2])) return errs.push(`${p.id} 행${i}: 셋째 자리는 배열이어야 한다`);
        r[2].forEach(cid=>attach(cid,i));
      }
    });

    if(lines.length){
      lines.sort((a,b)=>(a.rowIdx==null?-1:a.rowIdx)-(b.rowIdx==null?-1:b.rowIdx)||a.cid.localeCompare(b.cid));
      report.push({pid:p.id, title:PTIT[p.id], lines});
    }
  }
}

// 같은 카드가 한 패널에 pc와 행으로 동시에 걸리면 행이 이긴다 (pc는 「아직 안 정한 것」이므로)
let demoted=0;
for(const cid in PROW) for(const pid in PROW[cid]){
  const sc=DATA.find(s=>s.panels.some(p=>p.id===pid));
  const p=sc.panels.find(p=>p.id===pid);
  if((p.pc||[]).includes(cid)) demoted++;
}
if(demoted) warns.push(`pc와 행에 동시에 걸린 링크 ${demoted}건 — 제안 5에서 pc에서 빼면 된다`);

const ALL=[...seenPanel];
const NOIMG=ALL.filter(p=>!fs.existsSync(path.join(IMGDIR,p+'.webp'))).sort();
NOIMG.filter(p=>!/^d\d/.test(p)).forEach(p=>errs.push(`이미지 파일 없음: img/${p}.webp`));

// PMAP 값 정규화 — 1개면 문자열, 여러 개면 배열 (렌더가 둘 다 받는다)
for(const cid in PMAP){ PMAP[cid].sort(); if(PMAP[cid].length===1) PMAP[cid]=PMAP[cid][0]; }

/* ── 3. 판정 ───────────────────────────────────────────────────────── */
log(`장면 ${DATA.length} · 패널 ${ALL.length} · 사실표 ${nRows}행 · 이미지 ${ALL.length-NOIMG.length}`);
log(`연결 카드 ${Object.keys(PMAP).length}/${CARDS.length} (${(Object.keys(PMAP).length/CARDS.length*100).toFixed(2)}%)`
   +` · 패널단위 ${nPanelLinks} · 행단위 ${nRowLinks}`);
const covered=new Set(Object.values(PMAP).flatMap(v=>Array.isArray(v)?v:[v]));
log(`카드가 걸린 패널 ${covered.size}/${ALL.length} · 고아 ${ALL.length-covered.size}`);
warns.forEach(w=>log('  ⚠ '+w));
if(errs.length){ errs.slice(0,20).forEach(e=>console.error('  ✗ '+e));
  die(`오류 ${errs.length}건`); }

/* ── 4. 주입 ───────────────────────────────────────────────────────── */
const block='/*BUILD:START — build.js 생성물. 손으로 고치지 말 것. 사실표(sketchy.html)를 고치고 다시 돌린다.*/'
 +'var PMAP='+JSON.stringify(PMAP)
 +';var PROW='+JSON.stringify(PROW)
 +';var PTIT='+JSON.stringify(PTIT)
 +';var PBR='+JSON.stringify(PBR)
 +';var PFACT='+JSON.stringify(PFACT)
 +';var PNOIMG='+JSON.stringify(NOIMG)+';/*BUILD:END*/';

let out;
if(ix.includes('/*BUILD:START')){
  out=ix.replace(/\/\*BUILD:START[\s\S]*?BUILD:END\*\//, ()=>block);
} else {
  const m=ix.match(/<script>\/\* v9: 시각 니모닉 딥링크 \*\/[\s\S]*?<\/script>/);
  if(!m) die('주입 지점을 못 찾았다 (BUILD 마커도 v9 블록도 없다)');
  out=ix.replace(m[0], ()=>'<script>'+block+'</script>');
}
if(out===ix && !CHECK) log('  (index.html 변경 없음 — 이미 최신)');

/* ── 5. 읽을 수 있는 리포트 ────────────────────────────────────────── */
const gate={}; CARDS.forEach(c=>{ gate[c.g]=gate[c.g]||{n:0,l:0,gn:c.gn}; gate[c.g].n++; if(PMAP[c.id])gate[c.g].l++; });
let md='# 그림 ↔ 카드 연결 현황\n\n';
md+='> `build.js` 생성물이다. 손으로 고치지 말고 `sketchy.html`의 사실표를 고친 뒤 다시 빌드한다.\n';
md+='> sketchy.html은 13.88MB라 git diff를 못 읽는다. **태깅 검수는 이 파일로 한다.**\n\n';
md+=`- 연결 카드 **${Object.keys(PMAP).length} / ${CARDS.length}** (${(Object.keys(PMAP).length/CARDS.length*100).toFixed(2)}%)\n`;
md+=`- 패널 단위 ${nPanelLinks}건 · **행 단위 ${nRowLinks}건**\n`;
md+=`- 카드가 걸린 패널 ${covered.size}/${ALL.length} · 고아 ${ALL.length-covered.size}\n\n`;
md+='## 게이트별\n\n| 게이트 | 카드 | 연결 | 비율 |\n|---|---|---|---|\n';
Object.keys(gate).sort().forEach(g=>{ const v=gate[g];
  md+=`| ${g} ${v.gn} | ${v.n} | ${v.l} | ${(v.l/v.n*100).toFixed(1)}% |\n`; });
md+='\n## 고아 패널 (카드 0장)\n\n';
const orph=ALL.filter(p=>!covered.has(p));
md+=orph.length ? orph.map(p=>`- \`${p}\` ${PTIT[p]}`).join('\n')+'\n' : '없음\n';
md+='\n## 패널별 링크\n\n`[패널]`은 아직 행이 안 정해진 것이다. 제안 5에서 행으로 내린다.\n\n';
report.sort((a,b)=>a.pid.localeCompare(b.pid)).forEach(r=>{
  md+=`### \`${r.pid}\` ${r.title}\n\n`;
  r.lines.forEach(l=>{ md+= l.rowIdx==null
    ? `- [패널] \`${l.cid}\` ${l.q}\n`
    : `- [행${l.rowIdx} · ${l.prop}] \`${l.cid}\` ${l.q}\n`; });
  md+='\n';
});

/* ── 6. 쓰기 ───────────────────────────────────────────────────────── */
if(CHECK){ log('\n✅ --check 통과 (아무것도 쓰지 않았다)'); process.exit(0); }
fs.writeFileSync(IX,out); fs.writeFileSync(REPORT,md);
log(`\n✅ index.html 갱신 (${(Buffer.byteLength(out)/1048576).toFixed(2)}MB) · links_report.md ${(Buffer.byteLength(md)/1024).toFixed(0)}KB`);
