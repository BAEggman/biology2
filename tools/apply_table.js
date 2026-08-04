#!/usr/bin/env node
/* ═══════════════════════════════════════════════════════════════════════
   apply_table.js — 정정된 사실표를 sketchy.html에 주입한다
   사용: node tools/apply_table.js <표파일.json>            실제로 쓴다
        node tools/apply_table.js <표파일.json> --check     쓰지 않고 검사만
   입력 JSON:
     { "s01p01": { "f": [["소품","사실"], ["소품","사실",["카드ID",…]], …],
                   "bxAdd":  "표에서 내린 내용 (선택)",
                   "bxBack": "그림을 고쳐 표로 되돌린 내용 (선택)",
                   "svgFile": "/경로/도해.svg — 도해 패널의 svg를 통째로 바꾼다 (선택)" }, … }
   왜 텍스트를 직접 자르는가: sketchy.html이 14MB고 DATA는 손으로 쓴
   백틱 리터럴이다. 통째로 재직렬화하면 서식이 전부 날아가 diff를 못 읽는다.
   apply.js와 같은 괄호 스캐너로 해당 자리만 정확히 집어 고친다.
   안전장치
     · 카드 ID가 CARDS에 없으면 중단한다
     · 원래 f에 있던 카드 ID가 새 f에서 사라지면 중단한다 (링크 유실 금지)
     · 행이 2~3원소가 아니거나 빈 칸이 있으면 중단한다
     · 파일 저장은 맨 끝에서 한 번. 중간에 죽으면 원본이 그대로 남는다
   ═══════════════════════════════════════════════════════════════════════ */
