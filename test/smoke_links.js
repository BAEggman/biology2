const L=require('./_lib');
const FX=L.ensure();
/* 제안 1 단독 구동 — 채점이 정상 진행되고 링크가 살아있는 패널을 가리키는지 */
const fs=require('fs'), {JSDOM,VirtualConsole}=require('jsdom');
const F=FX.STAGE1;
const vc=new VirtualConsole(); const errs=[];
vc.on('jsdomError',e=>{const m=e.message.split('\n')[0]; if(!/scrollTo|parse CSS/.test(m)) errs.push(m);});
const dom=new JSDOM(fs.readFileSync(F,'utf8'),{runScripts:'dangerously',pretendToBeVisual:true,url:'https://x.io/',virtualConsole:vc});
const w=dom.window,d=w.document,$=i=>d.getElementById(i);
const vis=e=>e&&!e.classList.contains('hidden');
let pass=0,fail=0;
const T=(n,f)=>{try{const m=f();console.log('  ✓',n,m===undefined?'':'— '+m);pass++;}catch(e){console.log('  ✗',n,'—',e.message);fail++;}};
const PTIT=JSON.parse(fs.readFileSync(F,'utf8').match(/var PTIT=(\{.*?\});/s)[1]);

setTimeout(()=>{
  console.log('\n── 제안 1 단독 구동 ──');
  T('런타임 에러 0', ()=>errs.length?(()=>{throw new Error(errs[0])})():'clean');
  T('세션 시작', ()=>{ const b=$('startBtn'); b.disabled=false; b.click();
    if(!vis($('review'))) throw new Error('안 열림'); return 'ok'; });

  let links=[], arrLink=null;
  T('30장 전부 채점하며 진행 (종전 동작 유지)', ()=>{
    let n=0;
    for(let i=0;i<400 && vis($('review'));i++){
      const before=$('rNum').textContent;
      d.querySelector('.qcard').click();
      if(vis($('picLink'))){
        const a=$('picLink');
        links.push({href:a.getAttribute('href'), text:a.textContent});
        if(a.textContent.includes(' + ')) arrLink=a.textContent;
      }
      d.querySelector('.gbtn[data-g="'+(i%2?1:5)+'"]').click();
      if(vis($('review')) && $('rNum').textContent===before) throw new Error('카드가 안 넘어감 @'+before);
      n++;
    }
    return n+'장 처리 · 그림 링크 '+links.length+'장';
  });
  T('링크 href가 전부 실재 패널', ()=>{
    const bad=links.map(l=>l.href.split('#')[1]).filter(p=>!PTIT[p]);
    if(bad.length) throw new Error('죽은 참조: '+bad.join(' '));
    return links.length+'장 전부 살아있음';
  });
  T('링크 텍스트에 ID가 그대로 노출된 것 없음', ()=>{
    const raw=links.filter(l=>/— s\d\dp\d\d|— d\d\dp\d\d/.test(l.text));
    if(raw.length) throw new Error(raw[0].text);
    return '0건';
  });
  T('배열 카드는 두 제목이 + 로 이어짐', ()=>arrLink||'이번 세션엔 안 나옴(스킵)');
  console.log('\n'+(fail?'❌':'✅')+' 제안1 스모크 '+pass+' / 실패 '+fail);
  process.exit(fail?1:0);
},1200);
