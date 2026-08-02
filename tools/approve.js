#!/usr/bin/env node
/* approve.js — 승인 도구 HTML 생성 (제안 5)
   사용: node tools/approve.js [배치번호=1] [배치크기=40]
   출력: outputs/approve_N.html  — 열어서 그림을 누르고, 끝나면 결과를 복사해 붙여넣는다.

   마크다운 체크박스로 176장을 보는 건 고역이다. 그림을 보면 3초에 판정되는데
   제목만 읽으면 안 된다 — 그림을 띄운다. 이미지는 라이브에서 지연 로딩한다. */
const fs=require('fs'), path=require('path');
const ROOT=path.resolve(__dirname,'..');
const R=JSON.parse(fs.readFileSync(path.join(ROOT,'outputs/rank.json'),'utf8'));
const BATCH=parseInt(process.argv[2]||'1',10), SIZE=parseInt(process.argv[3]||'40',10);
const IMGBASE=process.env.IMGBASE||'https://baeggman.github.io/biology2/img/';

/* 대상: 격리(🧊) 전부 + lap 3~8 구간.
   격리는 가장 크게 무너진 것들이라 제일 먼저 붙어야 한다.
   앞서 이걸 뺐던 건 오판이었다 — 「그림이 걸린 카드가 더 많이 무너졌다」를
   그림이 무용하다는 뜻으로 읽었는데, 실제로는 스케치가 아직 완성이 안 된 것이다.
   그림이 부실해서 안 붙는 것과 그림이 안 걸려서 안 붙는 것은 다르다.
   빼는 건 lap 0~2 뿐이다 — 이미 붙고 있다.
   MODE=all 이면 전부, MODE=leech 면 격리만. */
const MODE=process.env.MODE||'both';
const inSet=r=> MODE==='all'   ? true
              : MODE==='leech' ? !!r.sus
              : (!!r.sus || (r.lap>=3 && r.lap<=8));
const pool=R.B.filter(inSet)
  .sort((a,b)=> (b.sus?1:0)-(a.sus?1:0) || b.lap-a.lap || b.rich-a.rich || b.wrong-a.wrong);
const items=pool.slice((BATCH-1)*SIZE, BATCH*SIZE);
if(!items.length){ console.error('그 배치엔 카드가 없다. 대상 '+pool.length+'장.'); process.exit(1); }
const nBatch=Math.ceil(pool.length/SIZE);

// 도해 패널은 이미지가 없다
const NOIMG=new Set(JSON.parse(fs.readFileSync(path.join(ROOT,'index.html'),'utf8')
  .match(/var PNOIMG=(\[.*?\]);/s)[1]));
const esc=s=>String(s==null?'':s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));

const cards=items.map((r,i)=>{
  const opts=r.cand.map(S=>`
    <div class="scene${S.weak?' weak':''}">
      <div class="shead">${esc(S.sid)} ${esc(S.scene)}${S.weak?' <em>⚠️ 챕터가 다르다</em>':''}
        <span class="hits">${S.hits.map(esc).join(' · ')}</span></div>
      <div class="panels">
        ${S.panels.map(p=>`
        <button class="p" data-card="${esc(r.id)}" data-pid="${esc(p.pid)}">
          ${NOIMG.has(p.pid)?'<div class="noimg">도해<br>(이미지 없음)</div>'
            :`<img loading="lazy" src="${IMGBASE}${esc(p.pid)}.webp" alt="">`}
          <div class="pt">${esc(p.t)}</div><div class="pid">${esc(p.pid)}</div>
        </button>`).join('')}
      </div>
    </div>`).join('');
  return `
  <section class="card" id="c${i}" data-card="${esc(r.id)}">
    <div class="hd"><span class="n">${(BATCH-1)*SIZE+i+1}</span>
      <code>${esc(r.id)}</code>
      <span class="m">🔴${r.rich} 💥${r.lap} ✗${r.wrong}/${r.n}${r.sus?' 🧊격리':''}</span>
      <span class="gate">${esc(r.g)} · ${esc(r.ch)}</span></div>
    <div class="q">${esc(r.q)}</div>
    <div class="a">${esc(r.a)}</div>
    ${opts}
    <div class="foot">
      <button class="none" data-card="${esc(r.id)}">해당 없음 — 이 카드엔 맞는 그림이 없다</button>
      <span class="pick" id="pick${i}"></span>
    </div>
  </section>`;
}).join('');

