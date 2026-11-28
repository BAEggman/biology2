// cuehash.js — 6+1 문(test/verify_standing.js ③)이 쓰는 정거장 해시. hook · obj 를 따로 sha1 앞 12자로.
const fs = require('fs'), path = require('path'), crypto = require('crypto');
const ROOT = path.join(__dirname, '..', '..', '..');
const h = s => crypto.createHash('sha1').update(String(s || '').normalize('NFC')).digest('hex').slice(0, 12);
function current(root) {
  const dir = path.join(root || ROOT, 'lessons'), out = {};
  for (const f of fs.readdirSync(dir).filter(f => /^L\d{2}[a-z]?\.json$/.test(f)).sort()) {
    const L = JSON.parse(fs.readFileSync(path.join(dir, f), 'utf8'));
    for (const s of L.stops) out[L.id + '|' + s.sid] = { hook: h(s.hook), obj: h(s.obj) };
  }
  return out;
}
// 바뀐 정거장 중 기록(index.json 의 일감 · 다듬음)이 지금 해시를 덮지 않는 것
function unrecorded(base, cur, index, jobExists) {
  const ok = {}; const bad = [];
  for (const [id, j] of Object.entries((index && index['일감']) || {})) {
    if (!jobExists(id)) continue;
    for (const [k, v] of Object.entries(j['닿은'] || {})) (ok[k] = ok[k] || []).push(v);
  }
  for (const d of (index && index['다듬음']) || []) for (const [k, v] of Object.entries(d['닿은'] || {})) (ok[k] = ok[k] || []).push(v);
  for (const [k, v] of Object.entries(cur)) {
    const b = base[k];
    if (b && b.hook === v.hook && b.obj === v.obj) continue;
    if ((ok[k] || []).some(r => r.hook === v.hook && r.obj === v.obj)) continue;
    bad.push(k);
  }
  return bad;
}
// 6+1 을 실제로 돌린 일감 폴더인가: 꾸러미 · 제안(보통 일감 셋 가 · 다 · 라 — 2026-11-23 사용자 결정 · 기호 일감은 여섯이 더 있음) · 심판(rN_judge)
function jobDone(dir) {
  if (!fs.existsSync(path.join(dir, 'packet.md'))) return false;
  const fs_ = fs.readdirSync(dir);
  return [...new Set(fs_.map(f => (f.match(/^r(\d+)_judge\.md$/) || [])[1]).filter(Boolean))]
    .some(n => '가다라'.split('').every(c => fs_.includes(`r${n}_${c}.md`)));
}
// 사용자가 직접 정한 고리의 일감(고르기 화면 — README §0 · 2026-11-23 「사용자가 직접 정한 고리는 제안 단계 없이 심판이 두 가지만 확인」 · 2026-11-26 두 판 면제 · 고르기 화면).
// 제안 파일이 없다. 대신 picks.json 에 「고름」이 있고, 그 과의 심판 확인 기록 확인_<과>.md(카드 사실 · 예약 기호)가 있어야 한다.
function pickLessons(dir) {
  const p = path.join(dir, 'picks.json');
  if (!fs.existsSync(p)) return [];
  let picks; try { picks = JSON.parse(fs.readFileSync(p, 'utf8')); } catch (e) { return []; }
  if (!Object.values(picks).some(v => v && v['결정'] === '고름')) return [];
  return fs.readdirSync(dir).map(f => (f.normalize('NFC').match(/^확인_(L\d{2}[a-z]?)\.md$/) || [])[1]).filter(Boolean)
    .filter(l => fs.readFileSync(path.join(dir, fs.readdirSync(dir).find(f => f.normalize('NFC') === `확인_${l}.md`)), 'utf8').trim().length > 80);
}
const pickDone = dir => pickLessons(dir).length > 0;
const jobOk = dir => jobDone(dir) || pickDone(dir);
// 그 일감이 이 정거장(과|sid)을 바꿀 자격이 있는가 — 6+1 일감이면 언제나, 사용자 고름 일감이면 그 과의 확인 기록이 있을 때만
const jobCovers = (dir, key) => jobDone(dir) || pickLessons(dir).includes(String(key).split('|')[0]);
module.exports = { h, current, unrecorded, jobDone, pickDone, pickLessons, jobOk, jobCovers, ROOT };
