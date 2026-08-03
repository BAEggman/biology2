#!/usr/bin/env node
/* ═══════════════════════════════════════════════════════════════════
   orphan.js — 고아 패널 전용 큐. 방향이 반대다.

   승인 큐(approve.js)는 「자주 틀리는 카드」에서 출발해 그림을 찾는다.
   그래서 상위 실패에 안 걸린 주제의 그림은 영원히 고아로 남는다 —
   s31p04 발효·코리회로, s32p01·p02 전자전달계, s33p01 당신생처럼
   핵심인데 아직 크게 무너지지 않은 것들이다.

   이 도구는 「그림」에서 출발해 카드를 찾는다.
   사실표 한 행마다 그 행의 용어를 담은 카드 후보를 붙여 보여준다.
   행 단위로 나오므로 승인하면 곧바로 PROW가 된다.

   사용: node tools/orphan.js [행당후보=3] [패널당후보=6]
   출력: outputs/orphan.html   —  결과 형식은 승인 큐와 같다 (apply.js가 먹는다)
   ═══════════════════════════════════════════════════════════════════ */
const fs=require('fs'), path=require('path');
const {terms, STOP, chNum, strip, parseDATA}=require('./_terms');
const ROOT=path.resolve(__dirname,'..');
const PERROW=parseInt(process.argv[2]||'3',10), PERPANEL=parseInt(process.argv[3]||'6',10);
const IMGBASE=process.env.IMGBASE||'https://baeggman.github.io/biology2/img/';

