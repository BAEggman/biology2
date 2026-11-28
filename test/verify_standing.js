#!/usr/bin/env node
/* 상시 요청 문 — 2026-11-23 · tools/plan/2026-11-23/지시서_상시요청_실행차례.md §2
   ① CLAUDE.md 와 tools/plan/상시요청.md 가 있고, 요청 여섯 줄마다 상태 · 증거 칸이 차 있다
   ② 「끝」이라 적힌 요청은 그 증거(테스트 · 산출물)가 저장소에 실제로 있다
   ③ 6+1 문: 기준선(test/cue_baseline.json) 뒤로 hook · obj 가 바뀐 정거장은 tools/cue/jobs/index.json 의 기록이 지금 해시를 덮는다
      (일감 기록은 6+1 을 실제로 돌린 폴더 — packet · rN_가 ~ 바 · rN_judge — 이거나,
       사용자가 고르기 화면에서 고른 일감 — picks.json 의 「고름」 + 그 과의 심판 확인 기록 확인_<과>.md — 일 때만 센다) */
const fs = require('fs'), path = require('path');
const R = path.join(__dirname, '..');
const { current, unrecorded, jobDone, jobOk, jobCovers, pickLessons } = require('../tools/cue/jobs/cuehash');
let bad = 0; const ok = (c, m) => { console.log((c ? '  ✓ ' : '  ✗ ') + m); if (!c) bad++; };
const P = f => path.join(R, f), has = f => fs.existsSync(P(f));

// ① 장치가 있다
ok(has('CLAUDE.md') && /상시요청\.md/.test(fs.readFileSync(P('CLAUDE.md'), 'utf8')), 'CLAUDE.md 가 있고 상시요청.md 를 먼저 읽으라고 한다');
ok(has('CLAUDE.md') && fs.readFileSync(P('CLAUDE.md'), 'utf8').split('\n').filter(l => l.trim()).length <= 24, 'CLAUDE.md 는 짧다(스무 줄 안팎)');
const S = has('tools/plan/상시요청.md') ? fs.readFileSync(P('tools/plan/상시요청.md'), 'utf8') : '';
ok(!!S, 'tools/plan/상시요청.md 가 있다');
function rows(src) {
  const out = {};
  for (const l of src.split('\n')) { const m = /^\|\s*([1-6])\s*\|(.*)\|\s*$/.exec(l); if (!m) continue;
    const c = m[2].split('|').map(x => x.trim()); out[m[1]] = { 요청: c[0], 상태: c[1], 증거: c[2], 다음: c[3] }; }
  return out;
}
const T = rows(S);
ok(Object.keys(T).length === 6, `요청 여섯 줄(지금 ${Object.keys(T).length})`);
const STATE = /^(안 함|하는 중|끝)/;
for (const [n, r] of Object.entries(T)) ok(STATE.test(r.상태 || '') && (r.증거 || '').length >= 8 && (r.다음 || '').length >= 2, `요청 ${n}: 상태 「${(r.상태 || '').slice(0, 14)}」 · 증거 · 다음 일이 찼다`);
ok(/사용자의 말/.test(S) && /phonetic cue/.test(S) && /자매염색분체/.test(S) && /독립 에이전트 6개/.test(S) && /별표/.test(S), '사용자의 말 원문이 그대로 있다');

// ② 「끝」의 증거
const PROOF = { 1: ['test/verify_lessonui.js'], 2: ['test/verify_names.js'], 3: ['test/verify_canon.js'], 4: ['test/verify_standing.js', 'tools/cue/jobs/index.json'], 5: ['tools/audit/2026-11-23/덱감사.json'], 6: ['CLAUDE.md', 'tools/plan/상시요청.md'] };
const doneOK = t => Object.entries(t).filter(([n, r]) => /^끝/.test(r.상태 || '')).every(([n]) => PROOF[n].every(has));
for (const [n, r] of Object.entries(T)) if (/^끝/.test(r.상태 || '')) ok(PROOF[n].every(has), `요청 ${n} 은 「끝」 — 증거 ${PROOF[n].join(' · ')} 가 있다`);
ok(doneOK({ 1: { 상태: '끝' } }) === has('test/verify_lessonui.js') && doneOK({ 6: { 상태: '끝' } }), '(자기 시험) 「끝」은 증거 파일이 있을 때만 통과');
const all = has('test/all.js') ? fs.readFileSync(P('test/all.js'), 'utf8') : '';
ok(/verify_standing\.js/.test(all), 'test/all.js 가 이 문을 돌린다');

