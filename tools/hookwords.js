#!/usr/bin/env node
/* ★ 후크말 대조 (2026-09-02 신설 · _후크대기 43)
 *
 * 왜 필요한가 — **같은 사고가 세 번 났다.**
 *   2026-08-26  GPCR·LGIC : 「물건은 그려져 있는데 사전의 말과 안 맞아 감사가 못 알아봤다」
 *   2026-09-02  GPCR       : 사전 「토큰을 뒤집으며」 vs 판 「토큰을 **도로** 뒤집어」
 *   2026-09-02  시냅시스    : 사전 「맞붙음」        vs 판 「맞붙**는다**」
 * 그림을 다시 그릴 일이 아니었다 — **말을 맞추면 되는 일**이었다.
 *
 * 쓰는 법
 *   node tools/hookwords.js -n 이름 이름 …   판을 세우기 **전에**: 그 이름들의 후크 props 를 뽑는다
 *   node tools/hookwords.js <판 id>          그 판이 쓰는 이름 × props 대조 (빠진 것 · 근접어)
 *   node tools/hookwords.js --near           덱 전체 근접어 훑기 — 「글자만 다른」 자리를 다 뽑는다
 *
 * ★ 규칙 — 새 판의 소품 칸은 **사전의 말을 그대로** 쓴다. 달라져야 하면 props 에 더한다.
 *
 * 표
 *   ✓  사전의 말이 소품 칸에 그대로 있다
 *   ★  **말이 어긋났다** — 그림은 있는데 말이 다르다. 이 도구가 잡으려고 만든 것
 *   ◇  이 판의 일이 아니다 — 남의 판을 가리키거나(판 번호 · 앞 판) 가르는 말(갈린다 · 같은 계열)
 *   ✗  덱 어디에도 그 물건이 없다
 */
const fs = require('fs'), path = require('path');
const R = f => fs.readFileSync(path.join(__dirname, '..', f), 'utf8');
const strip = x => String(x == null ? '' : x).replace(/<[^>]+>/g, '');

/* ── DATA ── */
const s = R('sketchy.html');
const i0 = s.indexOf('[', s.indexOf('const DATA'));
let d = 0, q = null, e = false, end = 0;
for (let k = i0; k < s.length; k++) {
  const c = s[k];
  if (q) { if (e) { e = false; continue } if (c === '\\') { e = true; continue } if (c === q) q = null; continue }
  if (c === '"' || c === "'" || c === '`') { q = c; continue }
  if (c === '[') d++; else if (c === ']') { d--; if (!d) { end = k + 1; break } }
}
const DATA = eval('(' + s.slice(i0, end) + ')');

const H = JSON.parse(R('tools/hooks.json'));
const HOOKS = H.hooks || {};
const L = k => new Set(Object.keys((H[k] || {})['목록'] || {}));
const FREE = { '뜻이있는약어': L('_뜻이있는약어'), '음차면제': L('_외래어면제'), '음차오탐': L('_음차오탐'),
               '답면제': L('_답면제'), '인명면제': L('_인명면제') };

/* ── 판 ── */
const PANEL = {};
for (const sc of DATA) for (const p of (sc.panels || [])) {
  const svgT = p.svg ? [...String(p.svg).matchAll(/<text\b[^>]*>([\s\S]*?)<\/text>/g)].map(m => strip(m[1])).join(' ') : '';
  PANEL[p.id] = {
    t: p.t || '',
    props: (p.f || []).map(r => strip(r[0])).join(' | ') + ' | ' + svgT,
    facts: (p.f || []).map(r => strip(r[1])).join(' | ') + ' ' + strip(p.br || '') ,
  };
}

/* ── 근접도 ────────────────────────────────────────────────────
 * 「글자만 다른」 자리를 잡는 자다. 두 가지를 지킨다.
 *   ① 공백을 떼고 잰다 — 「토큰을 뒤집으며」 ↔ 「토큰을 도로 뒤집어」 는 공백 때문에 짧게 잡힌다
 *   ② 길이가 아니라 **비율**로 자른다 — 「맞붙음」 ↔ 「맞붙는다」 의 겹친 말은 두 글자뿐이지만 뜻의 3분의 2다
 * 그냥 길이 3으로 자르면 「으로 」 같은 토씨가 걸리고 「맞붙」 은 놓친다.
 */
