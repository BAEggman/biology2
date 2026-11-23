#!/usr/bin/env node
/* 문 3 — 판 낱말(2026-11-23 · 11-19 지시서 §4.3). obj 에 판 · 화살표 · 글자를 적은 정거장이 과마다 기준선(test/boards_baseline.json)보다 늘지 않는다.
   허용(tools/cue/boards_ok.json)은 까닭이 「허용 — 」으로 시작한다. */
const fs = require('fs'), path = require('path');
const R = path.join(__dirname, '..');
const { scan, byLesson } = require('../tools/audit_lesson_boards.js');
let bad = 0; const ok = (c, m) => { console.log((c ? '  ✓ ' : '  ✗ ') + m); if (!c) bad++; };
const BF = path.join(R, 'test/boards_baseline.json'), B = JSON.parse(fs.readFileSync(BF, 'utf8'));
const rs = scan(), m = byLesson(rs);
if (process.argv[2] === '--lower') { for (const [L, v] of Object.entries(m)) if (B.과[L] === undefined || v < B.과[L]) B.과[L] = v; fs.writeFileSync(BF, JSON.stringify(B, null, 1) + '\n'); console.log('기준선을 내림'); process.exit(0); }
const up = Object.entries(m).filter(([L, v]) => v > (B.과[L] ?? 0));
ok(up.length === 0, `과마다 판 낱말 정거장이 기준선보다 늘지 않음(지금 ${Object.values(m).reduce((a, b) => a + b, 0)} · 허용 ${rs.filter(r => r.허용).length})${up.length ? ' — ' + up.map(([L, v]) => `${L} ${B.과[L] ?? 0}→${v}`).join(' · ') : ''}`);
const OK = JSON.parse(fs.readFileSync(path.join(R, 'tools/cue/boards_ok.json'), 'utf8'))['허용'] || {};
ok(Object.values(OK).every(v => /^허용 — .{4,}/.test(v)), `허용 ${Object.keys(OK).length} 줄마다 까닭`);
console.log(bad ? '\n❌ 문 3 판 낱말 ' + bad + '곳 실패' : '\n✅ 문 3 판 낱말 통과');
process.exit(bad ? 1 : 0);