// ③ 6+1 문
const B = JSON.parse(fs.readFileSync(P('test/cue_baseline.json'), 'utf8'))['정거장'];
const IDX = has('tools/cue/jobs/index.json') ? JSON.parse(fs.readFileSync(P('tools/cue/jobs/index.json'), 'utf8')) : null;
ok(!!IDX && IDX['일감'] && Array.isArray(IDX['다듬음']), 'tools/cue/jobs/index.json 이 있다');
const JD = id => path.join(R, 'tools/cue/jobs', id);
const jobEx = id => jobOk(JD(id));
for (const id of Object.keys((IDX || {})['일감'] || {})) ok(jobEx(id), `일감 ${id}: 꾸러미 · 제안 · 심판이 남아 있다(사용자 고름 일감이면 picks.json · 확인_<과>.md)`);
// 사용자 고름 일감이 바꾼 정거장은 그 과의 심판 확인 기록이 있어야 한다
const uncov = [];
for (const [id, j] of Object.entries((IDX || {})['일감'] || {})) for (const k of Object.keys(j['닿은'] || {})) if (!jobCovers(JD(id), k)) uncov.push(id + ' ' + k);
ok(uncov.length === 0, `사용자 고름 일감이 바꾼 정거장은 그 과의 심판 확인 기록(확인_<과>.md)이 있다${uncov.length ? ' — 없음: ' + uncov.slice(0, 8).join(' · ') : ''}`);
const cur = current(R);
const miss = unrecorded(B, cur, IDX, jobEx);
ok(miss.length === 0, `기준선 뒤 hook · obj 가 바뀐 정거장은 모두 6+1 기록이 있다${miss.length ? ' — 기록 없음: ' + miss.slice(0, 12).join(' ') + (miss.length > 12 ? ' …' + miss.length : '') + ' (node tools/cue/jobs/record.js <일감> <과|sid> · 다듬기는 --why 다듬음)' : ''}`);
// 자기 시험 — 기록 없는 바꿈은 잡히고, 기록하면 풀리고, 기록 뒤 또 바꾸면 다시 잡힌다
const k = Object.keys(cur)[0], c2 = JSON.parse(JSON.stringify(cur)); c2[k] = { hook: 'x', obj: cur[k].obj };
ok(unrecorded(B, c2, { 일감: {}, 다듬음: [] }, () => true).includes(k), '(자기 시험) 기록 없이 hook 을 바꾸면 막힌다');
ok(!unrecorded(B, c2, { 일감: { J: { 닿은: { [k]: c2[k] } } }, 다듬음: [] }, () => true).includes(k), '(자기 시험) 6+1 기록이 있으면 통과');
ok(unrecorded(B, c2, { 일감: { J: { 닿은: { [k]: c2[k] } } }, 다듬음: [] }, () => false).includes(k), '(자기 시험) 6+1 을 돌린 흔적이 없는 일감의 기록은 세지 않는다');
const c3 = JSON.parse(JSON.stringify(c2)); c3[k].hook = 'y';
ok(unrecorded(B, c3, { 일감: { J: { 닿은: { [k]: c2[k] } } }, 다듬음: [] }, () => true).includes(k), '(자기 시험) 기록한 뒤 또 바꾸면 다시 막힌다');
ok(!unrecorded(B, c2, { 일감: {}, 다듬음: [{ 닿은: { [k]: c2[k] } }] }, () => true).includes(k), '(자기 시험) 다듬음 기록도 통과');

// 자기 시험 — 사용자 고름 일감: picks 만 있으면 안 되고, 그 과의 확인 기록이 있어야 하며, 다른 과는 덮지 않는다
{
  const os = require('os'), T = fs.mkdtempSync(path.join(os.tmpdir(), 'pickjob-'));
  ok(!jobOk(T), '(자기 시험) 빈 폴더는 일감이 아니다');
  fs.writeFileSync(path.join(T, 'picks.json'), JSON.stringify({ a: { 결정: '고름', 물건: 'x' } }));
  ok(!jobOk(T), '(자기 시험) picks.json 만 있고 심판 확인 기록이 없으면 일감이 아니다');
  fs.writeFileSync(path.join(T, '확인_L99z.md'), '짧음');
  ok(!jobOk(T), '(자기 시험) 빈 껍데기 확인 기록은 세지 않는다');
  fs.writeFileSync(path.join(T, '확인_L99z.md'), '# 확인 L99z\n' + '카드 사실: 맞음 — 걸린 카드의 물음과 답을 하나씩 대조함. 예약 기호: 부딪치지 않음 — reserved.py 로 찾음.\n'.repeat(2));
  ok(jobOk(T) && pickLessons(T).join() === 'L99z', '(자기 시험) picks.json 의 「고름」 + 확인_<과>.md 가 있으면 사용자 고름 일감이다');
  ok(jobCovers(T, 'L99z|s1') && !jobCovers(T, 'L98a|s1'), '(자기 시험) 확인 기록이 있는 과의 정거장만 덮는다');
  fs.writeFileSync(path.join(T, 'picks.json'), JSON.stringify({ a: { 결정: '한 판 더' } }));
  ok(!jobOk(T), '(자기 시험) 「고름」이 하나도 없으면 일감이 아니다');
  fs.rmSync(T, { recursive: true, force: true });
}

console.log(bad ? '\n❌ 상시 요청 문 ' + bad + '곳 실패' : '\n✅ 상시 요청 문 통과');
process.exit(bad ? 1 : 0);
