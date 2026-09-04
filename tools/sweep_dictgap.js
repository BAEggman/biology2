#!/usr/bin/env node
/* ★ 사전에만 없는 후크 훑기 (2026-09-04 신설)
 *
 * 왜 만들었나 — **δ 가 우연히 잡혔다.**
 *   s11p04 는 2026 년 내내 「삼각 모자」로 pol δ 를 그리고 있었는데
 *   hooks.json 에 δ 항목이 없었다. 감사는 셋 다 이것을 못 잡는다:
 *     · audit_phonetics  — 그 행에 걸린 카드가 0장이면 값이 0이라 눈에 안 띈다
 *     · audit_loanwords  — 답만 본다. 그 이름이 어느 카드의 답에도 없으면 안 본다
 *     · hookwords --orphan — 사전에 있는데 안 그린 것을 찾는다. 이건 정반대다
 *   그래서 s49p01 이 δ 를 쓰려는 순간에야 「사전에 없다」가 드러났다.
 *   ★ 우연에 맡길 일이 아니다. 반대쪽을 전수로 훑는 도구를 따로 둔다.
 *
 * 무엇을 찾는가
 *   판의 **사실 칸**이 이름을 부르는데 hooks.json 의 어느 통에도 그 이름이 없는 자리.
 *   통은 여섯이다: hooks · _표기별칭 · _외래어면제 · _음차오탐 · _답면제 ·
 *   _뜻이있는약어 · _인명면제. 어디에도 없으면 「사전이 그 이름을 모른다」는 뜻이다.
 *
 * 무엇을 찾지 않는가
 *   그림이 있는지 없는지는 **판정하지 않는다.** 그것은 사람이 그림을 열어서 한다.
 *   이 도구는 「사전이 모르는 이름」의 목록을 내놓을 뿐이고,
 *   그 다음 갈래는 셋이다 — ① 후크를 준다 ② 면제/오탐에 넣는다 ③ 사실 칸에서 지운다.
 *
 * 쓰는 법
 *   node tools/sweep_dictgap.js            요약 — 이름별로 몇 판 · 몇 장
 *   node tools/sweep_dictgap.js <이름>      그 이름이 나오는 자리를 다 편다
 *   node tools/sweep_dictgap.js --cards     카드가 걸린 자리만 (급한 것부터)
 */
const fs = require('fs'), path = require('path');
const R = path.dirname(__dirname);
const strip = x => String(x == null ? '' : x).replace(/<[^>]+>/g, '');

const s = fs.readFileSync(path.join(R, 'sketchy.html'), 'utf8');
const i0 = s.indexOf('[', s.indexOf('const DATA'));
let d = 0, q = null, e = false, end = 0;
for (let k = i0; k < s.length; k++) { const c = s[k];
  if (q) { if (e) { e = false; continue } if (c === '\\') { e = true; continue } if (c === q) q = null; continue }
  if (c === '"' || c === "'" || c === '`') { q = c; continue }
  if (c === '[') d++; else if (c === ']') { d--; if (!d) { end = k + 1; break } } }
const DATA = eval('(' + s.slice(i0, end) + ')');

const H = JSON.parse(fs.readFileSync(path.join(__dirname, 'hooks.json'), 'utf8'));
const L = k => Object.keys((H[k] || {})['목록'] || H[k] || {});
/* 사전이 아는 이름 = 여섯 통의 합 */
const KNOWN_NAME = new Set([
  ...Object.keys(H.hooks || {}),
  ...L('_표기별칭'), ...L('_외래어면제'), ...L('_음차오탐'),
  ...L('_답면제'), ...L('_뜻이있는약어'), ...L('_인명면제'),
]);

