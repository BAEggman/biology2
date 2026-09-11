/* 「플래시카드 그림이 자동으로 나오지 않는다」 재현 (2026-09-11)
   가설: #picFix 는 hidden 상태에서 innerHTML 로 <img loading="lazy"> 를 심고 나서
         hidden 을 푼다. display:none 안에서 만들어진 lazy 이미지는 보이게 된 뒤에도
         곧바로 안 받아올 수 있다 — 스크롤·리사이즈가 와야 받는다. */
const { chromium, devices } = require('playwright');
const FILE = 'file://' + (process.argv[2] || '/tmp/b2/index.html');

async function run(label, ctxOpts, tap){
  const browser = await chromium.launch();
  const ctx = await browser.newContext(ctxOpts);
  const page = await ctx.newPage();
  await page.goto(FILE); await page.waitForTimeout(1500);
  await page.evaluate(()=>{ const b=document.getElementById('startBtn'); b.disabled=false; b.click(); });
  await page.waitForTimeout(400);

  // 그림 걸린 카드까지 진행
  let found=false;
  for(let i=0;i<400 && !found;i++){
    if(tap) await page.tap('.qcard'); else await page.click('.qcard',{position:{x:5,y:5}});
    await page.waitForTimeout(30);
    found = await page.evaluate(()=>!document.getElementById('picLink').classList.contains('hidden'));
    if(!found){ if(tap) await page.tap('.gbtn[data-g="5"]'); else await page.click('.gbtn[data-g="5"]'); await page.waitForTimeout(30); }
  }
  if(!found){ await browser.close(); return {label, err:'그림 카드 못 찾음'}; }

  if(tap) await page.tap('.gbtn[data-g="1"]'); else await page.click('.gbtn[data-g="1"]');

  const snap = async (ms)=>{ await page.waitForTimeout(ms);
    return await page.evaluate(()=>{
      const im=document.querySelector('#picFix img.pfimg');
      if(!im) return {img:false};
      const r=im.getBoundingClientRect();
      return { img:true, src:im.getAttribute('src'), loading:im.getAttribute('loading'),
               complete:im.complete, naturalW:im.naturalWidth,
               top:Math.round(r.top), h:Math.round(r.height),
               inView: r.top < innerHeight && r.bottom > 0, vh: innerHeight };
    }); };

  const t300 = await snap(300);
  const t1500 = await snap(1200);
  // 스크롤을 주면 받아오는가?
  await page.evaluate(()=>window.scrollBy(0,50));
  const tScroll = await snap(800);
  await browser.close();
  return {label, t300, t1500, tScroll};
}

(async()=>{
  console.log(JSON.stringify(await run('데스크톱 1440x900', {viewport:{width:1440,height:900}}, false), null, 1));
  console.log(JSON.stringify(await run('모바일 iPhone13', {...devices['iPhone 13'], isMobile:true, hasTouch:true}, true), null, 1));
})();
