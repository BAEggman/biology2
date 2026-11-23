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
// 6+1 을 실제로 돌린 일감 폴더인가: 꾸러미 · 제안 여섯(rN_가 ~ 바) · 심판(rN_judge)
function jobDone(dir) {
  if (!fs.existsSync(path.join(dir, 'packet.md'))) return false;
  const fs_ = fs.readdirSync(dir);
  return [...new Set(fs_.map(f => (f.match(/^r(\d+)_judge\.md$/) || [])[1]).filter(Boolean))]
    .some(n => '가나다라마바'.split('').every(c => fs_.includes(`r${n}_${c}.md`)));
}
module.exports = { h, current, unrecorded, jobDone, ROOT };
