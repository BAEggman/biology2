#!/usr/bin/env node
/* ★ 답 쪽 훑기 — audit_phonetics.js 의 눈먼 자리
 *
 * audit_phonetics.js 는 **사실 칸**의 이름만 본다. 그런데 학생이 실제로 인출해야 하는 것은
 * **카드의 답(a)** 이다. 답에 임의 라벨이 있는데 그 카드가 걸린 판의 소품이 그 이름을
 * 안 나르면, 그림을 외운 뒤 이름을 따로 외워야 한다 — 감사가 못 보는 위반이다.
 *
 * ★ 무엇을 위반으로 보지 않는가 (audit_phonetics.js 와 같은 잣대를 쓴다)
 *   ① KNOWN — 학생이 이미 낱말처럼 아는 것
 *   ② hooks.json 「_뜻이있는약어」 — 글자가 곧 뜻인 약어
 *   ③ hooks.json 「hooks」 에 등재된 후크의 소품이 그 판에 있다
 *   ④ ★ **발문(q)이 그 이름을 준다** — 단서로 주어지는 것은 인출 대상이 아니다
 *      (2026-08-26 에 세운 잣대. X-BT-16 「파보바이러스(B19)는 …」의 B19 가 그 예다)
 *
 * ★ 겹걸기를 존중한다 — 카드가 걸린 판 **전부**의 소품을 합쳐 본다.
 */
const fs = require('fs');
const path = require('path');
const R = f => fs.readFileSync(path.join(__dirname, '..', f), 'utf8');

/* ── sketchy.html 의 DATA ── */
const s = R('sketchy.html');
{ }
const i0 = s.indexOf('[', s.indexOf('const DATA'));
let d = 0, q = null, e = false, end = 0;
for (let k = i0; k < s.length; k++) {
  const c = s[k];
  if (q) { if (e) { e = false; continue } if (c === '\\') { e = true; continue } if (c === q) q = null; continue }
  if (c === '"' || c === "'" || c === '`') { q = c; continue }
  if (c === '[') d++; else if (c === ']') { d--; if (!d) { end = k + 1; break } }
}
const DATA = eval('(' + s.slice(i0, end) + ')');
const strip = x => String(x == null ? '' : x).replace(/<[^>]+>/g, '');

