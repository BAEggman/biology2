#!/usr/bin/env node
/* ═══════════════════════════════════════════════════════════════════════
   apply.js — 승인 큐 결과를 sketchy.html에 주입한다 (제안 5)

   사용: node tools/apply.js <결과파일>            실제로 쓴다
        node tools/apply.js <결과파일> --check     쓰지 않고 검사만

   입력 (approve_N.html의 「결과 복사」를 그대로 붙여넣은 파일):
     # 배치 1
     B1-51=s31p01#2            ← 행 단위. f[2]의 셋째 자리에 들어간다 (PROW)
     G1-31=s12p01,s12p02       ← 패널 단위. pc에 들어간다 (PMAP만)
     X-BT-13=                  ← 해당 없음. 「그려야 할 그림」 목록으로 간다

   왜 텍스트를 직접 자르는가: sketchy.html이 13.7MB고 DATA는 손으로 쓴
   백틱 리터럴이다. 통째로 재직렬화하면 서식이 전부 날아가고 diff를 못 읽는다.
   그래서 괄호 스캐너로 해당 자리만 정확히 집어 고친다.

   저장은 끝에서 한 번에. 중간에 죽으면 원본이 그대로 남는다.
   ═══════════════════════════════════════════════════════════════════════ */
const fs=require('fs'), path=require('path');
const ROOT=path.resolve(__dirname,'..');
/* SKETCHY 환경변수로 대상 파일을 바꿀 수 있다 — 검증 스위트가 사본에 대고 돌린다 */
const SK=process.env.SKETCHY||path.join(ROOT,'sketchy.html'), IX=path.join(ROOT,'index.html');
const NEEDPIC=process.env.NEEDPIC||path.join(ROOT,'outputs/need_picture.md');
const CHECK=process.argv.includes('--check');
const SRC=process.argv[2];

const die=m=>{ console.error('\n❌ 중단 — '+m); process.exit(1); };
const rx=s=>s.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
/* 카드 ID는 큰따옴표로 넣는다 — 기존 pc가 그 형식이고 verify_build가 JSON.parse 한다.
   찾을 때는 두 형식을 다 본다 (손으로 넣은 작은따옴표가 섞여 있을 수 있다). */
const Q=cid=>'"'+cid+'"';
const HAS=cid=>new RegExp("['\"]"+rx(cid)+"['\"]");
if(!SRC || SRC.startsWith('--')) die('결과 파일 경로가 없다.  node tools/apply.js <파일>');
if(!fs.existsSync(SRC)) die('파일이 없다: '+SRC);

let sk=fs.readFileSync(SK,'utf8');
const ix=fs.readFileSync(IX,'utf8');

/* ── 괄호 스캐너 — 따옴표·백틱·이스케이프를 존중한다 ───────────────── */
function matchAt(src, st){                       // st = 여는 괄호 위치
  const open=src[st], close={'[':']','{':'}'}[open];
  if(!close) die('여는 괄호가 아니다: '+open);
  let d=0,q=null,esc=false;
  for(let k=st;k<src.length;k++){ const c=src[k];
    if(q){ if(esc){esc=false;continue} if(c==='\\'){esc=true;continue} if(c===q)q=null; continue }
    if(c==='"'||c==="'"||c==='`'){ q=c; continue }
    if(c===open)d++; else if(c===close){ d--; if(!d) return k; } }
  die('괄호가 안 맞는다 (from '+st+')');
}
/* 배열 리터럴의 최상위 원소 [시작,끝] 목록 */
function elems(src, lb){                          // lb = '[' 위치
  const rb=matchAt(src,lb); const out=[];
  let d=0,q=null,esc=false,start=null;
  for(let k=lb+1;k<rb;k++){ const c=src[k];
    if(q){ if(esc){esc=false;continue} if(c==='\\'){esc=true;continue} if(c===q)q=null; continue }
    if(c==='"'||c==="'"||c==='`'){ if(start===null)start=k; q=c; continue }
    if(c==='['||c==='{'){ if(d===0&&start===null)start=k; d++; continue }
    if(c===']'||c==='}'){ d--; continue }
    if(c===','&&d===0){ if(start!==null){ out.push([start,k]); start=null; } continue }
    if(d===0&&start===null&&!/\s/.test(c)) start=k; }
  if(start!==null) out.push([start,rb]);
  return out.map(([a,b])=>[a, b]);
}

