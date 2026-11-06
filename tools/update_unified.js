#!/usr/bin/env node
/* update_unified.js — 이미 통합한 판(sNNuNN)에 사양(spec.json)의 글을 다시 입힌다. 2026-11-06
 *
 * merge_scene.js 는 낱장 → 통합판을 한 번만 만든다(옛 낱장이 물러난 뒤로는 다시 못 돌린다).
 * 그림을 고친 뒤(v2 · v3 …) 소품 칸 · 사실 칸 · br · bx · 라벨이 바뀌면 이 도구로 같은 사양을 다시 입힌다.
 *   - 카드(행의 셋째 자리)는 지금 덱의 것을 그대로 둔다 — 글만 바꾼다.
 *   - 사실 칸: spec 의 fact 가 있으면 그것, 없으면(null) 지금 덱의 사실 칸 그대로.
 *   - 행 수가 다르면 멈춘다(행을 늘리거나 줄이는 일은 이 도구가 하지 않는다).
 *   - tools/blind/manifest.json 의 그 판 항목(prop · fact · label)도 함께 고친다.
 *
 *   node tools/update_unified.js <spec.json> [--check]
 */
const fs = require('fs'), path = require('path');
const R = path.resolve(__dirname, '..');
const specPath = process.argv[2]; const CHECK = process.argv.includes('--check');
if (!specPath) { console.error('사용: node tools/update_unified.js <spec.json> [--check]'); process.exit(2); }
const S = JSON.parse(fs.readFileSync(specPath, 'utf8'));
const die = m => { console.error('✗ ' + m); process.exit(1); };
const skPath = path.join(R, 'sketchy.html');
let sk = fs.readFileSync(skPath, 'utf8');
function balanced(src, from, open, close) {
  const st = src.indexOf(open, from); let d = 0, q = null, esc = false;
  for (let k = st; k < src.length; k++) { const c = src[k];
    if (q) { if (esc) { esc = false; continue } if (c === '\\') { esc = true; continue } if (c === q) q = null; continue }
    if (c === '"' || c === "'" || c === '`') { q = c; continue }
    if (c === open) d++; else if (c === close) { d--; if (!d) return [st, k + 1]; } }
  die('괄호가 안 맞는다');
}
const [dst, dend] = balanced(sk, sk.indexOf('const DATA'), '[', ']');
const DATA = eval('(' + sk.slice(dst, dend) + ')');
const sc = DATA.find(s => s.id === S.scene); if (!sc) die('장면 없음 ' + S.scene);
const P = sc.panels.find(p => p.id === S.uid); if (!P) die('통합판 없음 ' + S.uid + ' — 먼저 merge_scene.js');
const strip = x => String(x == null ? '' : x).replace(/<[^>]+>/g, '');
if (!S.frame || S.frame.length !== 2) die('frame 은 [소품, 사실]');
const want = 1 + S.rows.length;
if (P.f.length !== want) die(`행 수가 다르다 — 덱 ${P.f.length} · 사양 ${want}`);
const newRows = P.f.map((row, i) => {
  const cards = row[2];
  let prop, fact;
  if (i === 0) { prop = S.frame[0]; fact = S.frame[1]; }
  else { const r = S.rows[i - 1]; prop = r.prop; fact = r.fact == null ? row[1] : r.fact; }
  if (!prop) die('소품 칸이 비었다 — 행 ' + (i + 1));
  return cards && cards.length ? [prop, fact, cards] : [prop, fact];
});
let changed = 0;
newRows.forEach((r, i) => { if (r[0] !== P.f[i][0]) { changed++; console.log(`  행 ${i + 1} 소품: ${strip(P.f[i][0]).slice(0, 50)} → ${strip(r[0]).slice(0, 50)}`); }
  if (r[1] !== P.f[i][1]) { changed++; console.log(`  행 ${i + 1} 사실: ${strip(P.f[i][1]).slice(0, 50)} → ${strip(r[1]).slice(0, 50)}`); } });
const bx = S.bx; if (/`|\$\{/.test(bx || '')) die('bx 에 ` 또는 ${ 가 있다');
if (bx !== P.bx) { changed++; console.log('  bx 바뀜'); }
if (S.br !== P.br) { changed++; console.log('  br 바뀜'); }
console.log(`${S.uid}: 바뀐 칸 ${changed}`);
if (CHECK) { console.log('✅ --check (아무것도 안 썼다)'); process.exit(0); }
/* 판 원문 자리 찾기 → 같은 꼴로 다시 쓴다(merge_scene.js 와 같은 직렬화) */
const sq = s => { if (/['\\\n]/.test(s)) die('홑따옴표 문자열에 못 넣는 글자: ' + s.slice(0, 40)); return "'" + s + "'"; };
const jsRow = r => '[' + r.map(x => JSON.stringify(x)).join(',') + ']';
const st = sk.indexOf(`{id:'${S.uid}',`); if (st < 0 || sk.indexOf(`{id:'${S.uid}',`, st + 5) >= 0) die('판 머리를 하나로 못 찾았다');
const [pst, pend] = balanced(sk, st, '{', '}');
const extra = Object.keys(P).filter(k => !['id', 't', 'wide', 'br', 'bx', 'f'].includes(k)); if (extra.length) die(S.uid + ' 에 다루지 않는 칸: ' + extra.join(','));
const panel = `{id:'${S.uid}',t:${sq(S.title || P.t)},${P.wide ? 'wide:1,' : ''}br:${sq(S.br)},bx:\`${bx}\`,f:[` + newRows.map(jsRow).join(',\n  ') + ']}';
sk = sk.slice(0, pst) + panel + sk.slice(pend);
fs.writeFileSync(skPath, sk);
/* manifest */
const manPath = path.join(R, 'tools/blind/manifest.json');
const man = JSON.parse(fs.readFileSync(manPath, 'utf8'));
const e = man.find(m => m.pid === S.uid); if (!e) die('manifest 에 ' + S.uid + ' 없음');
if (S.title) e.title = S.title;
e.rows = newRows.map((r, i) => ({ n: i + 1, prop: strip(r[0]), fact: strip(r[1]), label: (S.labels && S.labels[i]) || (e.rows[i] && e.rows[i].label) || '', cards: (r[2] || []).length }));
fs.writeFileSync(manPath, JSON.stringify(man, null, 1));
console.log('sketchy.html · manifest 고침 → node build.js && node test/all.js');