/* ── index.html 의 CARDS ── */
const idx = R('index.html');
const cm = idx.match(/id=["']CARDS["'][^>]*>([\s\S]*?)<\/script>/);
const CARDS = {};
for (const c of JSON.parse(cm[1])) if (c && c.id) CARDS[c.id] = c;

/* ── hooks.json ── */
const H = JSON.parse(R('tools/hooks.json'));
const HOOKS = H.hooks || {};
const MEAN = new Set(Object.keys((H['_뜻이있는약어'] || {})['목록'] || {}));
const FREE = new Set(Object.keys((H['_외래어면제'] || {})['목록'] || {}));
const LOANMISS = new Set(Object.keys((H['_음차오탐'] || {})['목록'] || {}));
const NAMEMISS = new Set(H['_인명오탐'] || []);
const ANSFREE = new Set(Object.keys((H['_답면제'] || {})['목록'] || {}));
/* ★ [고침 2026-08-26] audit_phonetics.js 가 읽는 _인명면제 를 여기서도 읽는다.
   두 감사가 같은 잣대를 써야 한다 — 안 그러면 한쪽에서 면제한 이름이 다른 쪽에서 살아난다. */
const EPOFREE = new Set(Object.keys((H['_인명면제'] || {})['목록'] || {}));

/* ── audit_phonetics.js 의 KNOWN·EPONYM 을 그대로 가져다 쓴다 (두 감사가 갈리면 안 된다) ── */
const pj = R('tools/audit_phonetics.js');
const KNOWN = new Set(pj.match(/const KNOWN = new Set\(`([\s\S]*?)`/)[1].split(/\s+/).filter(Boolean));
const EPO = [...new Set(pj.match(/const EPONYM = `([\s\S]*?)`/)[1].split(/\s+/).filter(Boolean))];

/* ── 판별 소품 · 카드→판 ── */
const PROPS = {}, WHERE = {};
for (const sc of DATA) for (const p of (sc.panels || [])) {
  /* ★ [고침 2026-08-26] svg 도해는 **그림 위에 이름을 글자로 찍는다** — 학생이 보고 읽으므로
     소품과 같이 센다. audit_phonetics.js 와 같은 처리다(<text> 안의 보이는 글자만). */
  const svgT = p.svg
    ? [...String(p.svg).matchAll(/<text\b[^>]*>([\s\S]*?)<\/text>/g)].map(m => strip(m[1])).join(' ')
    : '';
  PROPS[p.id] = (p.f || []).map(r => strip(r[0])).join(' | ') + ' | ' + svgT;
  for (const r of (p.f || [])) for (const cid of (r[2] || []))
    (WHERE[cid] = WHERE[cid] || new Set()).add(p.id);
}

const SYL = {A:'에이',B:'비',C:'씨',D:'디',E:'이',F:'에프',G:'지',H:'에이치',I:'아이',J:'제이',
             K:'케이',L:'엘',M:'엠',N:'엔',O:'오',P:'피',Q:'큐',R:'알',S:'에스',T:'티',U:'유',
             V:'브이',W:'더블유',X:'엑스',Y:'와이',Z:'제트'};
function carries(prop, name) {
  const hk = HOOKS[name];
  if (hk && (hk.props || []).some(w => prop.includes(w))) return true;
  if (prop.toLowerCase().includes(name.toLowerCase())) return true;
  const kor = [...name.toUpperCase()].map(ch => SYL[ch] || '').join('');
  if (kor && prop.includes(kor)) return true;
  if (kor.length >= 4) for (let a = 0; a + 2 < kor.length; a++) if (prop.includes(kor.slice(a, a + 3))) return true;
  return false;
}

/* 위첨자가 뜯긴 이온 등 — 도구 결함이지 위반이 아니다 */
const ARTIFACT = new Set('Ca2 Mg2 Fe2 Fe3 Na1 K1 Cl1 Zn2 Cu2 Mn2 NH NO SO PO HCO CO2 O2 N2 SiO CaCO H2O H2S NH4 NO3 NO2'.split(' '));  /* 위첨자·아래첨자가 뜯긴 이온 — 도구 결함이지 위반이 아니다 */
const ROMAN = /\b[A-Za-z][A-Za-z0-9]*\b/g;

const rows = [];
for (const cid of Object.keys(WHERE)) {
  const c = CARDS[cid]; if (!c) continue;
  const qq = strip(c.q), ans = strip(c.a);
  const pids = [...WHERE[cid]].sort();
  const prop = pids.map(p => PROPS[p] || '').join(' | ');
  const names = new Set();
  for (const m of (ans.match(ROMAN) || [])) {
    if (m.length < 2 || !/[A-Z]/.test(m)) continue;
    if (KNOWN.has(m) || MEAN.has(m) || ARTIFACT.has(m) || ANSFREE.has(m)) continue;
    if (/^[IVX]+$/.test(m)) continue;
    names.add(m);
  }
  for (const ep of EPO) {
    if (ep.length < 3 || !ans.includes(ep)) continue;
    if (FREE.has(ep) || LOANMISS.has(ep) || NAMEMISS.has(ep) || ANSFREE.has(ep) || EPOFREE.has(ep)) continue;
    names.add(ep);
  }
  const miss = [...names].filter(n => !qq.includes(n)).filter(n => !carries(prop, n)).sort();
  if (miss.length) rows.push({ cid, pids, miss, q: qq, a: ans });
}

/* ── 출력 ── */
const byPanel = {};
for (const r of rows) for (const p of r.pids) (byPanel[p] = byPanel[p] || []).push(r);
const names = {};
for (const r of rows) for (const n of r.miss) names[n] = (names[n] || 0) + 1;

if (process.argv.includes('--json')) {
  console.log(JSON.stringify({ cards: rows.length, names: Object.keys(names).length,
    panels: Object.keys(byPanel).length, rows }, null, 1));
} else {
  console.log(`★ 답에만 있고 소품이 안 나르는 이름 — 카드 ${rows.length}장 · 이름 ${Object.keys(names).length}종 · 판 ${Object.keys(byPanel).length}개\n`);
  const ps = Object.entries(byPanel).sort((a, b) => b[1].length - a[1].length);
  for (const [p, rs] of ps) {
    const ns = [...new Set(rs.flatMap(r => r.miss))].sort();
    console.log(`  ${String(rs.length).padStart(3)}장  ${p.padEnd(9)} ${ns.join(' · ')}`);
  }
  console.log('\n== 이름별 ==');
  for (const [n, k] of Object.entries(names).sort((a, b) => b[1] - a[1]))
    console.log(`  ${String(k).padStart(3)}  ${n}`);
}
