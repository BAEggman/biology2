#!/usr/bin/env node
/* 문 1 — 이름 고리 장부(2026-11-23 · 11-19 지시서 §4.1 · 상시 요청 지시서 §4)
   ① 과마다 N(사전에 고리 없음) + N′(사전에 있는데 흘림) 짝 수가 기준선(test/names_baseline.json)보다 늘지 않는다 — 줄면 --lower 로 기준선을 내린다
   ② closed(고쳐서 닫은 과)는 0
   ③ N · N′ 짝은 모두 이름 장부(tools/cue/names/장부.json)에 줄이 있다 — 덱 감사를 마친 과(덱감사.json 의 「끝난 과」)의 줄은 갈래 · 상태가 찼다
   ④ 면제는 새 통(hooks.json 「_이름고리_면제」)만 — 낱말마다 정해진 꼴의 까닭
   ⑤ 장부의 손 칸은 가름.json 과 같다 — 장부.json 을 직접 고치면 다음 mkledger.py --write 에 지워진다(2026-11-28 · 11-26 에 고른 18 줄이 그렇게 적혀 있었음) */
const fs = require('fs'), path = require('path');
const R = path.join(__dirname, '..');
const { compute, byLesson } = require('../tools/audit_lesson_names.js');
let bad = 0; const ok = (c, m) => { console.log((c ? '  ✓ ' : '  ✗ ') + m); if (!c) bad++; };
const BF = path.join(R, 'test/names_baseline.json'), B = JSON.parse(fs.readFileSync(BF, 'utf8'));
const rows = compute(), m = byLesson(rows);
if (process.argv[2] === '--lower') { let n = 0; for (const [L, v] of Object.entries(m)) if (B.과[L] === undefined || v < B.과[L]) { B.과[L] = v; n++; } fs.writeFileSync(BF, JSON.stringify(B, null, 1) + '\n'); console.log('기준선을 내림 —', n, '과'); process.exit(0); }
const up = Object.entries(m).filter(([L, v]) => v > (B.과[L] ?? 0));
ok(up.length === 0, `과마다 N + N′ 가 기준선보다 늘지 않음(합 ${Object.values(m).reduce((a, b) => a + b, 0)} · 기준선 합 ${Object.values(B.과).reduce((a, b) => a + b, 0)})${up.length ? ' — 는 과: ' + up.map(([L, v]) => `${L} ${B.과[L] ?? 0}→${v}`).join(' · ') : ''}`);
const down = Object.entries(m).filter(([L, v]) => v < (B.과[L] ?? 0));
if (down.length) console.log('  · 줄어든 과(node test/verify_names.js --lower 로 기준선을 내려라):', down.map(([L, v]) => `${L} ${B.과[L]}→${v}`).join(' · '));
const cl = (B.closed || []).filter(L => m[L] > 0);
ok(cl.length === 0, `닫은 과 ${(B.closed || []).length} 는 0${cl.length ? ' — 남은 과: ' + cl.join(' ') : ''}`);
const LED = JSON.parse(fs.readFileSync(path.join(R, 'tools/cue/names/장부.json'), 'utf8'));
const miss = rows.filter(r => (r.gate === 'N' || r.gate === 'N′') && !LED[r.lesson + '|' + r.term]);
ok(miss.length === 0, `N · N′ 짝이 모두 이름 장부에 있다${miss.length ? ' — 없는 짝: ' + miss.slice(0, 8).map(r => r.lesson + ' ' + r.term).join(' · ') + ' (python3 tools/cue/names/mkledger.py --write)' : ''}`);
const AF = path.join(R, 'tools/audit/2026-11-23/덱감사.json');
const done = fs.existsSync(AF) ? (JSON.parse(fs.readFileSync(AF, 'utf8'))['끝난 과'] || []) : [];
const open = Object.values(LED).filter(e => done.includes(e.과) && !(e.갈래 && e.상태));
ok(open.length === 0, `감사를 마친 과 ${done.length} 의 장부 줄은 갈래 · 상태가 찼다${open.length ? ' — 빈 줄: ' + open.slice(0, 8).map(e => e.과 + ' ' + e.낱말).join(' · ') : ''}`);
const GF = path.join(R, 'tools/cue/names/가름.json'), GAR = fs.existsSync(GF) ? JSON.parse(fs.readFileSync(GF, 'utf8')) : {};
const drift = Object.entries(LED).filter(([k, e]) => ['갈래', '처방', '근거', '일감', '상태'].some(c => (e[c] || '') !== ((GAR[k] || {})[c] || '')));
ok(drift.length === 0, `장부의 손 칸(갈래 · 처방 · 근거 · 일감 · 상태)은 가름.json 과 같다${drift.length ? ' — 어긋난 줄: ' + drift.slice(0, 8).map(x => x[0]).join(' · ') + ' (장부.json 을 직접 고치지 말고 tools/cue/names/setrow.py 로)' : ''}`);
const H = JSON.parse(fs.readFileSync(path.join(R, 'tools/hooks.json'), 'utf8'));
const EX = (H._이름고리_면제 || {}).목록 || {};
const badEx = Object.entries(EX).filter(([k, v]) => typeof v !== 'string' || !/^(일상어 — |이름 뜻 그대로 그림\(④\) — |발문이 이름을 줌 — )/.test(v));
ok(badEx.length === 0, `새 면제 통 ${Object.keys(EX).length} 줄의 까닭이 정해진 꼴${badEx.length ? ' — ' + badEx.map(x => x[0]).join(' · ') : ''}`);
ok(rows.every(r => r.gate !== '면제' || r.why), '면제로 센 짝은 모두 까닭이 있다');
console.log(bad ? '\n❌ 문 1 이름 고리 ' + bad + '곳 실패' : '\n✅ 문 1 이름 고리 통과');
process.exit(bad ? 1 : 0);
