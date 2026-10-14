#!/usr/bin/env node
/* merge_scene.js — 단원 통합: 한 장면의 낱장 여럿을 통합판(sNNu01) 하나로 바꾼다. 2026-10-14
 *
 * s08u01 을 손으로 한 절차(scratchpad/u08/make_s08u01.py)를 모든 단원에 쓸 수 있게 옮겼다.
 * 그림은 먼저 그려 img/<uid>.webp 로 설치돼 있어야 한다(install_img.py). 이 도구는 **데이터**만 옮긴다.
 *
 *   node tools/merge_scene.js <spec.json> [--check]
 *
 * spec.json:
 * {
 *   "scene": "s32",                       // 장면 id
 *   "uid": "s32u01",                      // 통합판 id
 *   "scene_title": "물레방아 담장",        // 장면 제목(바꾸지 않으면 생략)
 *   "title": "담장과 펌프집 · 물레방아 · 방해자 셋",   // 통합판 제목
 *   "from": ["s32p01","s32p02","s32p03"], // 합칠 낱장(순서대로) — 장면의 panels 전부여야 한다(일부 통합은 아직 지원 안 함)
 *   "br": "...", "bx": "<p>...</p>",      // 통합판 다리 · 본문(옛 bx 를 옮겨 쓰려면 bx_from: true → 옛 bx 를 순서대로 이어 붙인다)
 *   "frame": ["소품", "사실"],             // 틀 행(카드 없음) — 첫 행
 *   "rows": [                             // 그 뒤 행들 — 옛 행에서 카드를 가져온다
 *     {"from": "s32p01#1", "prop": "새 소품 글", "fact": null},   // fact null = 옛 사실 그대로 · 문자열 = 바꿈
 *     {"from": ["s32p01#0","s32p02#6"], "prop": "...", "fact": "..."},  // 둘을 한 행으로(카드 합침)
 *     {"from": null, "prop": "...", "fact": "...", "cards": []}         // 새 행(카드 없음)
 *   ],
 *   "why": "baseline.panelMerge 에 적을 까닭",
 *   "text_fixes": [["옛 글", "새 글"]]     // sketchy.html 전체에서 꼭 1번씩 맞아야 하는 치환(다른 판의 교차 참조 등)
 * }
 *
 * 하는 일: ① 옛 행 전부가 rows/frame 에 쓰였는지(빠진 카드 0) ② sketchy.html 장면 치환 ③ img/<옛>.webp → img/retired/ (git mv)
 *          ④ tools/retired/<scene>_<날짜>.json 에 옛 장면 + 옛행→새행 표 ⑤ baseline.panelMerge · pmapMoved(v10b 값 기준)
 *          ⑥ blind manifest(옛 판 빼고 새 판 넣기 · label 은 사실 첫 마디) ⑦ hooks.json 의 옛 id 언급은 바꾸지 않고 **목록만 찍는다**(손으로 고친다)
 * --check 는 ①만 하고 아무것도 쓰지 않는다. 끝나면 node build.js && node test/all.js 를 돌려라.
 */
const fs = require('fs'), path = require('path'), { execSync } = require('child_process');
const R = path.resolve(__dirname, '..');
const CHECK = process.argv.includes('--check');
const specPath = process.argv[2];
if (!specPath) { console.error('사용: node tools/merge_scene.js <spec.json> [--check]'); process.exit(2); }
const S = JSON.parse(fs.readFileSync(specPath, 'utf8'));
const die = m => { console.error('✗ ' + m); process.exit(1); };

/* ── DATA 읽기 (build.js 와 같은 파서) ── */
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
const old = Object.fromEntries(sc.panels.map(p => [p.id, p]));
const ids = sc.panels.map(p => p.id);
if (JSON.stringify(ids) !== JSON.stringify(S.from)) die('from 이 장면의 panels 와 다르다: ' + ids.join(',') + ' vs ' + S.from.join(','));
const strip = x => String(x == null ? '' : x).replace(/<[^>]+>/g, '');

