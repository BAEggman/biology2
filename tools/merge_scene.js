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
 *   "from": ["s32p01","s32p02","s32p03"], // 합칠 낱장(순서대로) — 장면의 panels 전부, 또는 일부(2026-10-22: 일부 통합 지원 — 나머지 판은 그 자리에 그대로 두고 통합판은 첫 낱장 자리에 들어간다)
 *   "br": "...", "bx": "<p>...</p>",      // 통합판 다리 · 본문(옛 bx 를 옮겨 쓰려면 bx_from: true → 옛 bx 를 순서대로 이어 붙인다)
 *   "frame": ["소품", "사실"],             // 틀 행 — 첫 행
 *   "frame_from": ["s32p01#0","s32p02#6"], // (선택) 틀 행에 흡수하는 옛 행 — 그 카드가 틀 행에 걸린다(무대 행 · 판을 넘는 ★ 행)
 *   "rows": [                             // 그 뒤 행들 — 옛 행에서 카드를 가져온다
 *     {"from": "s32p01#1", "prop": "새 소품 글", "fact": null},   // fact null = 옛 사실 그대로 · 문자열 = 바꿈
 *     {"from": ["s32p01#0","s32p02#6"], "prop": "...", "fact": "..."},  // 둘을 한 행으로(카드 합침)
 *     {"from": null, "prop": "...", "fact": "...", "cards": []}         // 새 행(카드 없음)
 *   ],
 *   "why": "baseline.panelMerge 에 적을 까닭",
 *   "text_fixes": [["옛 글", "새 글"]],    // sketchy.html 전체에서 꼭 1번씩 맞아야 하는 치환(다른 판의 교차 참조 등)
 *   "take_rows": {                        // (2026-10-22) 판은 남기고 행만 가져오기 — 그 판의 지정 행을 뽑아 통합판 rows 의 from 으로 쓴다
 *     "s20p03": {"rows": [4,5], "title": "양면 스위치", "br": "...", "bx_cut": ["<p>…단락 머리", …]}   // title/br 은 바꿀 때만 · bx_cut 은 그 판 bx 에서 통째로 지울 단락(정확히 1번 맞아야 하고 통합판 bx 뒤에 붙는다)
 *   }
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
const allIds = sc.panels.map(p => p.id);
const ids = S.from.slice();
ids.forEach(id => { if (!allIds.includes(id)) die('from 에 장면에 없는 판: ' + id); });
const TAKE = S.take_rows || {};   /* 2026-10-22 판은 남기고 행만 */
Object.keys(TAKE).forEach(id => { if (!allIds.includes(id)) die('take_rows 에 장면에 없는 판: ' + id); if (ids.includes(id)) die('take_rows 와 from 에 같이 있다: ' + id); });
const PARTIAL = ids.length !== allIds.length;   /* 2026-10-22 일부 통합 */
const merged = sc.panels.filter(p => ids.includes(p.id));
if (PARTIAL) console.log(`일부 통합: ${sc.id} 의 ${allIds.length}판 가운데 ${ids.join('·')} → ${S.uid} (나머지 ${allIds.length - ids.length}판은 그대로)`);
const strip = x => String(x == null ? '' : x).replace(/<[^>]+>/g, '');

