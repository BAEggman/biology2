#!/usr/bin/env node
/* audit_lesson_names.js — 문 1 · 이름 고리 장부(2026-11-23 · 11-19 지시서 §4.1 · 상시 요청 지시서 §4).
 * 씨앗 tools/audit/2026-11-19/lesson_names.js 를 키운 것. 과의 정거장마다 걸린 카드의 「답」에 든 임의 이름(음차 외래어 · 로마자 약어)을
 * 그 과의 obj(보이는 것) 전부가 나르는지 글자로 대 본다 — 그림에 정말 보이는지는 눈 검사(독자 ㄱ · ㄴ)가 본다.
 *   실림 : hooks.json 에 고리가 있고 그 소품 말이 obj 에 있다
 *   N′   : 고리는 사전에 있는데 obj 에 그 소품 말이 없다(흘림)
 *   N    : 사전에 고리가 없다 — 옛 면제(_외래어면제 · _뜻이있는약어 · _답면제 · _인명면제)도 과에서는 인정하지 않는다(채점표 §3 · 옛면제 표시만 남김)
 *   면제 : hooks.json 「_이름고리_면제」(까닭이 있는 새 통) — 일상어 · 이름 뜻 그대로 그림(④ — 어느 과 어느 물건) · 발문이 이름을 줌(카드 id)
 * 사용: node tools/audit_lesson_names.js [--sum | --json | --by-lesson | <과 id 앞머리>]   · 모듈: require(...).compute() */
