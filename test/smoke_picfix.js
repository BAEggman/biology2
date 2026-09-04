const L=require('./_lib');
const FX=L.ensure();
/* 실제 UI 구동 스모크 — 세션을 시작해 오답을 매기고 복구 화면을 확인한다 */
const fs=require('fs'); const {JSDOM,VirtualConsole}=require('jsdom');
const FILE=process.argv[2]||require('path').join(L.ROOT,'index.html');
const vc=new VirtualConsole();
const errs=[];
vc.on('jsdomError',e=>{ const m=e.message.split('\n')[0]; if(!/scrollTo|Could not parse CSS/.test(m)) errs.push(m); });

const dom=new JSDOM(fs.readFileSync(FILE,'utf8'),
  {runScripts:'dangerously',pretendToBeVisual:true,url:'https://baeggman.github.io/biology2/',virtualConsole:vc});
const w=dom.window, d=w.document;
const $=id=>d.getElementById(id);
const vis=el=>el && !el.classList.contains('hidden');

let pass=0,fail=0;
const T=(n,f)=>{ try{ const m=f(); console.log('  ✓',n,m===undefined?'':'— '+m); pass++; }
                 catch(e){ console.log('  ✗',n,'—',e.message); fail++; } };

setTimeout(()=>{
  console.log('\n── 앱 구동 ──');
  T('치명적 런타임 에러 0', ()=>errs.length?(()=>{throw new Error(errs[0])})():'clean');
  T('홈 화면이 그려짐', ()=>{ const home=$('home');
    if(!vis(home)) throw new Error('home 숨김');
    if(!home.textContent.trim().length) throw new Error('빈 화면');
    return 'ok'; });

  console.log('\n── 세션 시작 → 오답 → 복구 화면 ──');
  T('시작 버튼 클릭', ()=>{ const b=$('startBtn');
    if(!b) throw new Error('startBtn 없음');
    b.disabled=false; b.click();
    if(!vis($('review'))) throw new Error('review 안 열림');
    return 'review 열림'; });

  // PMAP에 걸린 카드가 나올 때까지 진행하며 오답 처리
  let found=null, hops=0;
  T('그림 걸린 카드까지 진행', ()=>{
    for(hops=0; hops<400; hops++){
      const cur=$('rNum').textContent;
      // 현재 카드 id는 picLink 표시 여부로 판별
      d.querySelector('.qcard').click();                    // reveal
      const hasPic = vis($('picLink'));
      if(hasPic){ found=cur; return '카드 '+cur+' (그림 있음), '+hops+'장 만에'; }
      const btn=d.querySelector('.gbtn[data-g="5"]');       // 그림 없으면 정답 처리하고 넘김
      if(!btn) throw new Error('등급 버튼 없음');
      btn.click();
      if(!vis($('review'))) throw new Error('세션이 끝나버림 ('+hops+'장)');
    }
    throw new Error('400장 안에 그림 걸린 카드 없음');
  });

  T('❌ 그냥 틀림(1) → 복구 화면이 뜬다', ()=>{
    const before=$('rNum').textContent;
    d.querySelector('.gbtn[data-g="1"]').click();
    const box=$('picFix');
    if(!vis(box)) throw new Error('picFix 안 열림');
    if(vis($('grades'))) throw new Error('등급 버튼이 안 숨음');
    if($('rNum').textContent!==before) throw new Error('카드가 넘어가 버림');
    return '열림 · 등급숨김 · 카드 유지';
  });
  T('  이미지 태그 src가 img/*.webp', ()=>{
    const im=$('picFix').querySelector('img.pfimg');
    if(!im){
      /* [2026-08-21] 예전에는 여기서 그냥 통과시켰다 — 그래서 도해 판이 그림 없이
         복구되는 것을 460장이나 놓쳤다. 이제 인라인 SVG 가 있어야 통과한다. */
      const sv=$('picFix').querySelector('.pfsvg svg');
      if(!sv) throw new Error('그림도 도해도 없다 — 복구 화면에 볼 것이 사실표뿐이다');
      return '도해 패널 · 인라인 SVG';
    }
    if(!/^img\/\w+\.webp$/.test(im.getAttribute('src'))) throw new Error(im.getAttribute('src'));
    if(im.getAttribute('loading')!=='lazy') throw new Error('lazy 아님');
    return im.getAttribute('src');
  });
  T('  요약 + 사실표가 함께 있다', ()=>{
    const box=$('picFix');
    const rows=box.querySelectorAll('table.pftab tr').length;
    if(!rows) throw new Error('사실표 0행');
    if(!box.querySelector('.pfbr')) throw new Error('요약 없음');
    if(!box.querySelector('.pftit').textContent.trim()) throw new Error('제목 비어있음');
    return '사실표 '+rows+'행 · 요약 있음 · 제목 "'+box.querySelector('.pftit').textContent+'"';
  });
  T('  전체 장면 링크가 살아있는 패널을 가리킨다', ()=>{
    const a=$('picFix').querySelector('.pfmore');
    const pid=a.getAttribute('href').split('#')[1];
    const PTIT=JSON.parse(fs.readFileSync(FILE,'utf8').match(/var PTIT=(\{.*?\});/s)[1]);
    if(!PTIT[pid]) throw new Error('죽은 참조: '+pid);
    return pid+' → '+PTIT[pid];
  });

  T('Space 키로 계속 → 다음 카드 · ★ 그 카드의 정답은 숨겨져 있어야 한다', ()=>{
    const before=$('rNum').textContent;
    d.dispatchEvent(new w.KeyboardEvent('keydown',{key:' ',bubbles:true}));
    if(vis($('picFix'))) throw new Error('picFix 안 닫힘');
    if($('rNum').textContent===before) throw new Error('카드가 안 넘어감');
    /* [2026-09-04] 예전 줄은 「등급 버튼이 안 돌아옴」이면 실패였다 — 그것이 곧 버그(정답이 펴진 상태)를
       기대 동작으로 적어 둔 것이었다. 새 카드는 정답도 등급도 숨기고 힌트만 보여야 한다. */
    if(vis($('ansBlock'))) throw new Error('★ 다음 카드의 정답이 펴져 있다 (클릭 전파 버그)');
    if(vis($('grades'))) throw new Error('★ 다음 카드의 등급 버튼이 펴져 있다');
    if(!vis($('revealHint'))) throw new Error('정답 보기 힌트가 안 보인다');
    return before+' → '+$('rNum').textContent+' · 정답 숨김';
  });
  T('마우스로 「계속」 클릭 → 다음 카드 · ★ 정답 숨김', ()=>{
    /* 그림 걸린 카드를 하나 더 찾아 오답 처리하고, 이번에는 버튼을 직접 클릭한다 */
    for(let i=0;i<400;i++){
      d.querySelector('.qcard').click();
      if(vis($('picLink'))) break;
      d.querySelector('.gbtn[data-g="5"]').click();
      if(!vis($('review'))) throw new Error('세션이 끝나버림');
    }
    d.querySelector('.gbtn[data-g="1"]').click();
    if(!vis($('picFix'))) throw new Error('picFix 안 열림');
    const before=$('rNum').textContent;
    $('pfNext').click();                                   /* 실제 클릭 — 버블이 .qcard 까지 올라간다 */
    if($('rNum').textContent===before) throw new Error('카드가 안 넘어감');
    if(vis($('ansBlock'))) throw new Error('★ 다음 카드의 정답이 펴져 있다 (클릭 전파 버그)');
    if(vis($('grades'))) throw new Error('★ 등급 버튼이 펴져 있다');
    return before+' → '+$('rNum').textContent+' · 정답 숨김';
  });
  T('Space 자동 반복(e.repeat)은 정답을 펴지 않는다', ()=>{
    if(vis($('ansBlock'))) throw new Error('시작부터 펴져 있음');
    d.dispatchEvent(new w.KeyboardEvent('keydown',{key:' ',bubbles:true,repeat:true}));
    if(vis($('ansBlock'))) throw new Error('★ 반복 keydown 이 정답을 폈다');
    return '무시됨';
  });

  console.log('\n── 회귀: 정답이면 방해하지 않는다 ──');
  T('✅ 안 되짚음(5)은 복구 화면 없이 바로 넘어간다', ()=>{
    for(let i=0;i<60;i++){
      d.querySelector('.qcard').click();
      if(!vis($('picLink'))){ continue_: {} }
      const before=$('rNum').textContent;
      d.querySelector('.gbtn[data-g="5"]').click();
      if(vis($('picFix'))) throw new Error('정답인데 복구 화면이 떴다');
      if($('rNum').textContent===before && vis($('review'))) throw new Error('안 넘어감');
      return '정상 통과';
    }
    return 'ok';
  });

  T('설정에서 토글 끄면 안 뜬다', ()=>{
    const cb=$('fPicFix'); if(!cb) throw new Error('체크박스 없음');
    cb.checked=false; $('setSave').click();
    if(w.localStorage.getItem('bio_srs_v1')){
      const db=JSON.parse(w.localStorage.getItem('bio_srs_v1'));
      if(db.picFix!==0) throw new Error('DB.picFix='+db.picFix);
      return 'DB.picFix=0 저장됨';
    }
    throw new Error('localStorage 비어있음');
  });

  console.log('\n'+(fail?'❌':'✅')+' 스모크 통과 '+pass+' / 실패 '+fail);
  process.exit(fail?1:0);
}, 1200);