/* ── ① 행 대조 ── */
const used = new Set(); const map = {};
const parseRef = ref => { const m = /^(s\d+p\d+[a-z]?)#(\d+)$/.exec(ref); if (!m || !old[m[1]] || !old[m[1]].f[+m[2]]) die('없는 옛 행 ' + ref); return [m[1], +m[2]]; };
const newRows = [];
if (!S.frame || S.frame.length !== 2) die('frame 은 [소품, 사실]');
{ const fc = []; (S.frame_from || []).forEach(ref => { const [pid, k] = parseRef(ref); if (used.has(ref)) die('옛 행을 두 번 썼다 ' + ref); used.add(ref); map[ref] = S.uid + '#0'; fc.push(...(old[pid].f[k][2] || [])); });
  const u = [...new Set(fc)]; newRows.push(u.length ? [S.frame[0], S.frame[1], u] : [S.frame[0], S.frame[1]]); }
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
for (const p of merged) p.f.forEach((row, k) => { const ref = p.id + '#' + k; if (!used.has(ref)) missing.push(ref + (row[2] && row[2].length ? ' [카드 ' + row[2].length + ']' : '')); });
/* take_rows: 지정 행이 전부 쓰였는지 · 지정 안 한 행이 쓰이지 않았는지 */
for (const [id, t] of Object.entries(TAKE)) { const want = new Set((t.rows || []).map(String));
  old[id].f.forEach((row, k) => { const ref = id + '#' + k; if (want.has(String(k)) && !used.has(ref)) missing.push(ref + ' [take_rows 인데 안 씀]'); if (!want.has(String(k)) && used.has(ref)) die('take_rows 에 없는 행을 썼다 ' + ref); }); }
const takenRows = Object.entries(TAKE).flatMap(([id, t]) => (t.rows || []).map(k => old[id].f[k]));
const oldCards = merged.flatMap(p => p.f.flatMap(r => r[2] || [])).concat(takenRows.flatMap(r => r[2] || []));
const newCards = newRows.flatMap(r => r[2] || []);
const lost = oldCards.filter(c => !newCards.includes(c));
console.log(`옛 행 ${merged.reduce((a, p) => a + p.f.length, 0) + takenRows.length}${takenRows.length ? '(남는 판에서 ' + takenRows.length + '행 포함)' : ''} → 새 행 ${newRows.length}(틀 1) · 카드 ${new Set(oldCards).size} → ${new Set(newCards).size}`);
if (missing.length) console.log('  ⚠ 안 쓴 옛 행: ' + missing.join(' · ') + '  (카드가 있으면 안 된다 — 틀 행에 흡수하려면 from 에 넣어라)');
if (lost.length) die('빠진 카드 ' + lost.length + ': ' + lost.join(' '));
if (CHECK) { console.log('✅ --check 통과 (아무것도 안 썼다)'); process.exit(0); }

/* ── ② 장면 치환 ── */
const sq = s => { if (/['\\\n]/.test(s)) die('홑따옴표 문자열에 못 넣는 글자: ' + s.slice(0, 40)); return "'" + s + "'"; };
const jsRow = r => '[' + r.map(x => JSON.stringify(x)).join(',') + ']';
let bx = S.bx;
if (S.bx_from) bx = merged.map(p => p.bx || '').join('') + (S.bx || '');
const bxCuts = {};   /* take_rows 판에서 떼어 통합판 bx 뒤에 붙일 단락 */
for (const [id, t] of Object.entries(TAKE)) { const pb = old[id].bx || ''; let rest = pb; const cut = [];
  const dcut = [];
  (t.bx_cut || []).forEach(h => { const i = rest.indexOf(h); if (i < 0 || rest.indexOf(h, i + 1) >= 0) die('bx_cut 「' + h.slice(0, 30) + '」 가 ' + id + ' bx 에 정확히 1번 있지 않다');
    const isD = /^<details/.test(h); const close = isD ? '</details>' : '</p>';
    const j = rest.indexOf(close, i); if (j < 0) die('bx_cut 끝(' + close + ')을 못 찾음'); const piece = rest.slice(i, j + close.length); (isD ? dcut : cut).push(piece); rest = rest.slice(0, i) + rest.slice(j + close.length); });
  bxCuts[id] = { rest, cut: cut.concat(dcut) }; bx = (bx || '') + cut.join('');
  if (dcut.length) { /* <details> 는 통합판 bx 의 마지막 qx 상자 안에 넣고, 없으면 새 상자를 연다 */
    const qi = (bx || '').lastIndexOf("<div class='qx'>");
    if (qi >= 0) { const end = bx.lastIndexOf('</div>'); bx = bx.slice(0, end) + dcut.join('') + bx.slice(end); }
    else bx = (bx || '') + "<div class='qx'><div class='qh'>여기서 갈리는 문제</div>" + dcut.join('') + '</div>'; } }
if (/`|\$\{/.test(bx || '')) die('bx 에 ` 또는 ${ 가 있다');
const traps = sc.traps ? "\n traps:[\n  " + sc.traps.map(sq).join(',\n  ') + ']' : '';
const nums = sc.nums ? ",\n nums:[\n  " + sc.nums.map(sq).join(',\n  ') + ']' : '';
const head = `{id:'${sc.id}',t:${sq(S.scene_title || sc.t)},gate:'${sc.gate}',unit:${sq(sc.unit)},panels:[\n`;
const panel = ` {id:'${S.uid}',t:${sq(S.title)},wide:1,br:${sq(S.br)},bx:\`${bx}\`,f:[` + newRows.map(jsRow).join(',\n  ') + ']}';
const st = sk.indexOf(`{id:'${sc.id}',`); if (st < 0 || sk.indexOf(`{id:'${sc.id}',`, st + 5) >= 0) die('장면 머리를 하나로 못 찾았다');
const [ost, oend] = balanced(sk, st, '{', '}');
if (!PARTIAL) {
  const src = head + panel + ']' + (sc.traps ? ',' : '') + traps + nums + '}';
  sk = sk.slice(0, ost) + src + sk.slice(oend);
} else {
  /* 일부 통합: 장면 글은 그대로 두고 panels 배열 안에서만 — 합칠 낱장들의 원문을 지우고, 첫 낱장 자리에 통합판을 넣는다 */
  const scSrc = sk.slice(ost, oend);
  const pi = scSrc.indexOf('panels:['); if (pi < 0) die('panels 못 찾음');
  const [pst, pend] = balanced(scSrc, pi + 7, '[', ']');
  let inner = scSrc.slice(pst + 1, pend - 1);
  const spans = []; let k = 0;
  while (k < inner.length) { const o = inner.indexOf('{', k); if (o < 0) break; const [a, b] = balanced(inner, o, '{', '}'); const m = /^\{id:'([^']+)'/.exec(inner.slice(a, b)); spans.push({ id: m ? m[1] : null, a, b }); k = b; }
  const firstIdx = spans.findIndex(sp => ids.includes(sp.id)); if (firstIdx < 0) die('첫 낱장 자리를 못 찾음');
  const parts = [];
  const rewriteTake = (id, src) => { const t = TAKE[id]; const p = old[id]; const keep = p.f.filter((_, k) => !(t.rows || []).map(String).includes(String(k)));
    const pb = bxCuts[id] ? bxCuts[id].rest : (p.bx || '');
    if (/`|\$\{/.test(pb)) die('bx 에 ` 또는 ${ 가 있다: ' + id);
    const extra = Object.keys(p).filter(k => !['id', 't', 'wide', 'br', 'bx', 'f'].includes(k)); if (extra.length) die(id + ' 에 다루지 않는 칸: ' + extra.join(','));
    return ` {id:'${id}',t:${sq(t.title || p.t)},${p.wide ? 'wide:1,' : ''}br:${sq(t.br || p.br || '')},bx:\`${pb}\`,f:[` + keep.map(jsRow).join(',\n  ') + ']}'; };
  spans.forEach((sp, i) => { if (TAKE[sp.id]) parts.push(rewriteTake(sp.id, inner.slice(sp.a, sp.b))); else if (!ids.includes(sp.id)) parts.push(inner.slice(sp.a, sp.b)); else if (i === firstIdx) parts.push(panel); });
  const newInner = '\n' + parts.join(',\n') + '\n';
  const newSc = scSrc.slice(0, pst + 1) + newInner + scSrc.slice(pend - 1);
  sk = sk.slice(0, ost) + newSc + sk.slice(oend);
}
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
let retPath = path.join(R, 'tools/retired', `${sc.id}_${strip(sc.t).replace(/\s+/g, '')}_${today}.json`);
if (fs.existsSync(retPath)) retPath = retPath.replace(/\.json$/, '_' + S.uid.replace(/^s\d+/, '') + '.json');   /* 같은 날 같은 장면을 두 번 통합하면 덮어쓰지 않는다(2026-10-22 교훈) */
fs.writeFileSync(retPath,
  JSON.stringify({ _왜: `${today} 단원 통합 — ${sc.id} 「${sc.t}」 ${PARTIAL ? ids.join('·') + ' (' + allIds.length + '판 가운데 ' + ids.length + '판)' : ids.length + '판'}을 통합판 ${S.uid} 한 장으로 다시 그렸다. ` + (S.why || ''), merged_into: S.uid, merged: ids, take_rows: Object.fromEntries(Object.entries(TAKE).map(([id, t]) => [id, (t.rows || []).map(k => ({ n: k, row: old[id].f[k] }))])), 옛행_새행: map, scene: PARTIAL ? { id: sc.id, t: sc.t, unit: sc.unit, panels: merged } : sc }, null, 1));

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
for (const s2 of DATA) for (const p of s2.panels) { if (ids.includes(p.id)) continue; (p.f || []).forEach((r, k) => { if (TAKE[p.id] && (TAKE[p.id].rows || []).map(String).includes(String(k))) return; for (const c of (r[2] || [])) (cur[c] = cur[c] || new Set()).add(p.id); }); }
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
for (const [id, t] of Object.entries(TAKE)) { const e = out.find(m => m.pid === id); if (!e) continue; const p = old[id]; const keep = p.f.filter((_, k) => !(t.rows || []).map(String).includes(String(k)));
  if (t.title) e.title = t.title; e.rows = keep.map((r, i) => ({ n: i + 1, prop: strip(r[0]), fact: strip(r[1]), label: label(r[1]), cards: (r[2] || []).length })); }
fs.writeFileSync(manPath, JSON.stringify(out, null, 1));
console.log(`manifest ${man.length} → ${out.length} (label 은 사실 첫 마디 — spec.labels 로 바꿀 수 있다)`);

/* ── ⑦ hooks.json 언급 목록 ── */
const H = fs.readFileSync(path.join(R, 'tools/hooks.json'), 'utf8');
const mentions = ids.filter(id => H.includes(id)).map(id => id + '×' + (H.split(id).length - 1));
if (mentions.length) console.log('  ⚠ tools/hooks.json 이 옛 id 를 말한다 — 「왜」·예약 설명을 새 판으로 고쳐라: ' + mentions.join(' '));
console.log('\n다음: python3 tools/install_img.py ' + S.uid + ' <2배 png>(안 했으면) → node build.js && node test/all.js');
