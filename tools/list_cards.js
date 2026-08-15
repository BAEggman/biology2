// 카드 연결 상태를 본다. PMAP(build.js가 만든 권위 있는 지도)을 그대로 쓴다.
//   node tools/list_cards.js '<ID 정규식>' [un|li]
// ★ 정규식으로 sketchy.html을 훑어 연결 여부를 판정하면 안 된다 —
//   S-SG-1 · X-BT-4 처럼 접두어에 붙임표가 든 카드 447장을 놓친다(2026-08-15 발견).
const fs = require('fs');
const h = fs.readFileSync(__dirname + '/../index.html', 'utf8');
const CARDS = JSON.parse(h.match(/<script id="CARDS"[^>]*>([\s\S]*?)<\/script>/)[1]);
const PMAP = JSON.parse(h.match(/var PMAP=(\{.*?\});/s)[1]);
const re = new RegExp(process.argv[2] || '.');
const only = process.argv[3];
const flat = v => Array.isArray(v) ? v.join('|') : v;
let n = 0, li = 0;
for (const c of CARDS) {
  if (!re.test(c.id)) continue;
  const p = PMAP[c.id];
  if (only === 'un' && p) continue;
  if (only === 'li' && !p) continue;
  n++; if (p) li++;
  const s = t => String(t || '').replace(/<[^>]*>/g, '').replace(/\s+/g, ' ').trim();
  console.log((p ? '●' + flat(p) : '○       ') + '  ' + c.id + ' | ' + s(c.q) + ' || ' + s(c.a));
}
console.log('총 ' + n + (only ? '' : ' (연결 ' + li + ' · 미연결 ' + (n - li) + ')'));