/* ── 카드 ID 사전 ──────────────────────────────────────────────────── */
let CARDS;
try{ CARDS=JSON.parse(ix.match(/id=["']CARDS["'][^>]*>([\s\S]*?)<\/script>/)[1]); }
catch(e){ die('CARDS 파싱 실패: '+e.message); }
const CARDSET=new Set(CARDS.map(c=>c.id));
const CARDQ=new Map(CARDS.map(c=>[c.id,c.q||'']));

/* ── 입력 파싱 ─────────────────────────────────────────────────────── */
const lines=fs.readFileSync(SRC,'utf8').split(/\r?\n/);
const picks=[], none=[], bad=[];
for(const raw of lines){
  const ln=raw.trim();
  if(!ln || ln.startsWith('#')) continue;
  const m=ln.match(/^([A-Za-z0-9_.\-#]+)\s*=\s*(.*)$/);
  if(!m){ bad.push(ln); continue; }
  const cid=m[1], rhs=m[2].trim();
  if(!CARDSET.has(cid)){ bad.push(ln+'   ← 없는 카드 ID'); continue; }
  if(!rhs){ none.push(cid); continue; }
  for(const tok of rhs.split(',').map(x=>x.trim()).filter(Boolean)){
    const t=tok.match(/^([a-z]\d{2}p\d{2})(?:#(\d+))?$/);
    if(!t){ bad.push(ln+'   ← 알 수 없는 패널 표기: '+tok); continue; }
    picks.push({cid, pid:t[1], row:t[2]===undefined?null:parseInt(t[2],10)});
  }
}
if(bad.length) die('읽을 수 없는 줄 '+bad.length+'개:\n   '+bad.join('\n   '));

/* ── 주입 ──────────────────────────────────────────────────────────── */
/* 뒤에서 앞으로 고친다 — 앞을 고치면 뒤 오프셋이 밀린다.
   그래서 「할 일」을 먼저 전부 계산하고 위치 역순으로 적용한다. */
const jobs=[], skipped=[], added=[];

/* ⚠ 같은 자리에 카드 둘이 오면 한 번에 처리해야 한다.
   전에는 픽마다 독립적으로 「셋째 자리 신설」을 계산했다. 편집은 끝에서
   한꺼번에 적용되므로 두 픽이 같은 미수정 원본을 보고 각각 `,["A"]` `,["B"]`를
   예약했고, 결과가 ['소품','사실',["A"],["B"]] — 원소 4개짜리 행이 됐다.
   build.js가 거부해서 배포는 안 됐지만, 목표 단위로 먼저 묶는 게 옳다. */
const TGT=new Map();                              // "pid#row" 또는 "pid" → [카드,...]
for(const j of picks){
  const k=j.pid+(j.row===null?'':'#'+j.row);
  if(!TGT.has(k)) TGT.set(k,{pid:j.pid, row:j.row, cids:[]});
  const t=TGT.get(k);
  if(!t.cids.includes(j.cid)) t.cids.push(j.cid);
}

function panelSpan(pid){
  const key="{id:'"+pid+"'";
  const n=sk.split(key).length-1;
  if(n!==1) die(pid+': DATA에서 '+n+'번 나온다 (1 기대)');
  const st=sk.indexOf(key);
  return [st, matchAt(sk, st)];
}
function keyArray(pid, ps, pe, key){              // pc:[  또는  f:[
  const re=new RegExp('[,{]\\s*'+key+'\\s*:\\s*\\[');
  const seg=sk.slice(ps,pe+1); const m=seg.match(re);
  if(!m) return null;
  return ps + m.index + m[0].length - 1;          // '[' 위치
}
/* 배열 안에 넣을 목록을 만든다 — 이미 있는 건 빼고, 없으면 skipped에 남긴다 */
function fresh(cids, cur, where){
  const out=[];
  for(const cid of cids){
    if(HAS(cid).test(cur)) skipped.push(cid+' → '+where+' (이미 있다)');
    else { out.push(cid); added.push({cid, where}); }
  }
  return out;
}

for(const t of TGT.values()){
  const [ps,pe]=panelSpan(t.pid);
  if(t.row===null){
    /* ── 패널 단위 → pc ── */
    const lb=keyArray(t.pid,ps,pe,'pc');
    if(lb===null){                                 // pc가 아예 없다 → 새로 만든다
      const at=ps+("{id:'"+t.pid+"'").length;
      t.cids.forEach(c=>added.push({cid:c, where:t.pid}));
      jobs.push({at, del:0, ins:',pc:['+t.cids.map(Q).join(',')+']',
                 tag:t.cids.join(' · ')+' → '+t.pid+' (pc 신설)'});
      continue;
    }
    const rb=matchAt(sk,lb);
    const cur=sk.slice(lb,rb+1);
    const add=fresh(t.cids, cur, t.pid);
    if(!add.length) continue;
    const empty=/^\[\s*\]$/.test(cur);
    jobs.push({at:rb, del:0, ins:(empty?'':',')+add.map(Q).join(','),
               tag:add.join(' · ')+' → '+t.pid+' (pc)'});
  } else {
    /* ── 행 단위 → f[row][2] ── */
    const fb=keyArray(t.pid,ps,pe,'f');
    if(fb===null) die(t.pid+': 사실표(f)가 없는데 행을 지정했다');
    const rows=elems(sk,fb);
    if(t.row>=rows.length) die(t.pid+'#'+t.row+': 행이 '+rows.length+'개뿐이다');
    const [rs,re_]=rows[t.row];
    const cells=elems(sk,rs);
    if(cells.length<2) die(t.pid+'#'+t.row+': 행 형식이 이상하다 — '+sk.slice(rs,re_).slice(0,60));
    if(cells.length>3) die(t.pid+'#'+t.row+': 원소가 '+cells.length+'개다 (최대 3) — 이미 깨진 행이다');
    const where=t.pid+'#'+t.row;
    if(cells.length===3){
      const [cs]=cells[2];
      const lb2=sk.indexOf('[',cs);
      const rb2=matchAt(sk, lb2);
      const cur=sk.slice(lb2,rb2+1);
      if(!cur.trim().startsWith('[')) die(where+': 셋째 자리가 배열이 아니다');
      const add=fresh(t.cids, cur, where);
      if(!add.length) continue;
      const empty=/^\[\s*\]$/.test(cur);
      jobs.push({at:rb2, del:0, ins:(empty?'':',')+add.map(Q).join(','),
                 tag:add.join(' · ')+' → '+where});
    } else {
      t.cids.forEach(c=>added.push({cid:c, where}));
      const rb2=matchAt(sk, rs);                   // 행 배열의 ']'
      jobs.push({at:rb2, del:0, ins:',['+t.cids.map(Q).join(',')+']',
                 tag:t.cids.join(' · ')+' → '+where+' (셋째 자리 신설)'});
    }
    /* 같은 패널의 pc에 같은 카드가 있으면 뺀다 — 행이 이긴다 */
    const lb=keyArray(t.pid,ps,pe,'pc');
    if(lb!==null){
      const rb=matchAt(sk,lb);
      const cur=sk.slice(lb,rb+1);
      for(const cid of t.cids){
        const pat=new RegExp("\\s*,?\\s*['\"]"+rx(cid)+"['\"]\\s*,?");
        const mm=cur.match(pat);
        if(mm){
          const abs=lb+mm.index;
          let ins='';
          if(/^\s*,/.test(mm[0]) && /,\s*$/.test(mm[0])) ins=',';
          jobs.push({at:abs, del:mm[0].length, ins, tag:cid+' ← '+t.pid+'.pc 에서 제거 (행이 이긴다)'});
        }
      }
    }
  }
}

/* 위치 역순 적용 */
jobs.sort((a,b)=> b.at-a.at || b.del-a.del);
for(const jb of jobs) sk = sk.slice(0,jb.at) + jb.ins + sk.slice(jb.at+jb.del);

/* ── 검사 ──────────────────────────────────────────────────────────── */
if(sk.split('const DATA').length-1!==1) die('const DATA가 1개가 아니다');
if(sk.split('const IMG').length-1!==1) die('const IMG가 1개가 아니다');
try{ eval('('+sk.slice(sk.indexOf('[',sk.indexOf('const DATA')), matchAt(sk, sk.indexOf('[',sk.indexOf('const DATA')))+1)+')'); }
catch(e){ die('주입 후 DATA 파싱 실패 — 아무것도 안 썼다: '+e.message); }

/* ── 보고 ──────────────────────────────────────────────────────────── */
const nRow=added.filter(a=>a.where.includes('#')).length, nPan=added.length-nRow;
console.log('');
jobs.slice().reverse().forEach(j=>console.log('  ✓ '+j.tag));
if(skipped.length){ console.log(''); skipped.forEach(s=>console.log('  · '+s)); }
console.log('\n  주입 '+added.length+'건 — 행 단위 '+nRow+' · 패널 단위 '+nPan+' · 건너뜀 '+skipped.length);

if(CHECK){ console.log('\n  해당 없음 '+none.length+'건 (기록은 실제 실행 때)');
           console.log('\n✅ --check 통과 (아무것도 쓰지 않았다)'); process.exit(0); }

if(none.length){
  const out=NEEDPIC;
  fs.mkdirSync(path.dirname(out),{recursive:true});
  const prev=fs.existsSync(out)?fs.readFileSync(out,'utf8'):'# 그림이 필요한 카드 — 승인 큐에서 「해당 없음」이 나온 것\n\n맞는 그림이 없다고 판정된 카드다. 다음에 그릴 장면의 1차 후보가 된다.\n\n';
  const have=new Set((prev.match(/^- `([^`]+)`/gm)||[]).map(s=>s.slice(3,-1)));
  const add=none.filter(c=>!have.has(c));
  if(add.length) fs.writeFileSync(out, prev+add.map(c=>'- `'+c+'`  '+CARDQ.get(c)).join('\n')+'\n');
  console.log('  해당 없음 '+none.length+'건 → '+path.relative(ROOT,out)+' (신규 '+add.length+')');
}

fs.writeFileSync(SK, sk);
console.log('\n✅ sketchy.html 저장 — 이제 `npm run build && npm test`');
