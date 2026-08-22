/* 음성 후크 사전 검증 (tools/hooks.json · tools/audit_phonetics.js)
 *
 * 왜 필요한가: 후크 감사는 지금까지 **손으로만 돌리는 도구**였다. 그래서
 *   ① 그림에서 소품이 사라져도 사전에 남은 죽은 후크를 아무도 못 잡았고
 *   ② 「뜻이 있는 약어라 면제」가 소리 없이 늘어나도 막을 것이 없었다.
 * 면제는 편하다 — 늘리는 만큼 감사가 눈을 감는다. 그래서 잠근다.
 *
 * ★ 후크판 「그린 것만 건다」 — 사전에 적은 소품이 그림(사실표)에 실제로 있어야 한다.
 */
const fs = require('fs'), path = require('path'), { execSync } = require('child_process');
const R = path.resolve(__dirname, '..');
let pass = 0, fail = 0;
const T = (n, f) => { try { const m = f(); console.log('  ✓', n, m === undefined ? '' : '— ' + m); pass++; }
                      catch (e) { console.log('  ✗', n, '—', String(e.message).split('\n')[0]); fail++; } };
const eq = (a, b, m) => { if (String(a) !== String(b)) throw new Error((m || '') + ' got ' + a + ' want ' + b); return a; };
const le = (a, b, m) => { if (!(a <= b)) throw new Error(m + ' ' + a + ' > 기준 ' + b + ' — 후크 미달이 늘었다(회귀)'); return a; };

const H = JSON.parse(fs.readFileSync(path.join(R, 'tools/hooks.json'), 'utf8'));
const BL = JSON.parse(fs.readFileSync(path.join(R, 'test/baseline.json'), 'utf8'));

console.log('\n── A. 사전의 모양 ──');
T('hooks 항목마다 props·형태·왜 가 있다', () => {
  const bad = Object.entries(H.hooks).filter(([k, v]) =>
    !v || !Array.isArray(v.props) || !v.props.length || !v['형태'] || !v['왜']);
  if (bad.length) throw new Error('빠진 것 ' + bad.length + '건: ' + bad.map(x => x[0]).join(' '));
  return Object.keys(H.hooks).length + '건';
});
T('면제 항목마다 이유가 있다', () => {
  const L = (H['_뜻이있는약어'] || {})['목록'] || {};
  const bad = Object.entries(L).filter(([, v]) => !v || !String(v).trim());
  if (bad.length) throw new Error('이유 없는 면제 ' + bad.length + '건: ' + bad.map(x => x[0]).join(' '));
  return Object.keys(L).length + '건';
});
/* 같은 라벨이 양쪽에 있으면 판정이 두 벌이다 — 어느 쪽이 근거인지 알 수 없어진다 */
T('면제와 후크가 겹치지 않는다', () => {
  const L = Object.keys((H['_뜻이있는약어'] || {})['목록'] || {});
  const dup = L.filter(k => H.hooks[k]);
  if (dup.length) throw new Error('양쪽에 있는 라벨: ' + dup.join(' '));
  return '0건';
});

console.log('\n── B. 죽은 후크 (사전에는 있는데 그림에 없다) ──');
/* 소품이 덱 **어딘가**에 있기만 해서는 안 된다 — 그 라벨이 나오는 **그 판**에 있어야 한다.
   E2F 의 「F자 장대」가 s19p01 에 있다고 s03p04 의 fMet 이 나른 것이 되지는 않는다.
   판별은 tools/audit_phonetics.js --dead 가 한다(DATA 파서를 한 곳에 둔다). */
T('후크의 소품이 그 라벨이 나오는 판에 있다', () => {
  const o = execSync('node ' + path.join(R, 'tools/audit_phonetics.js') + ' --dead',
    { cwd: R, encoding: 'utf8', maxBuffer: 1e9 });
  const mm = o.match(/죽은 후크 (\d+)건(?::\s*(.*))?/);
  if (!mm) throw new Error('--dead 출력을 못 읽었다');
  const dead = mm[1] === '0' ? [] : String(mm[2] || '').trim().split(/\s+/).filter(Boolean);
  const allow = BL.deadHooks || [];
  const bad = dead.filter(k => !allow.includes(k));
  if (bad.length) throw new Error('그 판에 소품이 없는 후크 ' + bad.length + '건: ' + bad.join(' '));
  return dead.length ? '죽은 후크 ' + dead.length + '건 — 전부 baseline.deadHooks 에 기록됨' : '0건';
});

console.log('\n── C. 래칫 — 후크 미달은 늘지 않는다 ──');
const sum = execSync('node ' + path.join(R, 'tools/audit_phonetics.js') + ' --sum',
  { cwd: R, encoding: 'utf8', maxBuffer: 1e9 });
const m = sum.match(/안 나르는 행 (\d+)\s*·\s*패널 (\d+)개\s*·\s*카드 (\d+)장/);
if (!m) { console.log('  ✗ 감사 출력을 못 읽었다'); fail++; }
else {
  const [, rows, panels, cards] = m.map(Number);
  T('후크 미달 행이 늘지 않는다', () => le(rows, BL.hookRows, '미달 행') + '행');
  T('후크 미달 판이 늘지 않는다', () => le(panels, BL.hookPanels, '미달 판') + '판');
  T('후크 미달 카드가 늘지 않는다', () => le(cards, BL.hookCards, '미달 장') + '장');
}
/* 면제는 늘어나도 되지만 **소리 없이는 안 된다** — baseline 을 고치는 손이 한 번 더 들어가야 한다 */
T('면제 목록이 소리 없이 늘지 않는다', () => {
  const n = Object.keys((H['_뜻이있는약어'] || {})['목록'] || {}).length;
  if (n > BL.meaningfulAbbr) throw new Error(
    '면제가 ' + n + '건으로 늘었다(기준 ' + BL.meaningfulAbbr + '). '
    + '늘리려면 baseline.meaningfulAbbr 을 고치면서 왜 면제인지 hooks.json 에 이유를 남긴다');
  return n + '건';
});

console.log('\n' + (fail ? '❌' : '✅') + ' 후크 사전 통과 ' + pass + ' / 실패 ' + fail);
process.exit(fail ? 1 : 0);