const NS = x => String(x).replace(/[\s|·「」]/g, '');
function nearness(prop, hay) {
  const a = NS(prop), b = NS(hay);
  const m = lcs(a, b);
  if (m.length < 2) return null;
  const r = m.length / a.length;
  // 두 글자짜리 겹침은 토씨일 때가 많다 — 「맞붙」(3분의 2)은 살리고 「물이」(절반)는 버린다
  if (m.length === 2 ? r < 0.6 : r < 0.4) return null;
  return { m, r };
}

/* 가장 긴 공통 부분문자열 */
function lcs(a, b) {
  let best = '';
  for (let i = 0; i < a.length; i++) {
    for (let j = i + best.length + 1; j <= a.length; j++) {
      const t = a.slice(i, j);
      if (b.includes(t)) { if (t.length > best.length) best = t; } else break;
    }
  }
  return best;
}

/* ── 이름이 「진짜로」 그 판에 나오는가 ─────────────────────────────
 * 왜 필요한가 — 그냥 부분문자열로 세면 거짓이 는다.
 *   K  가 MAPK 안에서 · AT 가 ATP 안에서 · AP 가 APC/C 안에서 · H3 가 CH3 안에서
 * 두 가지로 거른다.
 *   ① 로마자 이름은 앞뒤가 영숫자면 다른 낱말의 일부다
 *   ② 더 긴 후크 이름 안에 들어 있는 자리는 그 긴 후크의 자리다
 */
