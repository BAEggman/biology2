#!/usr/bin/env node
/* 패널 단위(pc) 카드 접지 검사.
 *
 * ★ 왜 필요한가 (2026-08-20)
 *   d01p01(감수분열 3열 대조표)에 「유성생식 생활사 3유형」과 「식물의 세대교번 흐름」이
 *   pc로 걸려 있었다. 그 도해에는 생활사도 포자체도 배우체도 한 칸이 없다.
 *   사용자가 잡았다: 「이거랑 연결이 안되는거같은데?」
 *   행 단위 링크는 소품이 증거지만, pc는 증거가 없다 — 그래서 뭉뚱그려 걸리기 쉽다.
 *
 * 방법: 카드의 질문+정답에서 나온 낱말이 그 패널의 글(제목·br·소품·사실) 어디에도
 *      안 나오면 「접지 없음」으로 본다. idf로 흔한 낱말을 죽인다.
 *      ★ 판정은 사람이 한다 — 도구는 후보만 모은다.
 */
const fs = require('fs');
const ROOT = __dirname + '/..';
const sk = fs.readFileSync(ROOT + '/sketchy.html', 'utf8');
const idx = fs.readFileSync(ROOT + '/index.html', 'utf8');

const i = sk.indexOf('[', sk.indexOf('const DATA'));
let d = 0, q = null, e = false, end = 0;
for (let k = i; k < sk.length; k++) {
  const c = sk[k];
  if (q) { if (e) { e = false; continue } if (c === '\\') { e = true; continue } if (c === q) q = null; continue }
  if (c === '"' || c === "'" || c === '`') { q = c; continue }
  if (c === '[') d++; else if (c === ']') { d--; if (!d) { end = k + 1; break } }
}
const DATA = eval('(' + sk.slice(i, end) + ')');
const CARDS = JSON.parse(idx.match(/id=["']CARDS["'][^>]*>([\s\S]*?)<\/script>/)[1]);
const BY = Object.fromEntries(CARDS.map(c => [c.id, c]));

const strip = x => String(x == null ? '' : x).replace(/<[^>]+>/g, '');
/* 낱말: 한글 2자 이상 덩어리 · 로마자 2자 이상 · 숫자+n */
const toks = s => (strip(s).match(/[가-힣]{2,}|[A-Za-z][A-Za-z0-9]{1,}|\d+n/g) || []);

/* 조사·흔한 꼬리를 떼기 위해 2~4글자 부분열도 같이 본다 */
function grams(w) {
  const out = new Set([w]);
  if (/^[가-힣]+$/.test(w)) for (let L = 2; L <= 4 && L < w.length; L++)
    for (let a = 0; a + L <= w.length; a++) out.add(w.slice(a, a + L));
  return [...out];
}

/* 패널별 글 모으기 */
const P = {};
for (const sc of DATA) for (const p of (sc.panels || [])) {
  const txt = [p.t, p.br, p.bx, ...(p.f || []).flatMap(r => [r[0], r[1]])].map(strip).join(' ');
  P[p.id] = {scene: sc.id, gate: sc.gate, title: p.t, text: txt, pc: p.pc || [],
             rowCards: new Set((p.f || []).flatMap(r => r[2] || []))};
}

/* idf — 여러 패널에 나오는 낱말은 증거가 못 된다 */
const df = {};
for (const pid in P) for (const w of new Set(toks(P[pid].text))) df[w] = (df[w] || 0) + 1;
const NP = Object.keys(P).length;

const rows = [];
for (const pid in P) {
  const v = P[pid];
  for (const cid of v.pc) {
    if (v.rowCards.has(cid)) continue;          // 행에도 걸려 있으면 증거가 있다
    const c = BY[cid]; if (!c) continue;
    /* ★ 그 카드에서 가장 드문 낱말 셋을 고른다 — 그것이 이 카드가 묻는 「그것」이다.
       흔한 낱말(감수분열·세포 …)은 어느 패널에나 있어 증거가 못 된다. */
    const words = [...new Set(toks(c.q).concat(toks(c.a)))].filter(w => w.length >= 2);
    const key = words.sort((a, b) => (df[a] || 0) - (df[b] || 0)).slice(0, 3);
    if (key.length < 2) continue;                // 판정 불가
    const has = w => grams(w).some(g => g.length >= 3 && v.text.includes(g)) || v.text.includes(w);
    const hit = key.filter(has);
    rows.push({pid, gate: v.gate, title: v.title, cid,
               score: hit.length / key.length, nw: key.length,
               miss: key.filter(w => !hit.includes(w)),
               q: strip(c.q).slice(0, 58), a: strip(c.a).slice(0, 54)});
  }
}

const arg = process.argv[2];
const bad = rows.filter(r => r.score === 0);
if (arg === '--sum') {
  console.log(`pc 카드(행에 안 걸린 것) ${rows.length}장 검사`);
  console.log(`그중 패널 글과 낱말이 하나도 안 겹치는 것 ${bad.length}장`);
  const byP = {};
  for (const r of bad) (byP[r.pid] = byP[r.pid] || []).push(r);
  const ent = Object.entries(byP).sort((a, b) => b[1].length - a[1].length);
  console.log('\n패널 순위:');
  for (const [pid, list] of ent.slice(0, 30))
    console.log(`  ${pid.padEnd(9)} ${String(list.length).padStart(3)}장  ${P[pid].title}`);
} else if (arg) {
  for (const r of bad.filter(x => x.pid.startsWith(arg)))
    console.log(`${r.pid}  ${r.cid}\n   Q ${r.q}\n   A ${r.a}\n   못 찾은 낱말: ${r.miss.join(' ')}`);
} else {
  const byP = {};
  for (const r of bad) (byP[r.pid] = byP[r.pid] || []).push(r);
  for (const [pid, list] of Object.entries(byP).sort((a, b) => b[1].length - a[1].length)) {
    console.log(`\n${pid}  [${P[pid].gate}]  ${list.length}장 — ${P[pid].title}`);
    for (const r of list) console.log(`   ${r.cid.padEnd(10)} ${r.q} → ${r.a}`);
  }
}
