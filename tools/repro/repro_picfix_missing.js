/* 「틀렸는데 복구 화면이 안 뜬다」 재현 (2026-09-11)
   등급 버튼 여섯 개를 각각 눌러 보고, 연속 오답에서도 매번 뜨는지 본다. */
const { chromium, devices } = require('playwright');
const FILE = 'file://' + (process.argv[2] || '/tmp/b2/index.html');

async function start(ctxOpts){
  const browser = await chromium.launch();
  const page = await (await browser.newContext(ctxOpts)).newPage();
  const errs=[]; page.on('pageerror',e=>errs.push(String(e).split('\n')[0]));
  await page.goto(FILE); await page.waitForTimeout(1200);
  await page.evaluate(()=>{ const b=document.getElementById('startBtn'); b.disabled=false; b.click(); });
  await page.waitForTimeout(300);
  return {browser, page, errs};
}
const vis = (page,id)=>page.evaluate(i=>!document.getElementById(i).classList.contains('hidden'), id);

/* ★ [2026-09-11] reveal() 에 시각 잠금(카드 표시 후 150ms · 복구 화면 닫은 뒤 450ms)이 있어
   기계 속도로 치면 「정답 보기」가 씹힌다. 사람처럼 기다렸다가, 안 펴졌으면 한 번 더 친다. */
async function revealCard(page, tap){
  for(let k=0;k<6;k++){
    await page.waitForTimeout(500);
    if(tap) await page.tap('.qcard'); else await page.click('.qcard',{position:{x:5,y:5}});
    await page.waitForTimeout(120);
    if(await vis(page,'grades')) return true;
  }
  return false;
}
async function toPicCard(page, tap){
  for(let i=0;i<500;i++){
    if(!await revealCard(page, tap)) return false;
    if(await vis(page,'picLink')) return true;
    if(tap) await page.tap('.gbtn[data-g="5"]'); else await page.click('.gbtn[data-g="5"]');
    await page.waitForTimeout(120);
  }
  return false;
}

(async()=>{
  // ① 등급별
  {
    const {browser,page,errs} = await start({viewport:{width:1440,height:900}});
    const res={};
    for(const g of ['0','1','2','3','4','5']){
      if(!await toPicCard(page,false)){ res[g]='그림카드 못찾음'; continue; }
      const shown = await page.evaluate(gg=>{ const b=document.querySelector('.gbtn[data-g="'+gg+'"]'); if(!b) return false; const r=b.getBoundingClientRect(); return r.width>0&&r.height>0; }, g);
      if(!shown){ res['g='+g]='버튼이 화면에 없음(이 카드에선 안 쓰임)'; continue; }
      await page.click(`.gbtn[data-g="${g}"]`); await page.waitForTimeout(250);
      const open = await vis(page,'picFix');
      res['g='+g] = open ? '복구 화면 뜸' : '안 뜸';
      if(open){ await page.click('#pfNext'); await page.waitForTimeout(200); }
    }
    console.log('① 등급별:', JSON.stringify(res), 'errors:', errs.slice(0,2));
    await browser.close();
  }
  // ② 연속 오답 5회
  {
    const {browser,page,errs} = await start({viewport:{width:1440,height:900}});
    const out=[];
    for(let n=1;n<=5;n++){
      if(!await toPicCard(page,false)){ out.push(n+':그림카드없음'); break; }
      await page.click('.gbtn[data-g="1"]'); await page.waitForTimeout(250);
      const open = await vis(page,'picFix');
      const hasImg = await page.evaluate(()=>!!document.querySelector('#picFix img.pfimg, #picFix .pfsvg svg'));
      out.push(n+':'+(open?'뜸':'✗안뜸')+(open?(hasImg?'/그림o':'/그림✗'):''));
      if(open){ await page.click('#pfNext'); await page.waitForTimeout(200); }
    }
    console.log('② 연속 오답:', out.join(' '), 'errors:', errs.slice(0,2));
    await browser.close();
  }
  // ③ 모바일 탭, 연속 오답 3회
  {
    const {browser,page,errs} = await start({...devices['iPhone 13'], isMobile:true, hasTouch:true});
    const out=[];
    for(let n=1;n<=3;n++){
      if(!await toPicCard(page,true)){ out.push(n+':그림카드없음'); break; }
      await page.tap('.gbtn[data-g="1"]'); await page.waitForTimeout(250);
      const open = await vis(page,'picFix');
      out.push(n+':'+(open?'뜸':'✗안뜸'));
      if(open){ await page.tap('#pfNext'); await page.waitForTimeout(200); }
    }
    console.log('③ 모바일:', out.join(' '), 'errors:', errs.slice(0,2));
    await browser.close();
  }
})();
