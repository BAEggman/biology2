// lesson_lib.js — 과(lesson) 도구들이 같이 쓰는 것: 덱 DATA 읽기 · 행 참조(sNNpNN#k) 풀기 · 과 파일 목록
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
let _DATA = null;
function deck() {
  if (_DATA) return _DATA;
  const s = fs.readFileSync(path.join(ROOT, 'sketchy.html'), 'utf8');
  const m = s.match(/const DATA\s*=\s*(\[[\s\S]*?\n\]);/);
  if (!m) throw new Error('sketchy.html 에서 DATA 를 못 찾음');
  _DATA = eval(m[1]);  // 덱 자체 파일 — 신뢰
  return _DATA;
}
const strip = h => String(h || '').replace(/<[^>]+>/g, '').replace(/\s+/g, ' ').trim();
function panelIndex() {
  const idx = {};
  for (const sc of deck()) for (const P of sc.panels) idx[P.id] = { scene: sc, panel: P };
  return idx;
}
// 'sNNpNN#k' → {pid, k, row:[prop,fact,cards]}
function resolveRef(ref, idx) {
  const m = /^([a-z]\d{2}[pu]\d{2}[a-z]?)#(\d+)$/.exec(ref);
  if (!m) throw new Error('행 참조 꼴이 아님: ' + ref);
  const e = (idx || panelIndex())[m[1]];
  if (!e) throw new Error('없는 판: ' + ref);
  const row = e.panel.f[+m[2]];
  if (!row) throw new Error('없는 행: ' + ref);
  return { pid: m[1], k: +m[2], row, panel: e.panel, scene: e.scene };
}
function lessons() {
  const dir = path.join(ROOT, 'lessons');
  return fs.readdirSync(dir).filter(f => /^L\d{2}[a-z]?\.json$/.test(f)).sort()
    .map(f => JSON.parse(fs.readFileSync(path.join(dir, f), 'utf8')));
}
// 정거장의 카드 = 옛 판 행(src)에 딸린 카드 + 곧장 건 카드(cards) − 이 정거장 것이 아닌 카드(drop)
function stopCards(s, idx) {
  const out = []; idx = idx || panelIndex();
  for (const r of (s.src || [])) { try { out.push(...(resolveRef(r, idx).row[2] || [])); } catch (e) {} }
  out.push(...(Array.isArray(s.cards) ? s.cards : []));
  const drop = new Set(Array.isArray(s.drop) ? s.drop : []);
  return [...new Set(out)].filter(c => !drop.has(c));
}
module.exports = { ROOT, deck, strip, panelIndex, resolveRef, lessons, stopCards };
