#!/usr/bin/env node
/* 한글 음차 외래어 전수조사 — Sketchy 원칙 1 「이름은 소리로 붙잡는다」의 **눈먼 자리**.
 *
 * 왜 만들었나 (2026-08-22, 사용자 지적)
 *   audit_phonetics.js 는 **로마자 약어와 인명만** 본다. 그래서
 *   「아포플라스트」 「심플라스트」 「익스팬신」 「수베린」 같은 **한글로 음차한 외래어**가
 *   통째로 감사 밖에 있었다. 학생이 외워야 하는 임의 이름이라는 점에서는 GPCR 과 똑같다.
 *
 * ★ 무엇을 위반으로 보는가
 *   **카드의 「답」에 든 음차 외래어**를 그 판의 소품(과 SVG 글자)이 못 나르면 위반이다.
 *
 * ★ 왜 「답」만 보는가 — 이것이 이 도구의 핵심이다
 *   질문에만 있는 말은 학생이 **이미 받은** 말이다. 「프라이머 수 차이는?」에서
 *   「프라이머」는 인출할 것이 아니라 주어진 것이다. 인출해야 하는 것은 답에 있는 말뿐이고,
 *   후크는 인출을 돕는 장치다. 답이 아닌 말에 후크를 붙이면 짐만 는다.
 *
 * ★ 증거는 **그 카드가 걸린 판 전부**의 소품 + SVG 글자다 (제목·br 은 안 친다)
 *   [고침 2026-08-25] 한 판만 보던 것을 여러 판의 합으로 바꿨다. 답이 목록인 카드
 *   (「HIV 약물 3종」·「2차 전령별 표적 넷」·「균류 5군」)가 여러 판에 한 조각씩 걸리면
 *   그 판이 안 그린 나머지 이름이 전부 미달로 잡혔는데, 실제 화면은 그렇지 않다 —
 *   showPicFix() 가 PMAP 의 판을 전부 펼쳐 그림과 사실표를 나란히 그린다.
 *   학생이 보는 것이 여러 판의 합이므로 증거도 합이어야 한다. 174 → 152장.
 *   ⚠ 한 판에만 걸린 카드(대다수)는 값이 그대로다 — 감사가 느슨해지지 않는다.
 *
 * ★ 증거는 **소품 + SVG 글자**뿐이다 (제목·br 은 안 친다)
 *   제목과 한 줄 요약은 그림 옆의 **글자**이지 그림이 아니다. 「그린 것만 건다」.
 *   ⚠ audit_phonetics.js 는 아직 제목·br 을 증거로 친다 — 둘의 기준이 다르다는 것을 알고 있다.
 */
const fs = require('fs'), path = require('path');
const R = path.dirname(__dirname);
const s = fs.readFileSync(path.join(R, 'sketchy.html'), 'utf8');
const i = s.indexOf('[', s.indexOf('const DATA'));
let d = 0, q = null, e = false, end = 0;
for (let k = i; k < s.length; k++) { const c = s[k];
  if (q) { if (e) { e = false; continue } if (c === '\\') { e = true; continue } if (c === q) q = null; continue }
  if (c === '"' || c === "'" || c === '`') { q = c; continue }
  if (c === '[') d++; else if (c === ']') { d--; if (!d) { end = k + 1; break } } }