const HNAMES = Object.keys(HOOKS);
const OCC = (hay, n) => { const o = []; let i = hay.indexOf(n); while (i >= 0) { o.push(i); i = hay.indexOf(n, i + 1) } return o };
const ROMAN = n => /^[A-Za-z0-9/+\-()·'.]+$/.test(n);
const LONGER = {};
for (const n of HNAMES) LONGER[n] = HNAMES.filter(m => m !== n && m.includes(n));
/* 이 판이 그 이름을 **제 일로** 말하는가, 아니면 **딴 데를 가리키며** 말하는가.
 * 덱은 이미 표를 쓰고 있다 —
 *   ⚠ 「…(s20p01b 브라시노스테로이드)과 갈린다」  ← 가르는 말 (판 번호가 곁에 있다)
 *   ★ 「트로포닌·트로포미오신과 같은 계열이라」    ← 계열을 짚는 말
 * 이런 자리는 그 물건이 이 판에 없어도 잘못이 아니다. 오히려 있어서는 안 된다.
 */
const REFMARK = /(s\d+p\d+[a-z]*|d\d+p\d+[a-z]*|갈린다|갈라|갈랐|와 다르|과 다르|와 달리|과 달리|아니다|아닌|같은 계열|계열이라|예약|앞 판|뒤 판|다른 판|곁판)/;
function present(facts, name) {
  const longer = LONGER[name] || [];
  let own = false, ref = false;
  for (const i of OCC(facts, name)) {
    if (ROMAN(name)) {
      const a = facts[i - 1] || '', b = facts[i + name.length] || '';
      if (/[A-Za-z0-9]/.test(a) || /[A-Za-z0-9]/.test(b)) continue;
    }
    let inside = false;
    for (const m of longer) { for (const j of OCC(facts, m)) if (j <= i && i + name.length <= j + m.length) { inside = true; break } if (inside) break }
    if (inside) continue;
    const win = facts.slice(Math.max(0, i - 30), i + name.length + 30);
    if (REFMARK.test(win)) ref = true; else own = true;
  }
  return own ? 'own' : (ref ? 'ref' : null);
}

function showName(name) {
  const h = HOOKS[name];
  if (h) {
    console.log('  ● ' + name + '  [' + h['형태'] + ']');
    console.log('     props : ' + h.props.map(p => '「' + p + '」').join(' · '));
    console.log('     왜    : ' + strip(String(h['왜'])).slice(0, 150));
    return 'hook';
  }
  for (const [k, set] of Object.entries(FREE)) if (set.has(name)) { console.log('  ○ ' + name + '  — ' + k + ' (후크 없음)'); return k; }
  console.log('  · ' + name + '  — 사전에 없다 (후크도 면제도 아니다)');
  return null;
}

function checkPanel(pid, quiet) {
  const P = PANEL[pid];
  if (!P) { console.log('그런 판이 없다: ' + pid); return 0; }
  const out = [];
  let bad = 0, near0 = 0;
  for (const [name, h] of Object.entries(HOOKS)) {
    const kind = present(P.facts, name);
    if (!kind) continue;
    const hit = h.props.find(p => P.props.includes(p));
    if (kind === 'ref' && !hit) { if (!quiet) out.push('  ◇ ' + name.padEnd(14) + ' 가리키거나 가르는 말 — 이 판의 일이 아니다'); continue; }
    if (hit) { if (!quiet) out.push('  ✓ ' + name.padEnd(14) + ' 「' + hit + '」'); continue; }
    // ① 먼저 **근접**을 본다 — 「그 물건이 다른 판에도 있다」가 어긋난 말을 덮으면 안 된다
    const near = h.props.map(p => { const n = nearness(p, P.props); return n && { p, ...n } })
                        .filter(Boolean).sort((a, b) => b.r - a.r || b.m.length - a.m.length)[0];
    if (near) {
      bad++; near0++;
      const i = NS(P.props).indexOf(near.m), ns = NS(P.props);
      out.push('  ★ ' + name.padEnd(14) + '말이 어긋났다 — 그림은 있는데 말이 다르다');
      out.push('       사전: 「' + near.p + '」   (props: ' + h.props.map(x => '「' + x + '」').join(' · ') + ')');
      out.push('       판  : 「…' + ns.slice(Math.max(0, i - 14), i + near.m.length + 14) + '…」  겹친 말 「' + near.m + '」 = 사전말의 ' + Math.round(near.r * 100) + '%');
      out.push('       → 판의 말을 사전에 맞추거나, props 에 그 말을 더한다');
      continue;
    }
    // ② 그 말이 **다른 판**에 그대로 있으면 잘못이 아니다 — 이 판은 그 판을 가리키고 있는 것이다
    const where = Object.keys(PANEL).filter(q => q !== pid && h.props.some(p => PANEL[q].props.includes(p)));
    if (where.length) { if (!quiet) out.push('  ◇ ' + name.padEnd(14) + ' 이 판에는 없다 — 그 물건은 ' + where.join(' · ') + ' 에 있다 (가리키는 말)'); continue; }
    // ③ 어디에도 없다
    bad++;
    out.push('  ✗ ' + name.padEnd(14) + 'props 중 아무것도 소품 칸에 없다 — 덱 어디에도 없다');
    out.push('       사전: ' + h.props.map(x => '「' + x + '」').join(' · '));
  }
  if (!quiet || bad) {
    console.log('\n■ ' + pid + '  「' + P.t + '」');
    for (const l of out) console.log(l);
  }
  NEAR += near0;
  return bad;
}
let NEAR = 0;

const args = process.argv.slice(2);
if (args[0] === '-n' || args[0] === '--names') {
  console.log('\n── 후크말 미리 보기 — 소품 칸에 이 말을 그대로 쓴다 ──');
  for (const n of args.slice(1)) showName(n);
  console.log('');
} else if (args[0] === '--near') {
  console.log('\n── 덱 전체 근접어 훑기 ── (★ = 그림은 있는데 말이 다르다 · ✗ = 아예 없다)');
  let n = 0, bad = 0;
  for (const pid of Object.keys(PANEL)) { const b = checkPanel(pid, true); if (b) { n++; bad += b } }
  console.log('\n판 ' + Object.keys(PANEL).length + '개 중 말이 어긋난 판 ' + n + '개 · 어긋난 후크 ' + bad + '건 (그중 ★ 근접 ' + NEAR + '건)');
} else if (args.length) {
  const bad = args.map(a => checkPanel(a, false)).reduce((a, b) => a + b, 0);  // ⚠ map(checkPanel) 로 쓰면 index 가 quiet 로 들어간다
  console.log('\n어긋난 후크 ' + bad + '건');
} else {
  console.log(fs.readFileSync(__filename, 'utf8').split('*/')[0]);
}