const fs=require('fs'), path=require('path');
const ROOT=path.resolve(__dirname,'..');
const SK=process.env.SKETCHY||path.join(ROOT,'sketchy.html');
const IX=process.env.INDEX||path.join(ROOT,'index.html');
const CHECK=process.argv.includes('--check');
const SRC=process.argv[2];
const die=m=>{ console.error('\n❌ 중단 — '+m); process.exit(1); };
if(!SRC || SRC.startsWith('--')) die('표 파일 경로가 없다.  node tools/apply_table.js <파일.json>');
if(!fs.existsSync(SRC)) die('파일이 없다: '+SRC);
let sk=fs.readFileSync(SK,'utf8');
/* ── 괄호 스캐너 — 따옴표·백틱·이스케이프를 존중한다 (apply.js와 동일) ── */
function matchAt(src, st){
  const open=src[st], close={'[':']','{':'}'}[open];
  if(!close) die('여는 괄호가 아니다: '+JSON.stringify(open)+' @'+st);
  let d=0,q=null,esc=false;
  for(let k=st;k<src.length;k++){ const c=src[k];
    if(q){ if(esc){esc=false;continue} if(c==='\\'){esc=true;continue} if(c===q)q=null; continue }
    if(c==='"'||c==="'"||c==='`'){ q=c; continue }
    if(c===open)d++; else if(c===close){ d--; if(!d) return k; } }
  die('괄호가 안 맞는다 (from '+st+')');
}
/* 객체 리터럴 안에서 최상위 `키:` 위치를 찾는다 (중첩 안으로 안 들어간다) */
function findKey(src, ob, key){
  const oe=matchAt(src,ob);
  let d=0,q=null,esc=false;
  for(let k=ob+1;k<oe;k++){ const c=src[k];
    if(q){ if(esc){esc=false;continue} if(c==='\\'){esc=true;continue} if(c===q)q=null; continue }
    if(c==='"'||c==="'"||c==='`'){ q=c; continue }
    if(c==='['||c==='{'){ d++; continue }
    if(c===']'||c==='}'){ d--; continue }
    if(d===0 && src.startsWith(key+':',k) && !/[A-Za-z0-9_$]/.test(src[k-1]||'')) return k+key.length+1;
  }
  return -1;
}
/* ── 카드 사전 ─────────────────────────────────────────────────────── */
let CARDSET;
try{
  const CARDS=JSON.parse(fs.readFileSync(IX,'utf8').match(/id=["']CARDS["'][^>]*>([\s\S]*?)<\/script>/)[1]);
  CARDSET=new Set(CARDS.map(c=>c.id));
}catch(e){ die('CARDS 파싱 실패: '+e.message); }
/* ── 입력 ──────────────────────────────────────────────────────────── */
let IN;
try{ IN=JSON.parse(fs.readFileSync(SRC,'utf8')); }catch(e){ die('입력 JSON 파싱 실패: '+e.message); }
/* bx는 백틱 리터럴 안에 들어간다. 마크다운 표기를 HTML로 바꾸고
   백틱·${ 를 남기지 않는다 — 하나만 새도 DATA 전체가 깨진다. */
function mdToHtml(s){
  return String(s)
    .replace(/\*\*([^*]+)\*\*/g,'<b>$1</b>')
    .replace(/`([^`]+)`/g,'<code>$1</code>')
    .replace(/`/g,'')          // 짝이 안 맞는 백틱
    .replace(/\$\{/g,'$&#123;') // 템플릿 치환 무력화
    .replace(/^\s*[-·]\s*/,'');
}
/* ── 검사 1: 행 형식·카드 존재 ─────────────────────────────────────── */
const bad=[];
for(const pid in IN){
  const f=IN[pid].f;
  if(!Array.isArray(f)||!f.length){ bad.push(pid+': f가 비었다'); continue; }
  f.forEach((r,i)=>{
    if(!Array.isArray(r)||r.length<2||r.length>3) bad.push(`${pid}#${i}: 원소가 ${Array.isArray(r)?r.length:'배열아님'}개다`);
    else{
      if(typeof r[0]!=='string'||!r[0].trim()) bad.push(`${pid}#${i}: 소품이 비었다`);
      if(typeof r[1]!=='string'||!r[1].trim()) bad.push(`${pid}#${i}: 사실이 비었다`);
      if(r.length===3){
        if(!Array.isArray(r[2])) bad.push(`${pid}#${i}: 셋째 원소가 배열이 아니다`);
        else for(const c of r[2]) if(!CARDSET.has(c)) bad.push(`${pid}#${i}: 덱에 없는 카드 ${c}`);
      }
    }
  });
}
if(bad.length) die('행 형식 오류 '+bad.length+'건\n  '+bad.slice(0,25).join('\n  '));
/* ── 패널 위치 찾기 + 검사 2: 링크 유실 ────────────────────────────── */
const jobs=[]; const lost=[]; const missing=[];
let nRowBefore=0, nRowAfter=0, nLink=0, nSvg=0;
for(const pid in IN){
  const re=new RegExp("\\{\\s*id\\s*:\\s*['\"]"+pid.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')+"['\"]\\s*,");
  const m=re.exec(sk);
  if(!m){ missing.push(pid); continue; }
  const ob=m.index;                                   // 패널 객체 여는 중괄호
  const fAt=findKey(sk,ob,'f');
  if(fAt<0){ missing.push(pid+' (f 없음)'); continue; }
  const lb=sk.indexOf('[',fAt), rb=matchAt(sk,lb);
  const oldF=eval('('+sk.slice(lb,rb+1)+')');
  nRowBefore+=oldF.length; nRowAfter+=IN[pid].f.length;
  const before=new Set(); for(const r of oldF) if(r[2]) for(const c of r[2]) before.add(c);
  const after =new Set(); for(const r of IN[pid].f) if(r[2]) for(const c of r[2]) after.add(c);
  for(const c of before) if(!after.has(c)) lost.push(pid+' → '+c);
  nLink+=after.size;
  /* 들여쓰기는 원본 f의 둘째 줄에서 가져온다 (없으면 7칸) */
  const seg=sk.slice(lb,rb+1);
  const im=seg.match(/\n(\s*)\[/);
  const ind=im?im[1]:'       ';
  const body=IN[pid].f.map(r=>{
    const parts=[JSON.stringify(r[0]), JSON.stringify(r[1])];
    if(r.length===3 && r[2].length) parts.push('['+r[2].map(c=>JSON.stringify(c)).join(',')+']');
    return '['+parts.join(',')+']';
  }).join(',\n'+ind);
  jobs.push({pid, at:lb, end:rb+1, text:'['+body+']'});
  /* bx 뒤에 문단을 붙인다 — bxAdd(표에서 내림) · bxBack(그림을 고쳐 되돌림) */
  const para=[];
  const bxAdd=mdToHtml((IN[pid].bxAdd||'').trim()).trim();
  if(bxAdd) para.push('<p><b>표에서 내린 것 (그림에 대응 소품이 없다).</b> '+bxAdd+'</p>');
  const bxBack=mdToHtml((IN[pid].bxBack||'').trim()).trim();
  if(bxBack) para.push('<p><b>도해를 고쳐 표로 되돌린 것.</b> '+bxBack+'</p>');
  if(para.length){
    const bxAt=findKey(sk,ob,'bx');
    if(bxAt<0){ missing.push(pid+' (bx 없음 — 문단 추가 건너뜀)'); }
    else{
      const qs=sk.indexOf('`',bxAt);
      if(qs<0 || qs>bxAt+4){ missing.push(pid+' (bx가 백틱이 아니다 — 문단 추가 건너뜀)'); }
      else{
        let qe=qs+1, esc=false;
        for(;qe<sk.length;qe++){ const c=sk[qe];
          if(esc){esc=false;continue} if(c==='\\'){esc=true;continue}
          if(c==='$'&&sk[qe+1]==='{') die(pid+' bx에 템플릿 치환이 있다 — 손으로 확인하라');
          if(c==='`') break; }
        const html=para.join('');
        if(/[`]/.test(html) || /\$\{/.test(html)) die(pid+' bx 추가문에 백틱/템플릿이 남았다: '+html.slice(0,120));
        jobs.push({pid, at:qe, end:qe, text:html});
      }
    }
  }
  /* 도해 교체 — svgFile 경로가 오면 그 파일 내용으로 svg 리터럴을 통째 바꾼다 */
  if(IN[pid].svgFile){
    const nv=fs.readFileSync(IN[pid].svgFile,'utf8').trim();
    if(!/^<svg[\s>]/.test(nv)) die(pid+' svgFile이 <svg>로 시작하지 않는다: '+IN[pid].svgFile);
    if(/[`]/.test(nv) || /\$\{/.test(nv)) die(pid+' svgFile에 백틱/템플릿이 있다 — DATA가 깨진다');
    const at=findKey(sk,ob,'svg');
    if(at<0) die(pid+': svg 키가 없다 (도해가 아니다)');
    const qs=sk.indexOf('`',at);
    if(qs<0 || qs>at+4) die(pid+': svg가 백틱 리터럴이 아니다');
    let qe=qs+1, esc=false;
    for(;qe<sk.length;qe++){ const c=sk[qe];
      if(esc){esc=false;continue} if(c==='\\'){esc=true;continue} if(c==='`') break; }
    jobs.push({pid, at:qs, end:qe+1, text:'`'+nv+'`'});
    nSvg++;
  }
}
if(missing.length) die('패널을 못 찾았다 '+missing.length+'건\n  '+missing.join('\n  '));
if(lost.length)    die('링크 유실 '+lost.length+'건 — 어느 행으로 옮길지 정하고 다시 넣어라\n  '+lost.join('\n  '));
/* ── 적용 (뒤에서부터) ─────────────────────────────────────────────── */
jobs.sort((a,b)=>b.at-a.at);
for(const j of jobs) sk=sk.slice(0,j.at)+j.text+sk.slice(j.end);
/* ── 검사 3: 고친 결과가 실제로 파싱되는가 (한 글자만 새도 DATA 전체가 죽는다) ── */
let PARSED;
try{
  const st=sk.indexOf('[', sk.indexOf('const DATA'));
  let d=0,q=null,esc=false,end=-1;
  for(let k=st;k<sk.length;k++){ const c=sk[k];
    if(q){ if(esc){esc=false;continue} if(c==='\\'){esc=true;continue} if(c===q)q=null; continue }
    if(c==='"'||c==="'"||c==='`'){ q=c; continue }
    if(c==='[')d++; else if(c===']'){ d--; if(!d){ end=k; break; } } }
  if(end<0) throw new Error('DATA 배열이 안 닫힌다');
  PARSED=eval('('+sk.slice(st,end+1)+')');
}catch(e){ die('고친 결과가 파싱되지 않는다: '+e.message+'\n  (원본은 손대지 않았다)'); }
const gotPanels=PARSED.reduce((s,x)=>s+x.panels.length,0);
const gotRows=PARSED.reduce((s,x)=>s+x.panels.reduce((t,p)=>t+(p.f||[]).length,0),0);
if(gotRows!==nRowAfter-0+ (PARSED.reduce((s,x)=>s+x.panels.filter(p=>!IN[p.id]).reduce((t,p)=>t+(p.f||[]).length,0),0)))
  die(`재파싱 행 수가 안 맞는다: ${gotRows}`);
console.log(`재파싱 확인 — 장면 ${PARSED.length} · 패널 ${gotPanels} · 행 ${gotRows}`);
console.log(`패널 ${Object.keys(IN).length}장 · 행 ${nRowBefore} → ${nRowAfter} · 카드 링크 ${nLink}개 보존`);
console.log(`bx 문단 ${jobs.filter(j=>j.at===j.end).length}건 · 도해 교체 ${nSvg}건 · 편집 ${jobs.length}곳`);
if(CHECK){ console.log('\n--check — 쓰지 않았다.'); process.exit(0); }
/* 되돌리기용 사본 */
const bak=SK+'.bak';
fs.writeFileSync(bak, fs.readFileSync(SK));
fs.writeFileSync(SK, sk);
console.log('\n✅ '+path.basename(SK)+' 갱신. 되돌리려면: mv '+path.basename(bak)+' '+path.basename(SK));
console.log('   다음: npm run build && npm test');