const DATA = eval('(' + s.slice(i, end) + ')');
const CARDS = JSON.parse(fs.readFileSync(path.join(R, 'index.html'), 'utf8')
  .match(/id=["']CARDS["'][^>]*>([\s\S]*?)<\/script>/)[1]);
const A = {}; for (const c of CARDS) A[c.id] = c;
const strip = x => String(x == null ? '' : x).replace(/<[^>]+>/g, '');

const H = JSON.parse(fs.readFileSync(path.join(__dirname, 'hooks.json'), 'utf8'));
const HOOKS = H.hooks || {};
const FREE = new Set(Object.keys((H['_외래어면제'] || {})['목록'] || {}));
/* ★ 오탐은 면제와 다르다 — 면제는 「음차가 맞지만 후크가 필요 없다」이고
   오탐은 「애초에 음차가 아니다」(순 한국어·일상 낱말)다. isLoan 이 어림짐작이라 섞여 든다.
   둘을 한 통에 담으면 면제 래칫이 도구 결함까지 재게 된다. */
const MISS = new Set(Object.keys((H['_음차오탐'] || {})['목록'] || {}));
/* ★ 표기별칭 — 「후크가 이미 있는데 감사가 표기가 달라 못 알아본다」를 잇는다.
   [보탬 2026-08-31] audit_phonetics.js·audit_answers.js 는 처음부터 이 통을 읽는데
   이 도구만 안 읽고 있었다. 그래서 「부갑상선호르몬」(= PTH 의 한글 풀어쓴 표기)이
   PTH 후크가 s07p03 에 서 있는데도 미달로 잡혔다. hooks.json 의 「_표기별칭」 항목이
   ★ 세 감사가 갈리면 안 된다 ★ 고 못 박아 둔 그대로, 여기서도 읽는다.
   ⚠ 이것은 사전을 늘리는 것이 아니라 도구를 맞추는 것이다 — 별칭은 verify_hooks.js 가
   「가리키는 이름에 후크가 없으면 못 넣는다」로 이미 막고 있다. */
const ALIAS = {};
for (const [k, v] of Object.entries((H['_표기별칭'] || {})['목록'] || {})) ALIAS[k] = v['이름'];

/* ㅡ 로 끝나는 무받침 음절과 외래어 전용 음절이 음차의 표지다 */
const EU = new Set('프브트드크그스즈츠르므느흐쁘뜨쓰쯔플블틀들클글슬즐츨를믈늘흘'.split(''));
const STRONG = new Set('플블틀캐퍼쉬셰뷰퓨츄쥬뜨쁘랄뤼웨왁펩렌롤린틴딘'.split(''));
/* 잡음의 거의 전부가 용언 활용형이다 — 끝 음절로 걸러 낸다 */
const TAIL = /[다서면지고며는은을어아게나자라도만까므든거져야니죠데때수것쪽뒤곳덜뿐임함됨직채중앞옆위밑끝셋넷둘록보]$/;
const DEMO = /^(그|이|저|여기|거기|우리|서로|모두|각각|다시|아주|매우|거의|바로|전자|연관)/;
function isLoan(t) {
  if (t.length < 3) return false;
  if (TAIL.test(t) || DEMO.test(t)) return false;
  let eu = 0, st = 0;
  for (const ch of t) { if (EU.has(ch)) eu++; if (STRONG.has(ch)) st++; }
  return st > 0 || eu >= 2 || (eu >= 1 && t.length >= 4);
}
const KOR = /[가-힣]{2,}/g;
/* ⚠ 2026-09-04 — 긴 조사를 먼저 둔다. 「글리코젠으로부터」가 「부터」만 떨어져
   「글리코젠으로」로 남는 바람에 사전에도 면제에도 안 걸렸다(B0-137). 긴 것부터 시도해야 한다.
   ⚠ 「인」은 절대 넣지 마라 — 헤파린→헤파, 팔로이딘→팔로이드로 토막 난다. */
const JOSA = /(으로부터|로부터|에서부터|으로|은|는|이|가|을|를|의|에|에서|로|와|과|도|만|부터|까지|보다|처럼|이라|라고|이고|고|며|면서|하고|한|하는|된|되는|들|만이|에는|에도|이나|나|성|째)$/;

function carries(evidence, w) {
  if (evidence.includes(w)) return true;
  for (const name of [w, ALIAS[w]]) {
    if (!name) continue;
    if (name !== w && evidence.includes(name)) return true;
    const hk = HOOKS[name];
    if (hk && (hk.props || []).some(p => evidence.includes(p))) return true;
  }
  return false;
}

/* ── 판마다의 증거 ─────────────────────────────────────────────────────── */
const EV = {};
for (const sc of DATA) for (const p of (sc.panels || [])) {
  const svg = p.svg ? [...String(p.svg).matchAll(/<text\b[^>]*>([\s\S]*?)<\/text>/g)].map(m => strip(m[1])).join(' ') : '';
  EV[p.id] = (p.f || []).map(x => strip(x[0])).join(' ') + ' ' + svg;
}

/* ★ 카드가 걸린 판 전부 — 「배열 카드」의 증거는 **여러 판의 합**이다 ─────────
   [고침 2026-08-25] 지금까지는 한 판의 소품만 증거로 봤다. 그래서 답이 목록인
   카드(「HIV 약물 3종」·「2차 전령별 표적 넷」·「균류 5군」)가 여러 판에 한 조각씩
   걸리면, 그 판이 안 그린 나머지 이름이 전부 미달로 잡혔다.
   그런데 실제 화면은 그렇지 않다 — index.html 의 showPicFix() 는 PMAP 에 든
   **판을 전부 펼쳐** 그림과 사실표를 나란히 그리고, 「🖼 그림으로 보기 — 제목A + 제목B」
   로 두 제목을 이어 붙인다. 학생이 보는 것이 여러 판의 합이므로 증거도 합이어야 한다.
   ★ 한 판에만 걸린 카드(대다수)는 값이 그대로다 — 감사가 느슨해지지 않는다. */
const CARDPANELS = {};
for (const sc of DATA) for (const p of (sc.panels || []))
  for (const r of (p.f || [])) for (const id of (r[2] || []))
    (CARDPANELS[id] = CARDPANELS[id] || new Set()).add(p.id);
const cardEv = id => [...(CARDPANELS[id] || [])].map(x => EV[x] || '').join(' ');

const viol = [];
for (const sc of DATA) for (const p of (sc.panels || [])) {
  for (const r of (p.f || [])) {
    const ids = r[2] || []; if (!ids.length) continue;
    const bad = new Set();
    for (const id of ids) {
      const c = A[id]; if (!c) continue;
      const ev = cardEv(id);                   /* ★ 이 카드가 걸린 판 전부의 소품 */
      const ans = strip(c.a || '');            /* ★ 답만 본다 */
      for (let t of (ans.match(KOR) || [])) {
        t = t.replace(JOSA, '');
        if (!isLoan(t) || FREE.has(t) || MISS.has(t)) continue;
        if (carries(ev, t)) continue;
        bad.add(t);
      }
    }
    if (bad.size) viol.push({ scene: sc.id, panel: p.id, gate: sc.gate, prop: strip(r[0]), nc: ids.length, bad: [...bad] });
  }
}

const byPanel = {};
for (const v of viol) { const o = byPanel[v.panel] = byPanel[v.panel] || { gate: v.gate, rows: [], cards: 0 }; o.rows.push(v); o.cards += v.nc; }
const ent = Object.entries(byPanel).sort((a, b) => b[1].cards - a[1].cards);
const arg = process.argv[2];

if (arg === '--sum') {
  console.log(`답에 음차 외래어가 있는데 소품이 못 나르는 행 ${viol.length}  ·  패널 ${ent.length}개  ·  카드 ${ent.reduce((a, [, v]) => a + v.cards, 0)}장`);
} else if (arg === '--labels') {
  const L = {};
  for (const v of viol) for (const w of v.bad) { const o = L[w] = L[w] || { cards: 0, rows: 0, panels: new Set() }; o.cards += v.nc; o.rows++; o.panels.add(v.panel); }
  const out = Object.entries(L).sort((a, b) => (b[1].cards - a[1].cards) || (b[1].rows - a[1].rows));
  console.log('고유 음차 낱말 ' + out.length + '개');
  for (const [w, v] of out) console.log(String(v.cards).padStart(3) + '장 ' + String(v.rows).padStart(2) + '행  ' + w.padEnd(16) + ' ' + [...v.panels].join(' '));
} else if (arg) {
  for (const v of viol.filter(x => x.panel.startsWith(arg) || x.gate === arg)) {
    console.log(`\n${v.panel}  [${v.gate}]  ${v.nc}장   낱말: ${v.bad.join(' · ')}`);
    console.log(`  소품: ${v.prop.slice(0, 90)}`);
  }
} else {
  for (const [pid, v] of ent) {
    console.log(`\n${pid}  [${v.gate}]  ${v.rows.length}행 · ${v.cards}장`);
    for (const r of v.rows) console.log(`   ${String(r.nc).padStart(2)}장  ${r.bad.join('·').padEnd(20)}  ${r.prop.slice(0, 50)}`);
  }
}
