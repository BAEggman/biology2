// stopcards.js — 과마다 정거장의 카드 id(lesson_lib.stopCards) → JSON {L:{sid:[id]}} (mkledger.py 가 부른다)
const { lessons, stopCards, panelIndex } = require('../../lesson_lib');
const idx = panelIndex(), out = {};
for (const L of lessons()) { out[L.id] = {}; for (const s of L.stops) out[L.id][s.sid] = stopCards(s, idx); }
console.log(JSON.stringify(out));
