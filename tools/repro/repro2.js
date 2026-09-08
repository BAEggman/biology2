/* 두 번째 재현 — 사용자가 실제로 하는 조작에 가깝게:
   ① Space 로 정답 보기 → 숫자키로 채점 → Space 로 「계속」 → 이어서 한 번 더 Space (빠른 연타)
   ② 「계속」을 더블클릭
   ③ 모바일에서 「계속」을 빠르게 두 번 탭 */
const { chromium, devices } = require('playwright');
const FILE = 'file://' + (process.argv[2] || '/tmp/b2/index.html');

async function setup(ctxOpts) {
  const browser = await chromium.launch();
  const ctx = await browser.newContext(ctxOpts);
  const page = await ctx.newPage();
  await page.goto(FILE);
  await page.waitForTimeout(1500);
  await page.evaluate(() => { const b = document.getElementById('startBtn'); b.disabled = false; b.click(); });
  await page.waitForTimeout(300);
  return { browser, page };
}
const state = page => page.evaluate(() => {
  const v = id => !document.getElementById(id).classList.contains('hidden');
  return { num: document.getElementById('rNum').textContent, ans: v('ansBlock'), grades: v('grades'),
           hint: v('revealHint'), picFix: v('picFix') };
});

async function toPicCard(page, tap) {
  for (let i = 0; i < 400; i++) {
    if (tap) await page.tap('.qcard'); else await page.keyboard.press('Space');
    await page.waitForTimeout(25);
    const has = await page.evaluate(() => !document.getElementById('picLink').classList.contains('hidden'));
    if (has) return true;
    if (tap) await page.tap('.gbtn[data-g="5"]'); else await page.keyboard.press('1');
    await page.waitForTimeout(25);
  }
  return false;
}

(async () => {
  // ① 키보드 연타
  {
    const { browser, page } = await setup({});
    await toPicCard(page, false);
    await page.keyboard.press('4');            // 🔴 아는 줄 알았는데 → 복구 화면
    await page.waitForTimeout(200);
    const before = await state(page);
    await page.keyboard.press('Space');        // 계속
    await page.waitForTimeout(90);
    await page.keyboard.press('Space');        // 손가락이 한 번 더 (빠른 연타)
    await page.waitForTimeout(300);
    console.log('① Space 연타  before=', JSON.stringify(before), '\n            after =', JSON.stringify(await state(page)));
    await browser.close();
  }
  // ② 더블클릭
  {
    const { browser, page } = await setup({});
    for (let i = 0; i < 400; i++) {
      await page.click('.qcard', { position: { x: 5, y: 5 } });
      await page.waitForTimeout(25);
      if (await page.evaluate(() => !document.getElementById('picLink').classList.contains('hidden'))) break;
      await page.click('.gbtn[data-g="5"]'); await page.waitForTimeout(25);
    }
    await page.click('.gbtn[data-g="1"]'); await page.waitForTimeout(200);
    const before = await state(page);
    await page.dblclick('#pfNext');
    await page.waitForTimeout(300);
    console.log('② 더블클릭    before=', JSON.stringify(before), '\n            after =', JSON.stringify(await state(page)));
    await browser.close();
  }
  // ③ 모바일 두 번 탭
  {
    const { browser, page } = await setup({ ...devices['iPhone 13'], isMobile: true, hasTouch: true });
    await toPicCard(page, true);
    await page.tap('.gbtn[data-g="1"]'); await page.waitForTimeout(200);
    const before = await state(page);
    await page.tap('#pfNext');
    await page.waitForTimeout(80);
    await page.touchscreen.tap(180, 300);      // 화면 가운데를 한 번 더
    await page.waitForTimeout(300);
    console.log('③ 두 번 탭    before=', JSON.stringify(before), '\n            after =', JSON.stringify(await state(page)));
    await browser.close();
  }
})();
