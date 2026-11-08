#!/usr/bin/env node
// lesson_rows.js — 한 묶음(sNN)의 판 · 행 · 카드 수 · 후크를 설계용으로 뽑는다 → lessons/draft/<sNN>_rows.md
// 사용: node tools/lesson_rows.js s16 [--full]   (--full: 사실 칸을 자르지 않음)
const fs = require('fs'), path = require('path');
const { ROOT, deck, strip, lessons } = require('./lesson_lib');
const id = process.argv[2]; const full = process.argv.includes('--full');
if (!id) { console.error('사용: node tools/lesson_rows.js s16'); process.exit(1); }
const sc = deck().find(x => x.id === id);
if (!sc) { console.error('없는 묶음: ' + id); process.exit(1); }
let hooks = {}; try { hooks = JSON.parse(fs.readFileSync(path.join(ROOT, 'tools/hooks.json'), 'utf8')); } catch (e) {}
// 이미 과가 덮은 행
const covered = {};
for (const L of lessons()) for (const st of L.stops) for (const r of (st.src || [])) covered[r] = L.id;
const cut = (s, n) => full ? s : (s.length > n ? s.slice(0, n) + '…' : s);
let out = `# ${sc.id} ${sc.t} — ${sc.unit || ''}\n\n`;
let nrow = 0, ncard = 0;
for (const P of sc.panels) {
  if (P.retired) { out += `\n## ${P.id} ${P.t} (retired — 통합판에 흡수)\n`; continue; }
  out += `\n## ${P.id} ${P.t}${P.wide ? ' (통합판)' : ''}\n> ${cut(strip(P.br), 400)}\n\n| # | 소품(그림) | 사실 | 카드 | 과 |\n|---|---|---|---|---|\n`;
  P.f.forEach((r, i) => {
    const cards = (r[2] || []).length; nrow++; ncard += cards;
    out += `| ${i} | ${cut(strip(r[0]), 90)} | ${cut(strip(r[1]), 220)} | ${cards} | ${covered[P.id + '#' + i] || ''} |\n`;
  });
}
// 후크 사전에서 이 묶음 용어
const terms = Object.entries(hooks).filter(([k, v]) => typeof v === 'object' && v && JSON.stringify(v).includes(sc.id));
if (terms.length) {
  out += `\n## hooks.json 에서 ${sc.id} 를 가리키는 항목 (${terms.length})\n`;
  for (const [k, v] of terms.slice(0, 80)) out += `- ${k}: ${cut(strip(JSON.stringify(v)), 160)}\n`;
}
out += `\n합계: 행 ${nrow} · 카드 ${ncard} · 과 후보 수 ≈ ${Math.max(1, Math.round(nrow / 12))}\n`;
fs.mkdirSync(path.join(ROOT, 'lessons/draft'), { recursive: true });
const fp = path.join(ROOT, 'lessons/draft', `${sc.id}_rows.md`);
fs.writeFileSync(fp, out);
console.log(`${fp} · 판 ${sc.panels.filter(p => !p.retired).length} · 행 ${nrow} · 카드 ${ncard}`);
