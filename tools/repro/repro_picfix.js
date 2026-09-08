/* 실제 브라우저에서 「그림 복구 → 계속 → 다음 카드」를 재현한다.
   jsdom 스모크는 통과하는데 사용자는 여전히 정답이 펴진다고 한다 —
   진짜 클릭·진짜 탭(터치)에서만 나는 길이 있는지 본다. */
const { chromium, devices } = require('playwright');
const FILE = 'file://' + (process.argv[2] || '/tmp/b2/index.html');

async function run(label, ctxOpts, tap) {
  const browser = await chromium.launch();
  const ctx = await browser.newContext(ctxOpts);
  const page = await ctx.newPage();
  const errs = [];
  page.on('pageerror', e => errs.push(String(e).split('\n')[0]));
  await page.goto(FILE);
  await page.waitForTimeout(1500);
  const out = { label, errs };

  await page.evaluate(() => { const b = document.getElementById('startBtn'); b.disabled = false; b.click(); });
  await page.waitForTimeout(400);
  out.reviewOpen = await page.evaluate(() => !document.getElementById('review').classList.contains('hidden'));

  // 그림 걸린 카드를 찾을 때까지 진행
  let found = false;
  for (let i = 0; i < 400 && !found; i++) {
    if (tap) await page.tap('.qcard'); else await page.click('.qcard', { position: { x: 5, y: 5 } });
    await page.waitForTimeout(30);
    found = await page.evaluate(() => !document.getElementById('picLink').classList.contains('hidden'));
    if (!found) {
      if (tap) await page.tap('.gbtn[data-g="5"]'); else await page.click('.gbtn[data-g="5"]');
      await page.waitForTimeout(30);
    }
  }
  out.foundPicCard = found;
  if (!found) { await browser.close(); return out; }

  if (tap) await page.tap('.gbtn[data-g="1"]'); else await page.click('.gbtn[data-g="1"]');
  await page.waitForTimeout(200);
  out.picFixOpen = await page.evaluate(() => !document.getElementById('picFix').classList.contains('hidden'));
  out.numBefore = await page.evaluate(() => document.getElementById('rNum').textContent);

  // 「계속」 — 진짜 마우스 클릭 / 진짜 탭
  if (tap) await page.tap('#pfNext'); else await page.click('#pfNext');
  await page.waitForTimeout(400);

  Object.assign(out, await page.evaluate(() => {
    const v = id => !document.getElementById(id).classList.contains('hidden');
    return { numAfter: document.getElementById('rNum').textContent,
             ansVisible: v('ansBlock'), gradesVisible: v('grades'),
             hintVisible: v('revealHint'), revealedFlag: window.revealed };
  }));
  await browser.close();
  return out;
}

(async () => {
  console.log(JSON.stringify(await run('데스크톱 마우스', {}, false), null, 1));
  console.log(JSON.stringify(await run('모바일 탭', { ...devices['iPhone 13'], isMobile: true, hasTouch: true }, true), null, 1));
})();
