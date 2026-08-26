#!/usr/bin/env node
/* ★ 카드 ↔ 그림 링크 전수조사 (2026-08-26 신설)
 *
 * SRS 가 카드를 틀렸을 때 그림을 띄우는 길은 이렇다:
 *   사실표 r[2] 의 카드 ID  →  build.js 가 PMAP/PROW/PFACT/PSVG 를 만든다
 *   →  index.html 의 showPicFix 가 img/<pid>.webp (없으면 PSVG) 를 띄우고
 *      PFACT 를 표로 그리며 PROW 가 가리키는 행을 강조한다
 *
 * 이 길의 **모든 이음매**를 검사한다. 하나라도 어긋나면 학생은 빈 화면을 본다.
 */
const fs = require('fs'), path = require('path');
const R = f => fs.readFileSync(path.join(__dirname, '..', f), 'utf8');
const ROOT = path.join(__dirname, '..');

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

const idx = R('index.html');
const CARDS = {};
for (const c of JSON.parse(idx.match(/id=["']CARDS["'][^>]*>([\s\S]*?)<\/script>/)[1])) if (c && c.id) CARDS[c.id] = c;
const g = re => { const m = idx.match(re); return m ? JSON.parse(m[1]) : null; };
const PMAP = g(/var PMAP=(\{[\s\S]*?\});var PROW=/);
const PROW = g(/var PROW=(\{[\s\S]*?\});var PTIT=/);
const PTIT = g(/var PTIT=(\{[\s\S]*?\});var PBR=/);
const PFACT= g(/var PFACT=(\{[\s\S]*?\});var PNOIMG=/);
const PNOIMG=g(/var PNOIMG=(\[[\s\S]*?\]);var PSVG=/);
const PSVG = g(/var PSVG=(\{[\s\S]*?\});\/\*BUILD:END/);

const P = {}, ROWS = {};
for (const sc of DATA) for (const p of (sc.panels || [])) { P[p.id] = p; ROWS[p.id] = (p.f || []).length; }
const pidList = v => v == null ? [] : (Array.isArray(v) ? v : [v]);

const err = [], warn = [], note = [];
const NOIMG = new Set(PNOIMG || []);

/* ① 사실표가 가리키는 카드가 실재하는가 */
let nRef = 0;
for (const pid in P) for (const r of (P[pid].f || [])) for (const cid of (r[2] || [])) {
  nRef++; if (!CARDS[String(cid)]) err.push(`헛참조 ${pid} → ${cid} (CARDS 에 없다)`); }
for (const pid in P) for (const cid of (P[pid].pc || [])) {
  nRef++; if (!CARDS[String(cid)]) err.push(`헛참조(pc) ${pid} → ${cid}`); }

/* ② PMAP 이 가리키는 판이 실재하는가 */
for (const cid in PMAP) for (const pid of pidList(PMAP[cid]))
  if (!P[pid]) err.push(`PMAP ${cid} → 없는 판 ${pid}`);

/* ③ PROW 의 행 번호가 실재하는 행인가 */
for (const cid in PROW) for (const pid in PROW[cid]) {
  if (!P[pid]) { err.push(`PROW ${cid} → 없는 판 ${pid}`); continue; }
  for (const n of PROW[cid][pid]) if (!(n >= 0 && n < ROWS[pid]))
    err.push(`PROW ${cid} @${pid} 행 ${n} — 이 판은 ${ROWS[pid]}행뿐이다`); }

/* ④ 걸린 판마다 띄울 그림이 있는가 (webp 또는 PSVG) */
const shown = new Set(Object.values(PMAP).flatMap(pidList));
for (const pid of shown) {
  const hasImg = fs.existsSync(path.join(ROOT, 'img', pid + '.webp'));
  const hasSvg = PSVG && PSVG[pid];
  if (!hasImg && !hasSvg) err.push(`띄울 그림 없음: ${pid} (webp 도 PSVG 도 없다)`);
  else if (!hasImg && hasSvg && !NOIMG.has(pid)) warn.push(`${pid} — webp 가 없는데 PNOIMG 에 없다`); }

/* ⑤ PFACT·PTIT 가 걸린 판마다 있는가 (없으면 표가 빈다) */
for (const pid of shown) {
  if (!PTIT[pid]) warn.push(`제목 없음: ${pid}`);
  if (!PFACT[pid] || !PFACT[pid].length) warn.push(`사실표 없음: ${pid} — 그림만 뜨고 표가 안 뜬다`); }

/* ⑥ PFACT 가 소스의 행 수와 같은가 (build 결과가 소스와 어긋나면 강조가 밀린다) */
for (const pid of shown) if (PFACT[pid] && PFACT[pid].length !== ROWS[pid])
  err.push(`행 수 불일치 ${pid}: PFACT ${PFACT[pid].length} ≠ 사실표 ${ROWS[pid]}`);

/* ⑦ PROW 가 가리키는 행이 정말 그 카드를 담고 있는가 (강조가 엉뚱한 행을 짚지 않는가) */
let nHit = 0, badHit = 0;
for (const cid in PROW) for (const pid in PROW[cid]) { if (!P[pid]) continue;
  for (const n of PROW[cid][pid]) { const r = (P[pid].f || [])[n]; if (!r) continue; nHit++;
    if (!(r[2] || []).some(x => String(x) === cid || String(x).split('#')[0] === cid)) {
      badHit++; if (badHit <= 5) err.push(`강조 어긋남 ${cid} @${pid}#${n}`); } } }

/* ⑧ 카드가 하나도 안 걸린 판 (고아) */
const orphan = Object.keys(P).filter(pid => !shown.has(pid));

/* ⑨ 같은 카드가 한 판에 pc 와 행으로 겹쳐 걸렸는가 */
for (const pid in P) for (const cid of (P[pid].pc || []))
  if ((P[pid].f || []).some(r => (r[2] || []).some(x => String(x).split('#')[0] === String(cid).split('#')[0])))
    warn.push(`pc 와 행에 겹쳐 걸림: ${pid} ${cid}`);

/* ⑩ 그림 파일이 있는데 아무 판도 안 쓰는 것 */
const used = new Set(Object.keys(P));
const strays = fs.readdirSync(path.join(ROOT, 'img')).filter(f => f.endsWith('.webp'))
  .map(f => f.replace(/\.webp$/, '')).filter(pid => !used.has(pid));

const sum = { 사실표참조: nRef, 연결카드: Object.keys(PMAP).length, 전체카드: Object.keys(CARDS).length,
  판: Object.keys(P).length, 카드걸린판: shown.size, 고아: orphan.length,
  강조검사: nHit, 오류: err.length, 경고: warn.length, 안쓰는그림: strays.length };

if (process.argv.includes('--sum')) { console.log(JSON.stringify(sum)); process.exit(err.length ? 1 : 0); }

console.log('\n★ 카드 ↔ 그림 링크 전수조사\n');
for (const [k, v] of Object.entries(sum)) console.log('  ' + k.padEnd(12) + ' ' + v);
if (orphan.length) console.log('\n── 고아 판 (카드가 하나도 안 걸림) ──\n  ' + orphan.join(' '));
if (strays.length) console.log('\n── 아무 판도 안 쓰는 그림 ──\n  ' + strays.join(' '));
if (warn.length) { console.log('\n── 경고 ──'); warn.slice(0, 30).forEach(w => console.log('  ⚠ ' + w)); }
if (err.length) { console.log('\n── 오류 ──'); err.slice(0, 40).forEach(x => console.log('  ✗ ' + x)); }
else console.log('\n  ✅ 이음매 오류 0건 — 걸린 카드는 전부 그림과 사실표와 강조 행까지 닿는다');
console.log('');
process.exit(err.length ? 1 : 0);
