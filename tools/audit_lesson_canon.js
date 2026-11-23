#!/usr/bin/env node
/* audit_lesson_canon.js — 문 2 · 기호 일관(2026-11-23 · 11-19 지시서 §4.2). 규칙은 tools/cue/canon.json.
 *   「fact 또는 카드 답에 X」 규칙: 그 과의 fact 나 걸린 카드의 답에 X 가 나오면, 그 과의 obj 어딘가에 「있어야」 가운데 하나가 있다(예외 과 빼고).
 *   「<물건> 소품」 규칙: obj 에 그 물건이 나오는 과는 「예외」에 뜻과 함께 적혀 있어야 한다(같은 물건 · 다른 뜻을 막음).
 *   덤(보고만 · --report): _심볼예약 의 물건 말이 여러 과의 obj 에 나올 때 그 정거장 fact 머리말이 서로 다른 것.
 * 사용: node tools/audit_lesson_canon.js [--json | --report]   · 모듈: require(...).check() → [{규칙, 과, 까닭}] */
const fs = require('fs'), path = require('path');
const { ROOT, lessons, stopCards, panelIndex, strip } = require('./lesson_lib');
const C = JSON.parse(fs.readFileSync(path.join(ROOT, 'tools/cue/canon.json'), 'utf8'));
let CARDS = null;
function cards() { if (CARDS) return CARDS; CARDS = {}; for (const c of JSON.parse(fs.readFileSync(path.join(ROOT, 'index.html'), 'utf8').match(/id=["']CARDS["'][^>]*>([\s\S]*?)<\/script>/)[1])) CARDS[c.id] = c; return CARDS; }
function lessonText(L, idx) {
  const obj = L.stops.map(s => strip(s.obj)).join(' ¦ '), fact = L.stops.map(s => strip(s.fact)).join(' ¦ ');
  const ans = [];
  for (const s of L.stops) for (const id of stopCards(s, idx)) { const c = cards()[id.replace(/#\d+$/, '')]; if (c) ans.push(strip((c.a || '') + ' ' + (Array.isArray(c.it) ? c.it.join(' ') : ''))); }
  return { obj, fact, ans: ans.join(' ¦ ') };
}
function check(rules) {
  rules = rules || C['규칙']; const idx = panelIndex(), out = [];
  const LS = lessons().map(L => ({ id: L.id, ...lessonText(L, idx) }));
  for (const r of rules) {
    const ex = r['예외'] || {};
    let m = /^fact 또는 카드 답에 (.+)$/.exec(r['때'] || '');
    if (m) { const X = m[1];
      const re = new RegExp('(^|[^가-힣])' + X.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));
      for (const L of LS) { if (ex[L.id]) continue; if (!(re.test(L.fact) || re.test(L.ans))) continue;
        if (!(r['있어야'] || []).some(p => L.obj.includes(p))) out.push({ 규칙: r['개념'], 과: L.id, 까닭: `${X} 가 나오는데 obj 에 ${(r['있어야'] || []).join(' / ')} 없음` }); }
      continue; }
    m = /^(.+) 소품$/.exec(r['때'] || '');
    if (m) { const P = m[1]; for (const L of LS) if (L.obj.includes(P) && !ex[L.id]) out.push({ 규칙: r['개념'], 과: L.id, 까닭: `${P} 가 obj 에 있는데 예외(뜻)에 없음` }); continue; }
    out.push({ 규칙: r['개념'], 과: '-', 까닭: '읽을 수 없는 「때」: ' + r['때'] });
  }
  return out;
}
function report() {
  const H = JSON.parse(fs.readFileSync(path.join(ROOT, 'tools/hooks.json'), 'utf8')), RES = Object.keys(H['_심볼예약'] || {}).filter(k => !k.startsWith('_') && k.length >= 2 && k.length <= 8);
  const seen = {};
  for (const L of lessons()) for (const s of L.stops) { const o = strip(s.obj), head = (strip(s.fact).split(' — ')[0] || '').slice(0, 24);
    for (const k of RES) if (o.includes(k)) (seen[k] = seen[k] || []).push(`${L.id} ${s.sid}: ${head}`); }
  return Object.entries(seen).filter(([k, v]) => new Set(v.map(x => x.split(': ')[1])).size > 1 && new Set(v.map(x => x.split(' ')[0])).size > 1);
}
module.exports = { check, report };
if (require.main === module) {
  const a = process.argv[2];
  if (a === '--report') { for (const [k, v] of report()) console.log(k + '\n   ' + v.join('\n   ')); }
  else { const r = check(); if (a === '--json') console.log(JSON.stringify(r)); else { for (const x of r) console.log(x.규칙, x.과, x.까닭); console.log('어긋남', r.length); } }
}