const ix=fs.readFileSync(path.join(ROOT,'index.html'),'utf8');
const sk=fs.readFileSync(path.join(ROOT,'sketchy.html'),'utf8');
const CARDS=JSON.parse(ix.match(/id=["']CARDS["'][^>]*>([\s\S]*?)<\/script>/)[1]);
const PMAP =JSON.parse(ix.match(/var PMAP=(\{.*?\});/s)[1]);
const NOIMG=new Set(JSON.parse(ix.match(/var PNOIMG=(\[.*?\]);/s)[1]));
const DATA=parseDATA(sk);

/* ── 1. 고아 패널 = PMAP이 한 번도 가리키지 않는 패널 ───────────── */
const covered=new Set(Object.values(PMAP).flatMap(v=>Array.isArray(v)?v:[v]));
const PAN=[];
for(const sc of DATA) for(const p of sc.panels)
  PAN.push({pid:p.id, sid:sc.id, scene:sc.t, t:p.t, gate:(sc.gate||'').split('·'),
            ch:chNum(sc.unit), unit:sc.unit||'', br:p.br||'', f:p.f||[],
            text:(p.f||[]).map(r=>r[0]+' '+r[1]).join(' ')+' '+strip(p.br)+' '+strip(p.bx)+' '+p.t});
const orphans=PAN.filter(p=>!covered.has(p.pid));
if(!orphans.length){ console.log('고아 패널이 없다.'); process.exit(0); }

/* ── 2. 용어 가중치 — rank.js와 같은 식 ─────────────────────────── */
const PTERM=new Map(PAN.map(p=>[p.pid,[...terms(p.text)].filter(w=>w.length>=2 && !STOP.has(w))]));
const DF={};
for(const p of PAN) for(const w of new Set(PTERM.get(p.pid))) DF[w]=(DF[w]||0)+1;
const weight=w=>Math.pow(w.length,0.9)/2.4 / Math.log2(2+(DF[w]||0));

/* ── 3. 패널마다 후보 카드 찾기 ──────────────────────────────────
   챕터가 게이트를 이긴다(rank.js와 같은 판단). 이미 어딘가에 걸린 카드는 뺀다 —
   고아를 없애는 게 목적인데 이미 그림이 있는 카드를 또 붙이면 값이 없다. */
const CTEXT=new Map(CARDS.map(c=>[c.id,((c.q||'')+' '+(c.a||'')).replace(/\s+/g,' ')]));
const REALGATE=new Set(CARDS.map(c=>c.g));
/* 같은 장면의 형제 패널에 실제로 걸린 카드들의 게이트 — 경험적 신호다.
   s23·s27·s30은 gate 필드에 게이트 문자 대신 챕터 번호("48","49","53")가 들어 있어
   게이트 폴백이 통째로 죽는다. 형제가 이미 B·G 카드를 걸고 있으면 그게 진짜 게이트다. */
const SIBG={};
for(const cid in PMAP){
  const arr=Array.isArray(PMAP[cid])?PMAP[cid]:[PMAP[cid]];
  const g=(CARDS.find(c=>c.id===cid)||{}).g; if(!g) continue;
  arr.forEach(pid=>{ const sid=pid.replace(/p\d+[ab]?$/,''); (SIBG[sid]=SIBG[sid]||new Set()).add(g); });
}
function pool(p){
  const byCh=CARDS.filter(c=>chNum(c.ch).some(n=>p.ch.includes(n)));
  if(p.ch.length && byCh.length) return byCh.filter(c=>!PMAP[c.id]);
  const g1=p.gate.filter(g=>REALGATE.has(g));
  if(g1.length) return CARDS.filter(c=>g1.includes(c.g) && !PMAP[c.id]);
  const g2=SIBG[p.sid];                       // 형제가 거는 게이트로 되짚는다
  if(g2 && g2.size) return CARDS.filter(c=>g2.has(c.g) && !PMAP[c.id]);
  return [];
}
function score(text, cid){
  const t=CTEXT.get(cid);
  let s=0, hit=[];
  for(const w of new Set([...terms(text)].filter(x=>x.length>=2 && !STOP.has(x))))
    if(t.includes(w)){ s+=weight(w); hit.push(w); }
  return {s:+s.toFixed(2), hit};
}

const esc=s=>String(s==null?'':s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let nOpt=0;
const blocks=orphans.map((p,pi)=>{
  const P=pool(p);
  const used=new Set();
  const rows=p.f.map((r,ri)=>{
    const txt=r[0]+' '+r[1];
    const cands=P.map(c=>({c, ...score(txt,c.id)}))
      .filter(x=>x.s>=0.85).sort((a,b)=>b.s-a.s).slice(0,PERROW);
    cands.forEach(x=>used.add(x.c.id));
    nOpt+=cands.length;
    return `<tr class="frow"><td class="fp">${esc(r[0])}</td><td class="ff">${esc(r[1])}
      <div class="cands">${cands.length?cands.map(x=>`
        <button class="cd" data-card="${esc(x.c.id)}" data-pid="${esc(p.pid)}" data-row="${ri}">
          <code>${esc(x.c.id)}</code> ${esc(x.c.q)}
          <em>${esc(x.c.a)}</em></button>`).join(''):'<span class="no">후보 없음</span>'}</div>
    </td></tr>`;
  }).join('');
  /* 행에 안 걸렸지만 패널 전체와는 맞는 카드 — 어느 행인지 애매한 경우용 */
  const wide=P.filter(c=>!used.has(c.id)).map(c=>({c, ...score(p.text,c.id)}))
    .filter(x=>x.s>=1.9).sort((a,b)=>b.s-a.s).slice(0,PERPANEL);
  nOpt+=wide.length;
  return `
  <section class="pn" id="p${pi}" data-pid="${esc(p.pid)}">
    <div class="hd"><span class="n">${pi+1}</span><code>${esc(p.pid)}</code>
      <b>${esc(p.scene)}</b> · ${esc(p.t)}
      <span class="unit">${esc(p.unit)}</span><span class="pool">후보 풀 ${P.length}장</span></div>
    <div class="body">
      <div class="im">${NOIMG.has(p.pid)?'<div class="noimg">도해<br>(이미지 없음)</div>'
        :`<img loading="lazy" src="${IMGBASE}${esc(p.pid)}.webp" alt="">`}
        <div class="br">${p.br}</div></div>
      <table>${rows}</table>
    </div>
    ${wide.length?`<div class="wide"><div class="wh">행은 못 정하겠지만 이 그림과 맞는 카드 — 패널 통째로 건다</div>
      ${wide.map(x=>`<button class="cd w" data-card="${esc(x.c.id)}" data-pid="${esc(p.pid)}" data-row="">
        <code>${esc(x.c.id)}</code> ${esc(x.c.q)}<em>${esc(x.c.a)}</em></button>`).join('')}</div>`:''}
    <div class="foot"><span class="pick" id="pick${pi}"></span></div>
  </section>`;
}).join('');

const html=`<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>고아 패널 큐 — 그림 ${orphans.length}장</title>
<style>
:root{--ink:#1F2937;--ink2:#4B5563;--line:#E5E7EB;--amber:#F59E0B;--teal:#0F766E;--bg:#F8FAFC;--ok:#15803D}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.6 -apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo","Malgun Gothic",sans-serif}
header{position:sticky;top:0;z-index:9;background:#fff;border-bottom:1px solid var(--line);padding:12px 16px;display:flex;gap:12px;align-items:center;flex-wrap:wrap}
h1{font-size:16px;margin:0;font-weight:800}
.bar{flex:1;min-width:120px;height:8px;background:var(--line);border-radius:99px;overflow:hidden}
.bar i{display:block;height:100%;background:var(--ok);width:0;transition:width .2s}
.cnt{font-size:13px;font-weight:700;color:var(--ink2)}
.btn{border:0;border-radius:10px;padding:9px 14px;font-size:14px;font-weight:800;cursor:pointer;background:var(--teal);color:#fff}
main{max-width:1080px;margin:0 auto;padding:16px}
.hint{font-size:13px;color:var(--ink2);background:#FFFBEB;border:1px solid #FDE68A;border-radius:10px;padding:10px 12px;margin-bottom:14px;word-break:keep-all}
.pn{background:#fff;border:1px solid var(--line);border-radius:14px;padding:14px;margin-bottom:16px}
.pn.done{border-color:var(--ok);box-shadow:inset 3px 0 0 var(--ok)}
.hd{display:flex;gap:8px;align-items:center;flex-wrap:wrap;font-size:13px;margin-bottom:10px}
.n{background:var(--ink);color:#fff;border-radius:99px;padding:1px 9px;font-weight:800;font-size:12px}
.hd code{background:#F1F5F9;padding:2px 7px;border-radius:6px;font-weight:700;font-size:12px}
.unit{color:var(--ink2);font-size:12px}
.pool{margin-left:auto;color:#94A3B8;font-size:12px}
.body{display:grid;grid-template-columns:230px 1fr;gap:14px;align-items:start}
.im img,.noimg{width:100%;aspect-ratio:1;object-fit:cover;border-radius:10px;background:#F1F5F9;display:block}
.noimg{display:grid;place-items:center;font-size:12px;color:var(--ink2);font-weight:700;text-align:center}
.im .br{font-size:12px;line-height:1.5;background:#FEF3C7;border-radius:8px;padding:8px;margin-top:8px;word-break:keep-all}
table{width:100%;border-collapse:collapse}
td{border-top:1px solid var(--line);padding:6px 6px;vertical-align:top;word-break:keep-all;font-size:13px}
.fp{color:#92400E;font-weight:700;width:30%}
.cands{display:flex;flex-direction:column;gap:5px;margin-top:6px}
.no{font-size:11px;color:#CBD5E1}
button.cd{display:block;width:100%;text-align:left;font:inherit;font-size:12.5px;line-height:1.45;
  border:1.5px solid var(--line);background:#FCFCFD;border-radius:9px;padding:6px 9px;cursor:pointer;word-break:keep-all}
button.cd:hover{border-color:var(--amber);background:#FFFBEB}
button.cd.on{border-color:var(--ok);background:#F0FDF4}
button.cd code{background:#F1F5F9;padding:1px 5px;border-radius:5px;font-size:11px;font-weight:700;margin-right:5px}
button.cd em{display:block;font-style:normal;color:var(--teal);font-weight:700;font-size:11.5px;margin-top:2px}
button.cd.on code{background:#DCFCE7}
.wide{margin-top:12px;border-top:1px dashed var(--line);padding-top:10px;display:flex;flex-direction:column;gap:5px}
.wh{font-size:12px;font-weight:700;color:var(--ink2)}
.foot{margin-top:10px;font-size:12px;font-weight:700;color:var(--ok);min-height:18px}
#out{position:sticky;bottom:0;background:#fff;border-top:2px solid var(--teal);padding:12px 16px}
#out textarea{width:100%;height:90px;font:12px ui-monospace,monospace;border:1px solid var(--line);border-radius:10px;padding:10px}
@media(max-width:760px){.body{grid-template-columns:1fr}}
</style></head><body>
<header>
  <h1>고아 패널 ${orphans.length}장</h1>
  <div class="bar"><i id="bar"></i></div>
  <span class="cnt" id="cnt">0 / ${orphans.length}</span>
  <button class="btn" id="copy">결과 복사</button>
</header>
<main>
  <p class="hint"><b>방향이 반대다.</b> 승인 큐는 「자주 틀리는 카드」에서 출발했다 —
  그래서 아직 크게 무너지지 않은 주제의 그림은 영영 안 걸린다. 여기 있는 ${orphans.length}장은
  <b>앱에서 아예 도달할 수 없는 그림</b>이다. 발효·전자전달계·당신생 같은 핵심이 섞여 있다.<br>
  각 <b>사실 행 아래에 그 행의 용어를 담은 카드 후보</b>를 붙였다. 맞으면 누른다 — 그대로 행 단위 링크가 된다.
  맞는 게 하나도 없으면 그냥 넘긴다. <b>후보 풀에서 이미 그림이 걸린 카드는 뺐다.</b></p>
  ${blocks}
</main>
<div id="out">
  <div class="hint" style="background:none;border:0;padding:0;margin:0 0 6px">다 고르면 아래를 통째로 복사해 대화에 붙여넣는다.</div>
  <textarea id="res" readonly></textarea>
</div>
<script>
var KEY='orphan_q1';
var pick={};
try{ pick=JSON.parse(localStorage.getItem(KEY)||'{}'); }catch(e){}
function key(b){ return b.dataset.pid + (b.dataset.row===''?'':'#'+b.dataset.row); }
function render(){
  document.querySelectorAll('button.cd').forEach(function(b){
    var v=pick[b.dataset.card]||[];
    b.classList.toggle('on', v.indexOf(key(b))>=0);
  });
  var done=0, n=document.querySelectorAll('section.pn').length;
  document.querySelectorAll('section.pn').forEach(function(s,i){
    var pid=s.dataset.pid, got=[];
    for(var c in pick) (pick[c]||[]).forEach(function(k){
      if(k===pid||k.indexOf(pid+'#')===0) got.push(c+'→'+k);
    });
    if(got.length) done++;
    s.classList.toggle('done', got.length>0);
    var el=document.getElementById('pick'+i);
    if(el) el.textContent=got.length?('✓ '+got.join('  ')):'';
  });
  document.getElementById('cnt').textContent=done+' / '+n;
  document.getElementById('bar').style.width=(done/n*100)+'%';
  var lines=[];
  Object.keys(pick).sort().forEach(function(c){ if((pick[c]||[]).length) lines.push(c+'='+pick[c].join(',')); });
  document.getElementById('res').value='# 고아 패널 큐\\n'+lines.join('\\n');
  localStorage.setItem(KEY, JSON.stringify(pick));
}
document.addEventListener('click', function(e){
  var b=e.target.closest('button.cd'); if(!b) return;
  var c=b.dataset.card, k=key(b), v=pick[c]||[];
  var i=v.indexOf(k);
  if(i>=0) v.splice(i,1); else v.push(k);
  if(v.length) pick[c]=v; else delete pick[c];
  render();
});
document.getElementById('copy').onclick=function(){
  var t=document.getElementById('res'); t.select();
  try{ document.execCommand('copy'); this.textContent='복사됨 ✓';
       var s=this; setTimeout(function(){ s.textContent='결과 복사'; },1500); }catch(e){}
};
render();
</script></body></html>`;

const out=path.join(ROOT,'outputs','orphan.html');
fs.mkdirSync(path.dirname(out),{recursive:true});
fs.writeFileSync(out, html);
console.log(`고아 패널 ${orphans.length}장 · 후보 ${nOpt}개 (패널당 ${(nOpt/orphans.length).toFixed(1)})`);
orphans.forEach(p=>console.log('  '+p.pid+'  '+p.scene+' · '+p.t));
console.log(`→ ${out}  (${(Buffer.byteLength(html)/1024).toFixed(0)}KB)`);
