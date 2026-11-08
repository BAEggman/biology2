#!/usr/bin/env node
// lesson_cover.js — 갈아엎기 진척: 묶음(sNN)마다 행 · 카드가 과(lesson) 정거장의 src 로 얼마나 덮였는지.
// 사용: node tools/lesson_cover.js            (전체 표 · 카드 많은 순)
//       node tools/lesson_cover.js s16        (그 묶음의 안 덮인 행 목록)
//       node tools/lesson_cover.js --json     (lesson/index.html 이 쓰는 JSON)
const { deck, strip, lessons } = require('./lesson_lib');
const arg = process.argv[2];
const covered = {};
for (const L of lessons()) for (const st of L.stops) for (const r of (st.src || [])) (covered[r] = covered[r] || []).push(L.id + '#' + L.stops.indexOf(st));
const rows = [];
for (const sc of deck()) {
  let r = 0, c = 0, rc = 0, cc = 0; const un = [];
  for (const P of sc.panels) { if (P.retired) continue; P.f.forEach((row, i) => {
    const cards = (row[2] || []).length; r++; c += cards;
    if (covered[P.id + '#' + i]) { rc++; cc += cards; } else un.push({ ref: P.id + '#' + i, cards, prop: strip(row[0]).slice(0, 60), fact: strip(row[1]).slice(0, 120) });
  }); }
  const Ls = lessons().filter(L => L.scene === sc.id).map(L => L.id);
  rows.push({ id: sc.id, unit: sc.unit || sc.t, rows: r, cards: c, rowsCovered: rc, cardsCovered: cc, lessons: Ls, uncovered: un, kind: sc.id[0] });
}
rows.sort((a, b) => b.cards - a.cards);
if (arg === '--json') { console.log(JSON.stringify(rows.map(({ uncovered, ...x }) => x))); process.exit(); }
if (arg) {
  const sc = rows.find(x => x.id === arg); if (!sc) { console.error('없는 묶음'); process.exit(1); }
  console.log(`${sc.id} ${sc.unit} — 행 ${sc.rowsCovered}/${sc.rows} · 카드 ${sc.cardsCovered}/${sc.cards} · 과 ${sc.lessons.join(' ') || '없음'}`);
  console.log('안 덮인 행:'); for (const u of sc.uncovered) console.log(`  ${u.ref} (카드 ${u.cards}) ${u.prop} | ${u.fact}`);
  process.exit();
}
const tot = { rows: 0, cards: 0, rc: 0, cc: 0 };
console.log('묶음\t카드\t행\t덮인 행\t덮인 카드\t과');
for (const x of rows) { tot.rows += x.rows; tot.cards += x.cards; tot.rc += x.rowsCovered; tot.cc += x.cardsCovered;
  console.log(`${x.id} ${x.unit.slice(0, 22)}\t${x.cards}\t${x.rows}\t${x.rowsCovered}\t${x.cardsCovered}\t${x.lessons.join(' ')}`); }
console.log(`합계\t${tot.cards}\t${tot.rows}\t${tot.rc}\t${tot.cc}\t과 ${lessons().length}`);
