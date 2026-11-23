#!/usr/bin/env node
/* 문 2 — 기호 일관(2026-11-23 · 11-19 지시서 §4.2). tools/cue/canon.json 의 규칙마다: 개념이 나오는 과는 정본 물건을 쓴다 · 같은 물건 · 다른 뜻은 예외에 적힌 것만.
   기준선(test/canon_baseline.json)에 없는 어긋남이 생기면 실패 · 규칙마다 「정한 곳」이 있다 · 예외마다 까닭. */
const fs = require('fs'), path = require('path');
const R = path.join(__dirname, '..');
const { check } = require('../tools/audit_lesson_canon.js');
let bad = 0; const ok = (c, m) => { console.log((c ? '  ✓ ' : '  ✗ ') + m); if (!c) bad++; };
const BF = path.join(R, 'test/canon_baseline.json'), B = JSON.parse(fs.readFileSync(BF, 'utf8'));
const C = JSON.parse(fs.readFileSync(path.join(R, 'tools/cue/canon.json'), 'utf8'))['규칙'];
const now = check().map(x => x.규칙 + '|' + x.과);
if (process.argv[2] === '--lower') { B.어긋남 = B.어긋남.filter(k => now.includes(k)); fs.writeFileSync(BF, JSON.stringify(B, null, 1) + '\n'); console.log('기준선', B.어긋남.length); process.exit(0); }
const neu = now.filter(k => !B.어긋남.includes(k));
ok(neu.length === 0, `기준선(${B.어긋남.length}) 밖의 어긋남 없음${neu.length ? ' — 새로: ' + neu.join(' · ') : ''}`);
const fixed = B.어긋남.filter(k => !now.includes(k)); if (fixed.length) console.log('  · 닫힌 어긋남(node test/verify_canon.js --lower):', fixed.join(' · '));
ok(C.every(r => r['개념'] && r['때'] && (r['있어야'] || []).length && r['정한 곳']), `규칙 ${C.length} 마다 개념 · 때 · 있어야 · 정한 곳`);
ok(C.every(r => Object.values(r['예외'] || {}).every(v => typeof v === 'string' && v.length >= 4)), '예외마다 까닭');
ok(!now.some(k => k.endsWith('|-')), '규칙의 「때」를 모두 읽을 수 있다');
// 자기 시험 — 정본 물건이 빠진 과를 지어내면 잡힌다
const t = check([{ 개념: '시험', 때: 'fact 또는 카드 답에 알도스테론', 있어야: ['없는물건xyz'], 예외: {} }]);
ok(t.length > 0, '(자기 시험) 정본 물건이 없으면 잡힌다');
console.log(bad ? '\n❌ 문 2 기호 일관 ' + bad + '곳 실패' : '\n✅ 문 2 기호 일관 통과');
process.exit(bad ? 1 : 0);