/* ── ① 행 대조 ── */
const used = new Set(); const map = {};
const parseRef = ref => { const m = /^(s\d+p\d+[a-z]?)#(\d+)$/.exec(ref); if (!m || !old[m[1]] || !old[m[1]].f[+m[2]]) die('없는 옛 행 ' + ref); return [m[1], +m[2]]; };
const newRows = [];
if (!S.frame || S.frame.length !== 2) die('frame 은 [소품, 사실]');
newRows.push([S.frame[0], S.frame[1]]);
S.rows.forEach((r, i) => {
  const refs = r.from == null ? [] : (Array.isArray(r.from) ? r.from : [r.from]);
  let cards = [], fact = r.fact;
  refs.forEach(ref => { const [pid, k] = parseRef(ref); if (used.has(ref)) die('옛 행을 두 번 썼다 ' + ref); used.add(ref);
    map[ref] = S.uid + '#' + (i + 1); const o = old[pid].f[k]; if (o[2]) cards.push(...o[2]); if (fact == null) fact = o[1]; });
  if (refs.length === 0 && r.cards) cards = r.cards.slice();
  if (fact == null) die('사실 칸이 비었다 — 행 ' + (i + 1));
  if (!r.prop) die('소품 칸이 비었다 — 행 ' + (i + 1));
  cards = [...new Set(cards)];
  newRows.push(cards.length ? [r.prop, fact, cards] : [r.prop, fact]);
});
const missing = [];
for (const p of sc.panels) p.f.forEach((row, k) => { const ref = p.id + '#' + k; if (!used.has(ref)) missing.push(ref + (row[2] && row[2].length ? ' [카드 ' + row[2].length + ']' : '')); });
const oldCards = sc.panels.flatMap(p => p.f.flatMap(r => r[2] || []));
const newCards = newRows.flatMap(r => r[2] || []);
const lost = oldCards.filter(c => !newCards.includes(c));
console.log(`옛 행 ${sc.panels.reduce((a, p) => a + p.f.length, 0)} → 새 행 ${newRows.length}(틀 1) · 카드 ${new Set(oldCards).size} → ${new Set(newCards).size}`);
if (missing.length) console.log('  ⚠ 안 쓴 옛 행: ' + missing.join(' · ') + '  (카드가 있으면 안 된다 — 틀 행에 흡수하려면 from 에 넣어라)');
if (lost.length) die('빠진 카드 ' + lost.length + ': ' + lost.join(' '));
if (CHECK) { console.log('✅ --check 통과 (아무것도 안 썼다)'); process.exit(0); }

/* ── ② 장면 치환 ── */
const sq = s => { if (/['\\\n]/.test(s)) die('홑따옴표 문자열에 못 넣는 글자: ' + s.slice(0, 40)); return "'" + s + "'"; };
const jsRow = r => '[' + r.map(x => JSON.stringify(x)).join(',') + ']';
let bx = S.bx;
if (S.bx_from) bx = sc.panels.map(p => p.bx || '').join('') + (S.bx || '');
if (/`|\$\{/.test(bx || '')) die('bx 에 ` 또는 ${ 가 있다');
const traps = sc.traps ? "\n traps:[\n  " + sc.traps.map(sq).join(',\n  ') + ']' : '';
const nums = sc.nums ? ",\n nums:[\n  " + sc.nums.map(sq).join(',\n  ') + ']' : '';
const head = `{id:'${sc.id}',t:${sq(S.scene_title || sc.t)},gate:'${sc.gate}',unit:${sq(sc.unit)},panels:[\n`;
const panel = ` {id:'${S.uid}',t:${sq(S.title)},wide:1,br:${sq(S.br)},bx:\`${bx}\`,f:[` + newRows.map(jsRow).join(',\n  ') + ']}]';
const src = head + panel + (sc.traps ? ',' : '') + traps + nums + '}';
const st = sk.indexOf(`{id:'${sc.id}',`); if (st < 0 || sk.indexOf(`{id:'${sc.id}',`, st + 5) >= 0) die('장면 머리를 하나로 못 찾았다');
const [ost, oend] = balanced(sk, st, '{', '}');
sk = sk.slice(0, ost) + src + sk.slice(oend);
(S.text_fixes || []).forEach(([a, b]) => { const n = sk.split(a).length - 1; if (n !== 1) die(`text_fixes 「${a.slice(0, 40)}」 ${n}번 맞음`); sk = sk.replace(a, b); });
const left = ids.filter(id => sk.includes(id));
if (left.length) console.log('  ⚠ sketchy.html 에 옛 id 가 아직 남아 있다(교차 참조 — text_fixes 로 고쳐라): ' + left.join(' '));
fs.writeFileSync(skPath, sk);

/* ── ③ 그림 보관 ── */
fs.mkdirSync(path.join(R, 'img/retired'), { recursive: true });
for (const id of ids) { const f = path.join(R, 'img', id + '.webp'); if (fs.existsSync(f)) execSync(`git mv "img/${id}.webp" "img/retired/${id}.webp"`, { cwd: R }); }
if (!fs.existsSync(path.join(R, 'img', S.uid + '.webp'))) console.log('  ⚠ img/' + S.uid + '.webp 가 없다 — install_img.py 로 설치해야 build 가 통과한다');

/* ── ④ 옛 장면 보관 ── */
const today = new Date().toISOString().slice(0, 10);
fs.mkdirSync(path.join(R, 'tools/retired'), { recursive: true });
fs.writeFileSync(path.join(R, 'tools/retired', `${sc.id}_${strip(sc.t).replace(/\s+/g, '')}_${today}.json`),
  JSON.stringify({ _왜: `${today} 단원 통합 — ${sc.id} 「${sc.t}」 ${ids.length}판을 통합판 ${S.uid} 한 장으로 다시 그렸다. ` + (S.why || ''), merged_into: S.uid, 옛행_새행: map, scene: sc }, null, 1));

/* ── ⑤ baseline ── */
const blPath = path.join(R, 'test/baseline.json');
const BL = JSON.parse(fs.readFileSync(blPath, 'utf8'));
BL.panelMerge = BL.panelMerge || {};
BL.panelMerge[S.uid] = { from: ids, why: S.why || '' };
const prev = fs.readFileSync(path.join(R, 'test/.tmp/index.v10b.html'), 'utf8');
const J = (s, n) => JSON.parse(s.match(new RegExp('var ' + n + '=(\\{.*?\\});', 's'))[1]);
const norm = v => (Array.isArray(v) ? v : [v]).slice().sort().join('|');
const P0 = J(prev, 'PMAP');
/* 새 PMAP 값은 build 가 정하므로 여기서 미리 센다: 카드 → 걸린 판 집합(통합판 포함) */
const cur = {};
for (const s2 of DATA) for (const p of (s2.id === sc.id ? [] : s2.panels)) for (const r of (p.f || [])) for (const c of (r[2] || [])) (cur[c] = cur[c] || new Set()).add(p.id);
for (const r of newRows) for (const c of (r[2] || [])) (cur[c] = cur[c] || new Set()).add(S.uid);
BL.pmapMoved = BL.pmapMoved || {};
let moved = 0;
for (const c of new Set(oldCards)) { if (!(c in P0)) continue; const from = norm(P0[c]); const to = [...cur[c]].sort().join('|'); if (from === to) continue;
  const prevRec = BL.pmapMoved[c];
  const why = `${today} 단원 통합 — ${sc.id} ${ids.join('·')} → ${S.uid}. 행은 그대로 옮겼다(tools/retired 의 옛행_새행).`;
  if (prevRec) { if (prevRec.from !== from) die('pmapMoved[' + c + '].from 이 v10b 값과 다르다'); prevRec.to = to; prevRec.why += ' ｜ ' + why; }
  else BL.pmapMoved[c] = { from, to, why };
  moved++; }
fs.writeFileSync(blPath, JSON.stringify(BL, null, 1));
console.log(`baseline: panelMerge[${S.uid}] · pmapMoved ${moved}건`);

/* ── ⑥ blind manifest ── */
const manPath = path.join(R, 'tools/blind/manifest.json');
const man = JSON.parse(fs.readFileSync(manPath, 'utf8'));
const i0 = man.findIndex(m => m.pid === ids[0]);
const label = f => { const t = strip(f).replace(/^★\s*/, ''); const m = /^(.{4,40}?)(?: — |\.|,|\(|·|:)/.exec(t); return (m ? m[1] : t.slice(0, 40)).trim(); };
const entry = { pid: S.uid, img: 'img/' + S.uid + '.webp', scene: S.scene_title || sc.t, unit: sc.unit, title: S.title,
  rows: newRows.map((r, i) => ({ n: i + 1, prop: strip(r[0]), fact: strip(r[1]), label: (S.labels && S.labels[i]) || label(r[1]), cards: (r[2] || []).length })) };
const out = man.filter(m => !ids.includes(m.pid)); out.splice(i0 < 0 ? out.length : i0, 0, entry);
fs.writeFileSync(manPath, JSON.stringify(out, null, 1));
console.log(`manifest ${man.length} → ${out.length} (label 은 사실 첫 마디 — spec.labels 로 바꿀 수 있다)`);

/* ── ⑦ hooks.json 언급 목록 ── */
const H = fs.readFileSync(path.join(R, 'tools/hooks.json'), 'utf8');
const mentions = ids.filter(id => H.includes(id)).map(id => id + '×' + H.split(id).length - 1);
if (mentions.length) console.log('  ⚠ tools/hooks.json 이 옛 id 를 말한다 — 「왜」·예약 설명을 새 판으로 고쳐라: ' + mentions.join(' '));
console.log('\n다음: python3 tools/install_img.py ' + S.uid + ' <2배 png>(안 했으면) → node build.js && node test/all.js');
