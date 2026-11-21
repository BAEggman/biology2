/* tts_order.js — 과 번호 → 짧은 제목(제목의 「 — 」 앞) · ttsNorm 의 「L13a 에서 본」을 「「…」 그림에서 본」으로 읽는 데 쓴다 */
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
module.exports = function ttsOrder() {
  const o = {};
  for (const f of fs.readdirSync(path.join(ROOT, 'lessons')).filter(f => /^L\d{2}[a-z]?\.json$/.test(f)).sort()) {
    const L = JSON.parse(fs.readFileSync(path.join(ROOT, 'lessons', f), 'utf8'));
    o[L.id] = String(L.title).split(' — ')[0].replace(/[「」<&]/g, '').trim();
  }
  return o;
};
