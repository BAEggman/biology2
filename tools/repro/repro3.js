/* 잠금이 정상 조작까지 막지 않는지 — 「계속」 뒤 0.6초 기다렸다 Space → 정답이 펴져야 한다 */
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch(); const page = await (await browser.newContext()).newPage();
  await page.goto('file:///tmp/b2/index.html'); await page.waitForTimeout(1500);
  await page.evaluate(() => { const b=document.getElementById('startBtn'); b.disabled=false; b.click(); });
  await page.waitForTimeout(300);
  for (let i=0;i<400;i++){ await page.keyboard.press('Space'); await page.waitForTimeout(30);
    if (await page.evaluate(()=>!document.getElementById('picLink').classList.contains('hidden'))) break;
    await page.keyboard.press('1'); await page.waitForTimeout(30); }
  await page.keyboard.press('4'); await page.waitForTimeout(200);
  await page.keyboard.press('Space');            // 계속
  await page.waitForTimeout(600);                // 사람이 새 문제를 읽는 시간
  await page.keyboard.press('Space');            // 정답 보기
  await page.waitForTimeout(200);
  const v = id => page.evaluate(i=>!document.getElementById(i).classList.contains('hidden'), id);
  console.log('0.6초 뒤 Space → 정답:', await v('ansBlock'), '· 등급:', await v('grades'));
  // 카드 넘긴 직후 150ms 안쪽도 확인
  await page.keyboard.press('1'); await page.waitForTimeout(40);
  console.log('채점 직후 40ms Space 전 상태 정답:', await v('ansBlock'));
  await page.keyboard.press('Space'); await page.waitForTimeout(60);
  console.log('  40ms 뒤 Space → 정답:', await v('ansBlock'), '(막혀야 정상)');
  await page.waitForTimeout(300); await page.keyboard.press('Space'); await page.waitForTimeout(150);
  console.log('  다시 Space → 정답:', await v('ansBlock'), '(펴져야 정상)');
  await browser.close();
})();