/* ── 이름 뽑기 — 세 감사와 같은 잣대를 쓴다 ───────────────────────── */
const GREEK = /[αβγδεζηθικλμνξοπρστυφχψωΑΒΓΔΕΘΛΠΣΦΨΩ]/g;
const ROMAN = /\b[A-Za-z][A-Za-z0-9-]*\b/g;
const KOR = /[가-힣]{2,}/g;
const EU = new Set('프브트드크그스즈츠르므느흐쁘뜨쓰쯔플블틀들클글슬즐츨를믈늘흘'.split(''));
const STRONG = new Set('플블틀캐퍼쉬셰뷰퓨츄쥬뜨쁘랄뤼웨왁펩렌롤린틴딘'.split(''));
const TAIL = /[다서면지고며는은을어아게나자라도만까므든거져야니죠데때수것쪽뒤곳덜뿐임함됨직채중앞옆위밑끝셋넷둘록보]$/;
const DEMO = /^(그|이|저|여기|거기|우리|서로|모두|각각|다시|아주|매우|거의|바로|전자|연관)/;
const JOSA = /(으로부터|로부터|에서부터|으로|은|는|이|가|을|를|의|에|에서|로|와|과|도|만|부터|까지|보다|처럼|이라|라고|이고|고|며|면서|하고|한|하는|된|되는|들|만이|에는|에도|이나|나|성|째)$/;
function isLoan(t) {
  if (t.length < 3) return false;
  if (TAIL.test(t) || DEMO.test(t)) return false;
  let eu = 0, st = 0;
  for (const ch of t) { if (EU.has(ch)) eu++; if (STRONG.has(ch)) st++; }
  return st > 0 || eu >= 2 || (eu >= 1 && t.length >= 4);
}
/* 로마자 잡음 — audit_phonetics 의 KNOWN 과 같은 것을 쓴다(중복 유지보수를 피한다) */
const ap = fs.readFileSync(path.join(__dirname, 'audit_phonetics.js'), 'utf8');
const KNOWNROM = new Set((ap.match(/const KNOWN = new Set\(`([\s\S]*?)`\.split/) || [,''])[1].split(/\s+/).filter(Boolean));

const hit = {};                              /* 이름 → {panels:Set, rows:[], cards:n} */
const add = (n, panel, prop, fact, nc) => {
  const o = hit[n] = hit[n] || { panels: new Set(), rows: [], cards: 0 };
  o.panels.add(panel); o.rows.push({ panel, prop, fact, nc }); o.cards += nc;
};
/* ★ 판이 스스로 그 말을 하고 있으면 구멍이 아니다 — 두 경우를 한 규칙으로 막는다.
 *   ⓐ **소품 낱말** — 「캐스터네츠」·「크랭크」·「다이아몬드」처럼 그림 속 물건의 이름.
 *      그 낱말 자체를 인출할 일이 없다. 사전에 넣을 것이 아니라 세지 말아야 할 것이다.
 *   ⓑ **도해가 찍은 글자** — d 계열 SVG 는 이름을 차트 위에 글자로 쓴다(P700 · 푸르킨예 …).
 *      audit_phonetics 가 이미 같은 이유로 면제한다. 세 도구의 잣대가 갈리면 안 된다.
 *   ⚠ δ 는 이 그물을 빠져나간다 — 소품은 「삼각 모자」이고 「δ」라는 글자는 어디에도 없다.
 *      그것이 바로 이 도구가 잡아야 하는 자리다. */
const PANELSAYS = {};
for (const sc of DATA) for (const p of (sc.panels || [])) {
  const svgT = p.svg
    ? [...String(p.svg).matchAll(/<text\b[^>]*>([\s\S]*?)<\/text>/g)].map(m => strip(m[1])).join(' ')
    : '';
  PANELSAYS[p.id] = (p.f || []).map(x => strip(x[0])).join(' ') + ' ' + svgT + ' ' + strip(p.t || '');
}
/* 카드 번호가 사실 칸에 적히면 로마자로 잡힌다 — 그것은 이름이 아니다 */
const CARDID = /^[A-Z]{1,3}[0-9]?-[A-Z]{0,3}[0-9]+$/;
for (const sc of DATA) for (const p of (sc.panels || [])) for (const r of (p.f || [])) {
  const prop = strip(r[0]), fact = strip(r[1]), nc = (r[2] || []).length;
  const says = PANELSAYS[p.id] || '';
  const names = new Set();
  for (const m of (fact.match(GREEK) || [])) names.add(m);
  for (const m of (fact.match(ROMAN) || [])) {
    if (m.length < 2 || !/[A-Z]/.test(m)) continue;
    if (KNOWNROM.has(m) || /^[IVX]+$/.test(m) || CARDID.test(m)) continue;
    names.add(m);
  }
  for (let t of (fact.match(KOR) || [])) {
    t = t.replace(JOSA, '').replace(JOSA, '');   /* 조사가 겹쳐 붙는다 — 두 번 벗긴다 */
    if (isLoan(t)) names.add(t);
  }
  for (const n of names) {
    if (KNOWN_NAME.has(n)) continue;
    if (says.includes(n)) continue;              /* ★ 판이 스스로 그 말을 한다 */
    add(n, p.id, prop, fact, nc);
  }
}

const arg = process.argv[2];
const ent = Object.entries(hit).sort((a, b) => (b[1].cards - a[1].cards) || (b[1].panels.size - a[1].panels.size));
if (arg && !arg.startsWith('--')) {
  const o = hit[arg];
  if (!o) { console.log(`「${arg}」 — 사전 구멍 목록에 없다 (사전이 이미 알거나, 사실 칸에 안 나온다)`); process.exit(0) }
  console.log(`\n■ 「${arg}」 — 판 ${o.panels.size}개 · 걸린 카드 ${o.cards}장\n`);
  for (const r of o.rows) {
    console.log(`  ${r.panel}  (${r.nc}장)`);
    console.log(`    소품: ${r.prop.slice(0, 110)}`);
    console.log(`    사실: ${r.fact.slice(0, 150)}\n`);
  }
  process.exit(0);
}
const only = arg === '--cards';
const rows = ent.filter(([, o]) => !only || o.cards > 0);
console.log('\n── 사전이 모르는 이름 ── (사실 칸이 부르는데 hooks.json 여섯 통 어디에도 없다)\n');
console.log('  장   판   이름');
for (const [n, o] of rows)
  console.log(`${String(o.cards).padStart(5)} ${String(o.panels.size).padStart(4)}   ${n}   ${[...o.panels].slice(0, 4).join(' ')}`);
console.log(`\n이름 ${rows.length}종 · 카드가 걸린 것 ${ent.filter(([, o]) => o.cards > 0).length}종`);
console.log('★ 이 도구는 그림이 있는지 판정하지 않는다. 갈래는 셋 — ① 후크를 준다 ② 면제/오탐에 넣는다 ③ 사실 칸에서 지운다.');