const html=`<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>승인 큐 ${BATCH}/${nBatch} — 그림↔카드</title>
<style>
:root{--ink:#1F2937;--ink2:#4B5563;--line:#E5E7EB;--amber:#F59E0B;--amber-l:#FFFBEB;
      --teal:#0F766E;--bg:#F8FAFC;--ok:#15803D}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:15px/1.6 -apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo","Malgun Gothic",sans-serif}
header{position:sticky;top:0;z-index:9;background:#fff;border-bottom:1px solid var(--line);padding:12px 16px;
  display:flex;gap:12px;align-items:center;flex-wrap:wrap}
h1{font-size:16px;margin:0;font-weight:800}
.bar{flex:1;min-width:120px;height:8px;background:var(--line);border-radius:99px;overflow:hidden}
.bar i{display:block;height:100%;background:var(--ok);width:0;transition:width .2s}
.cnt{font-size:13px;font-weight:700;color:var(--ink2)}
.btn{border:0;border-radius:10px;padding:9px 14px;font-size:14px;font-weight:800;cursor:pointer}
.btn-p{background:var(--teal);color:#fff}
main{max-width:960px;margin:0 auto;padding:16px}
.card{background:#fff;border:1px solid var(--line);border-radius:14px;padding:14px;margin-bottom:16px}
.card.done{border-color:var(--ok);box-shadow:inset 3px 0 0 var(--ok)}
.hd{display:flex;gap:8px;align-items:center;flex-wrap:wrap;font-size:12px;color:var(--ink2);margin-bottom:8px}
.n{background:var(--ink);color:#fff;border-radius:99px;padding:1px 9px;font-weight:800}
.hd code{background:#F1F5F9;padding:2px 7px;border-radius:6px;font-weight:700;color:var(--ink)}
.m{font-weight:700;color:#B45309}
.gate{margin-left:auto}
.q{font-size:16px;font-weight:800;line-height:1.5;word-break:keep-all}
.a{font-size:14px;color:var(--teal);font-weight:700;margin:4px 0 12px;word-break:keep-all}
.scene{border-top:1px dashed var(--line);padding-top:10px;margin-top:10px}
.scene.weak{opacity:.72}
.shead{font-size:13px;font-weight:800;color:#78350F;margin-bottom:8px}
.shead em{font-style:normal;font-weight:700;color:#B91C1C;font-size:11px}
.hits{display:block;font-weight:600;font-size:11px;color:var(--ink2);margin-top:2px}
.panels{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:10px}
button.p{border:2px solid var(--line);background:#fff;border-radius:12px;padding:6px;cursor:pointer;
  text-align:left;font:inherit;transition:.12s}
button.p:hover{border-color:var(--amber)}
button.p.on{border-color:var(--ok);background:#F0FDF4}
button.p.on .pt{color:var(--ok)}
button.p img,.noimg{width:100%;aspect-ratio:1;object-fit:cover;border-radius:8px;background:#F1F5F9;display:block}
.noimg{display:grid;place-items:center;font-size:12px;color:var(--ink2);text-align:center;font-weight:700}
.pt{font-size:12.5px;font-weight:700;margin-top:5px;line-height:1.35;word-break:keep-all}
.pid{font-size:11px;color:#94A3B8;font-family:ui-monospace,monospace}
.foot{display:flex;align-items:center;gap:10px;margin-top:12px;flex-wrap:wrap}
button.none{border:1px solid var(--line);background:#fff;border-radius:10px;padding:7px 12px;
  font:inherit;font-size:13px;color:var(--ink2);cursor:pointer}
button.none.on{background:#FEF2F2;border-color:#FCA5A5;color:#B91C1C;font-weight:700}
.pick{font-size:12px;font-weight:700;color:var(--ok)}
#out{position:sticky;bottom:0;background:#fff;border-top:2px solid var(--teal);padding:12px 16px}
#out textarea{width:100%;height:86px;font:12px ui-monospace,monospace;border:1px solid var(--line);
  border-radius:10px;padding:10px;resize:vertical}
.hint{font-size:12px;color:var(--ink2);margin-bottom:6px}
</style></head><body>
<header>
  <h1>승인 큐 ${BATCH} / ${nBatch}</h1>
  <div class="bar"><i id="bar"></i></div>
  <span class="cnt" id="cnt">0 / ${items.length}</span>
  <button class="btn btn-p" id="copy">결과 복사</button>
</header>
<main>
  <p class="hint"><b>격리(🧊) 전부 + 3~8번 무너진 것</b> — 가장 크게 무너진 순서다.
  <b>맞는 그림이 없으면 「해당 없음」이 정답이다</b> — 그게 곧 「이건 그려야 한다」는 뜻이고, 그 목록이 다음 작업이 된다.
  그림을 눌러 고른다. <b>여러 개 고를 수 있다</b> — 한 카드가 두 패널에 걸치는 경우가 있다.
  맞는 게 없으면 <b>해당 없음</b>. 진행은 자동 저장된다.</p>
  ${cards}
</main>
<div id="out">
  <div class="hint">다 고르면 아래를 통째로 복사해서 대화에 붙여넣는다.</div>
  <textarea id="res" readonly></textarea>
</div>
<script>
var KEY='approve_b${BATCH}';
var pick={};
try{ pick=JSON.parse(localStorage.getItem(KEY)||'{}'); }catch(e){}

function render(){
  document.querySelectorAll('button.p').forEach(function(b){
    var v=pick[b.dataset.card]||[];
    b.classList.toggle('on', v.indexOf(b.dataset.pid)>=0);
  });
  document.querySelectorAll('button.none').forEach(function(b){
    b.classList.toggle('on', (pick[b.dataset.card]||[]).length===0 && pick[b.dataset.card]!==undefined);
  });
  var done=0;
  document.querySelectorAll('section.card').forEach(function(s,i){
    var v=pick[s.dataset.card];
    var ok=v!==undefined; if(ok) done++;
    s.classList.toggle('done', ok);
    var el=document.getElementById('pick'+i);
    if(el) el.textContent = !ok?'' : (v.length? '✓ '+v.join(', ') : '— 해당 없음');
  });
  var n=document.querySelectorAll('section.card').length;
  document.getElementById('cnt').textContent=done+' / '+n;
  document.getElementById('bar').style.width=(done/n*100)+'%';
  var lines=[];
  document.querySelectorAll('section.card').forEach(function(s){
    var v=pick[s.dataset.card];
    if(v!==undefined) lines.push(s.dataset.card+'='+v.join(','));
  });
  document.getElementById('res').value='# 배치 ${BATCH}\\n'+lines.join('\\n');
  localStorage.setItem(KEY, JSON.stringify(pick));
}
document.addEventListener('click', function(e){
  var b=e.target.closest('button.p');
  if(b){ var c=b.dataset.card, v=pick[c]||[];
    var i=v.indexOf(b.dataset.pid);
    if(i>=0) v.splice(i,1); else v.push(b.dataset.pid);
    pick[c]=v; render(); return; }
  var nb=e.target.closest('button.none');
  if(nb){ var c2=nb.dataset.card;
    if(pick[c2]!==undefined && pick[c2].length===0) delete pick[c2]; else pick[c2]=[];
    render(); return; }
});
document.getElementById('copy').onclick=function(){
  var t=document.getElementById('res'); t.select();
  try{ document.execCommand('copy'); this.textContent='복사됨 ✓';
       var s=this; setTimeout(function(){ s.textContent='결과 복사'; },1500); }catch(e){}
};
render();
</script></body></html>`;

const out=path.join(ROOT,'outputs','approve_'+BATCH+'.html');
fs.mkdirSync(path.dirname(out),{recursive:true});
fs.writeFileSync(out, html);
const opts=items.reduce((a,r)=>a+r.cand.reduce((s,c)=>s+c.panels.length,0),0);
console.log(`대상 ${pool.length}장 (B ${R.B.length}장 중 · 격리 ${pool.filter(r=>r.sus).length} + lap3~8 ${pool.filter(r=>!r.sus).length})`);
console.log(`배치 ${BATCH}/${nBatch} — 카드 ${items.length}장 · 선택지 ${opts}개 (카드당 ${(opts/items.length).toFixed(1)})`);
console.log(`→ ${out}  (${(Buffer.byteLength(html)/1024).toFixed(0)}KB)`);
