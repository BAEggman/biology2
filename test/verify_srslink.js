#!/usr/bin/env node
/* ★ 카드 ↔ 그림 링크 이음매 (2026-08-26 신설)
 *
 * 이 덱에는 링크를 보는 검사가 여럿 있었지만 전부 **한 조각씩**이었다 —
 * verify_build 는 PMAP 이 바뀌었는지, verify_links 는 커버·고아, smoke 는 화면이 뜨는지.
 * 그런데 「사실표 ID → PMAP → PROW → img/webp → PFACT 표 → 강조 행」이라는
 * **사슬 전체**를 끝에서 끝까지 따라가는 검사는 없었다.
 *
 * tools/audit_srslink.js 가 그 사슬을 따라가고, 여기서는 그 결과를 잠근다.
 */
const { execSync } = require('child_process'), path = require('path'), fs = require('fs');
const R = path.resolve(__dirname, '..');
const BL = JSON.parse(fs.readFileSync(path.join(R, 'test/baseline.json'), 'utf8'));
let pass = 0, fail = 0;
const T = (n, f) => { try { const m = f(); console.log('  ✓', n, m === undefined ? '' : '— ' + m); pass++; }
                      catch (e) { console.log('  ✗', n, '—', String(e.message).split('\n')[0]); fail++; } };

let S;
console.log('\n── 사슬 전체 ──');
T('audit_srslink 가 돈다', () => {
  S = JSON.parse(execSync('node ' + path.join(R, 'tools/audit_srslink.js') + ' --sum',
    { cwd: R, encoding: 'utf8', maxBuffer: 1e9 }));
  return '참조 ' + S['사실표참조'] + '건';
});
if (S) {
  T('★ 이음매 오류가 없다', () => { if (S['오류']) throw new Error(S['오류'] + '건 — tools/audit_srslink.js 로 본다'); return '0건'; });
  T('경고가 늘지 않는다', () => { if (S['경고'] > (BL.srsWarn || 0)) throw new Error(S['경고'] + ' > 기준 ' + (BL.srsWarn || 0)); return S['경고'] + '건'; });
  T('강조 행 검사가 참조 수만큼 돈다', () => {
    if (S['강조검사'] < S['사실표참조']) throw new Error('강조 ' + S['강조검사'] + ' < 참조 ' + S['사실표참조']);
    return S['강조검사'] + '건'; });
  T('아무 판도 안 쓰는 그림이 늘지 않는다', () => {
    if (S['안쓰는그림'] > (BL.strayImg || 0)) throw new Error(S['안쓰는그림'] + ' > 기준 ' + (BL.strayImg || 0));
    return S['안쓰는그림'] + '장'; });
  T('고아 판이 늘지 않는다', () => {
    if (S['고아'] > BL.orphan) throw new Error(S['고아'] + ' > 기준 ' + BL.orphan); return S['고아'] + '개'; });
}
console.log('\n' + (fail ? '❌' : '✅') + ' 링크 이음매 통과 ' + pass + ' / 실패 ' + fail);
process.exit(fail ? 1 : 0);