const fs = require('fs'), path = require('path');
const { ROOT, lessons, stopCards, panelIndex, strip } = require('./lesson_lib');
const H = JSON.parse(fs.readFileSync(path.join(ROOT, 'tools/hooks.json'), 'utf8'));
const HOOKS = H.hooks || {};
const list = k => Object.keys((H[k] || {})['목록'] || {});
const FREE = new Set(list('_외래어면제')), MISS = new Set(list('_음차오탐')), MEAN = new Set(list('_뜻이있는약어')), ANSF = new Set(list('_답면제')), MANF = new Set(list('_인명면제'));
const NAMEX = new Set(list('_이름장부면제'));
const NEWEX = (H['_이름고리_면제'] || {})['목록'] || {};
const BUSY = (H['_유지붐빔'] || {})['목록'] || {}; // 「과 낱말」 → {까닭 · 일감} — 6+1 심판의 판정 // 새 통 — 낱말 또는 「과|낱말」 → 까닭 // 이름 장부의 ㉮(2026-11-22 · tools/cue/names) — 일상어 · 연장 흠
const ALIAS = {}; for (const [k, v] of Object.entries((H['_표기별칭'] || {})['목록'] || {})) ALIAS[k] = v['이름'];
const ph = fs.readFileSync(path.join(ROOT, 'tools/audit_phonetics.js'), 'utf8');
const KNOWN = new Set((ph.match(/const KNOWN = new Set\(`([\s\S]*?)`/) || [, ''])[1].split(/\s+/).filter(Boolean));
const CARDS = {}; for (const c of JSON.parse(fs.readFileSync(path.join(ROOT, 'index.html'), 'utf8').match(/id=["']CARDS["'][^>]*>([\s\S]*?)<\/script>/)[1])) CARDS[c.id] = c;
const EU = new Set('프브트드크그스즈츠르므느흐쁘뜨쓰쯔플블틀들클글슬즐츨를믈늘흘'.split(''));
const STRONG = new Set('플블틀캐퍼쉬셰뷰퓨츄쥬뜨쁘랄뤼웨왁펩렌롤린틴딘'.split(''));
const TAIL = /[다서면지고며는은을어아게나자라도만까므든거져야니죠데때수것쪽뒤곳덜뿐임함됨직채중앞옆위밑끝셋넷둘록보]$/;
const DEMO = /^(그|이|저|여기|거기|우리|서로|모두|각각|다시|아주|매우|거의|바로|전자|연관)/;
const JOSA = /(으로부터|로부터|에서부터|으로|은|는|이|가|을|를|의|에|에서|로|와|과|도|만|부터|까지|보다|처럼|이라|라고|이고|고|며|면서|하고|한|하는|된|되는|들|만이|에는|에도|이나|나|성|째)$/;
function isLoan(t) { if (t.length < 3 || TAIL.test(t) || DEMO.test(t)) return false; let eu = 0, st = 0; for (const ch of t) { if (EU.has(ch)) eu++; if (STRONG.has(ch)) st++; } return st > 0 || eu >= 2 || (eu >= 1 && t.length >= 4); }
const hookOf = n => HOOKS[n] || (ALIAS[n] && HOOKS[ALIAS[n]]) || null;
const idx = panelIndex(); const rows = [];
const SUB = { '₀': '0', '₁': '1', '₂': '2', '₃': '3', '₄': '4', '₅': '5', '₆': '6', '₇': '7', '₈': '8', '₉': '9' };
const seen = new Set();
for (const L of lessons()) { const objAll = L.stops.map(s => strip(s.obj || '')).join(' ¦ '), looseAll = L.stops.map(s => strip(s.obj || '') + ' ' + strip(s.hook || '') + ' ' + strip(s.say || '')).join(' ¦ ');
 for (const s of L.stops) {
  const ids = stopCards(s, idx); if (!ids.length) continue;
  // ★ 증거는 그 과의 obj 전부 — 답이 목록인 카드는 여러 정거장에 한 조각씩 걸린다(옛 감사의 「걸린 판 전부의 합」과 같은 까닭)
  const obj = objAll, loose = looseAll;
  const terms = new Set();
  for (const id of ids) { const c = CARDS[id.replace(/#\d+$/, '')] || CARDS[id]; if (!c) continue;
    const ans = strip((c.a || '') + ' ' + (Array.isArray(c.it) ? c.it.join(' ') : ''));
    for (let t of (ans.match(/[가-힣]{2,}/g) || [])) { t = t.replace(JOSA, ''); if (isLoan(t) && !MISS.has(t) && !NAMEX.has(t)) terms.add(t); }
    for (let t of (ans.match(/[A-Za-z][A-Za-z0-9₀-₉]*[A-Za-z0-9₀-₉]/g) || [])) { t = t.replace(/[₀-₉]/g, ch => SUB[ch]); if (!KNOWN.has(t) && !/^[a-z]+$/.test(t) && !/^[A-Z][a-z]{3,}$/.test(t)) terms.add(t); }
  }
  for (const t of terms) {
    if (seen.has(L.id + '|' + t)) continue; seen.add(L.id + '|' + t);
    const hk = hookOf(t); let cls;
    if (hk && (hk.props || []).some(p => obj.includes(p))) cls = 'A0';
    else if (hk) cls = 'A1';
    else if (FREE.has(t) || MEAN.has(t) || ANSF.has(t) || MANF.has(t)) cls = 'B';
    else cls = 'C';
    const ex = NEWEX[L.id + '|' + t] || NEWEX[t] || (BUSY[L.id + ' ' + t] ? '유지 — 붐빔(6+1 심판) — ' + BUSY[L.id + ' ' + t]['까닭'] : null);
    const gate = cls === 'A0' ? '실림' : ex ? '면제' : cls === 'A1' ? 'N′' : 'N';
    rows.push({ lesson: L.id, sid: s.sid, term: t, cls, gate, old: cls === 'B', why: ex, props: hk ? hk.props : null, inLoose: hk ? (hk.props || []).some(p => loose.includes(p)) : false, nc: ids.length });
  }
 }
}
function byLesson(rs) { const m = {}; for (const L of lessons()) m[L.id] = 0; for (const r of rs) if (r.gate === 'N' || r.gate === 'N′') m[r.lesson]++; return m; }
module.exports = { compute: () => rows, byLesson };
if (require.main !== module) return;
const arg = process.argv[2];
if (arg === '--by-lesson') { console.log(JSON.stringify(byLesson(rows))); process.exit(0); }
if (arg === '--gate') { const n = k => rows.filter(r => r.gate === k).length; console.log('실림', n('실림'), '· N′', n('N′'), '· N', n('N'), '(옛 면제', rows.filter(r => r.gate === 'N' && r.old).length + ')', '· 면제', n('면제')); process.exit(0); }
if (arg === '--json') console.log(JSON.stringify(rows));
else if (arg === '--sum' || !arg) {
  const n = k => rows.filter(r => r.cls === k); const u = a => new Set(a.map(r => r.term)).size, st = a => new Set(a.map(r => r.lesson + r.sid)).size, ls = a => new Set(a.map(r => r.lesson)).size;
  for (const k of ['A0', 'A1', 'B', 'C']) console.log(k, '건', n(k).length, '· 낱말', u(n(k)), '· 정거장', st(n(k)), '· 과', ls(n(k)));
  if (!arg) for (const k of ['A1', 'C', 'B']) { const m = {}; for (const r of n(k)) (m[r.term] = m[r.term] || new Set()).add(r.lesson + ':' + r.sid); console.log('\n== ' + k); for (const [t, v] of Object.entries(m).sort((a, b) => b[1].size - a[1].size)) console.log('  ' + t.padEnd(14) + [...v].slice(0, 6).join(' ') + (v.size > 6 ? ' …' + v.size : '')); }
} else for (const r of rows.filter(r => r.lesson.startsWith(arg))) console.log(r.lesson, r.sid, r.cls, r.term, r.props ? '← ' + r.props.join(' / ') : '');
