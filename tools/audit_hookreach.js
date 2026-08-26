#!/usr/bin/env node
/* ★ 후크 → 카드 도달 훑기 (2026-08-26 신설)
 *
 * 기존 감사 둘은 **판에서 출발한다** — 「이 행에 이름이 있는데 소품이 안 나른다」.
 * 그런데 반대 방향에 눈먼 자리가 있었다:
 *
 *   ① **후크는 세웠는데 그 이름을 묻는 카드가 그 판에 안 걸린 것** — 후크가 아무에게도 안 닿는다
 *   ② **카드는 그 이름을 묻는데 후크가 있는 판이 아닌 딴 판에 걸린 것** — 학생이 후크를 못 본다
 *
 * 이 도구는 hooks.json 의 후크마다 「그 후크를 보게 되는 카드」를 세고,
 * 덱 전체에서 그 이름을 묻는 카드와 견주어 **닿은 것과 못 닿은 것**을 가른다.
 *
 * ⚠ 「못 닿음」이 다 잘못은 아니다 — 그 카드가 딴 판에 걸릴 정당한 까닭이 있을 수 있다.
 *    그래서 이 도구는 **막지 않고 보여만 준다**. 판단은 사람이 한다.
 */
const fs = require('fs'), path = require('path');
const R = f => fs.readFileSync(path.join(__dirname, '..', f), 'utf8');

const s = R('sketchy.html');
const i0 = s.indexOf('[', s.indexOf('const DATA'));
let d = 0, q = null, e = false, end = 0;
for (let k = i0; k < s.length; k++) {
  const c = s[k];
  if (q) { if (e) { e = false; continue } if (c === '\\') { e = true; continue } if (c === q) q = null; continue }
  if (c === '"' || c === "'" || c === '`') { q = c; continue }
  if (c === '[') d++; else if (c === ']') { d--; if (!d) { end = k + 1; break } }
}
const DATA = eval('(' + s.slice(i0, end) + ')');
const strip = x => String(x == null ? '' : x).replace(/<[^>]+>/g, '');

const idx = R('index.html');
const CARDS = {};
for (const c of JSON.parse(idx.match(/id=["']CARDS["'][^>]*>([\s\S]*?)<\/script>/)[1])) if (c && c.id) CARDS[c.id] = c;

const H = JSON.parse(R('tools/hooks.json'));
const HOOKS = H.hooks || {};
const ALIAS = {};   // 표기 별칭: 다른 표기 → 정식 이름
for (const [k, v] of Object.entries((H['_표기별칭'] || {})['목록'] || {})) ALIAS[k] = v['이름'];

/* ★ 덱이 「후크가 필요 없다」고 이미 판정한 이름들 — 두 감사와 **같은 목록**을 읽는다.
   이것을 안 걸면 Na·K·Ca·Cl 처럼 KNOWN 인 것까지 「후크를 못 봤다」로 세어 숫자가 거짓이 된다.
   ⚠ 후크가 있는데 KNOWN 인 이름이 있다 — 그것은 잘못이 아니다. 후크는 **덤**이지 의무가 아니다.
      의무는 audit_phonetics.js·audit_answers.js 가 잡는 자리에만 있다. */
const pj = R('tools/audit_phonetics.js');
const KNOWN = new Set(pj.match(/const KNOWN = new Set\(`([\s\S]*?)`/)[1].split(/\s+/).filter(Boolean));
const L = k => new Set(Object.keys((H[k] || {})['목록'] || {}));
const EXEMPT = new Set([...KNOWN, ...L('_뜻이있는약어'), ...L('_외래어면제'), ...L('_음차오탐'),
                        ...L('_답면제'), ...L('_인명면제'), ...(H['_인명오탐'] || [])]);

/* ── 판별 소품 · 판별 카드 · 카드별 판 ── */
const PROPS = {}, PCARDS = {}, CARDPANELS = {};
const dangling = [];
for (const sc of DATA) for (const p of (sc.panels || [])) {
  const svgT = p.svg ? [...String(p.svg).matchAll(/<text\b[^>]*>([\s\S]*?)<\/text>/g)].map(m => strip(m[1])).join(' ') : '';
  PROPS[p.id] = (p.f || []).map(r => strip(r[0])).join(' | ') + ' | ' + svgT;
  PCARDS[p.id] = new Set();
  for (const r of (p.f || [])) for (const cid of (r[2] || [])) {
    const base = String(cid).split('#')[0];
    if (!CARDS[base]) dangling.push(p.id + ' → ' + cid);
    PCARDS[p.id].add(base);
    (CARDPANELS[base] = CARDPANELS[base] || new Set()).add(p.id);
  }
  for (const cid of (p.pc || [])) {
    const base = String(cid).split('#')[0];
    if (!CARDS[base]) dangling.push(p.id + ' →(pc) ' + cid);
    PCARDS[p.id].add(base);
    (CARDPANELS[base] = CARDPANELS[base] || new Set()).add(p.id);
  }
}

/* 어떤 이름이 카드에 나오나 — 별칭도 같은 이름으로 친다.
   ⚠ 로마자는 **낱말 경계**로 봐야 한다. 그냥 includes 로 보면 CD 가 CD4·CD8·CD34 를 다 먹고,
   K·AT·AM·Na 같은 것이 아무 글에나 걸려 숫자가 통째로 거짓이 된다 (v1 이 그랬다). */
const spellings = name => [name, ...Object.keys(ALIAS).filter(a => ALIAS[a] === name)];
const esc = x => x.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
const RX = {};
function rx(sp) {
  if (RX[sp]) return RX[sp];
  const roman = /[A-Za-z]/.test(sp);
  const hangul = /^[가-힣]+$/.test(sp);
  /* 로마자: 앞뒤에 영숫자가 붙으면 안 된다 (CD 가 CD4 를 먹지 않게).
     한글: **뒤에 한글이 이어지면 딴 낱말이다** — 「캡」이 「캡시드」를, 「요소」가 「물관요소」를 먹었다.
       뒤는 조사·기호·끝만 허용하고, 앞도 한글이 아니어야 한다.
     그리스 문자 등은 그대로 본다. ⚠ β-산화·α-케토글루타르산 같은 **화학 이름의 접두어**는
       여기서 안 걸러진다 — 손으로 가려야 한다. outputs/후크도달_판정_2026-08-26.md 참고. */
  /* ⚠ 한글은 **뒤를 통째로 막으면 안 된다** — 조사가 한글이라 「옥신이」·「옥신은」이 통째로 빠진다.
     그래서 뒤에 올 수 있는 것을 **조사·어미의 첫 글자**로 열어 둔다.
     이러면 「캡시드」(캡+시)·「대포자낭」(대포자+낭)·「소포자엽」은 걸러지고 「옥신이」는 남는다. */
  const JOSA = '이가은는을를과와의에도만로으부터까지나며랑라서보';
  const pat = roman  ? '(?<![A-Za-z0-9])' + esc(sp) + '(?![A-Za-z0-9])'
            : hangul ? '(?<![가-힣])' + esc(sp) + '(?![가-힣]|$)|(?<![가-힣])' + esc(sp) + '(?=[' + JOSA + ']|$)'
            : esc(sp);
  return RX[sp] = new RegExp(pat);
}
/* ★ 「그 카드가 그 이름을 인출로 요구하는가」 — 덱이 이미 쓰는 잣대 그대로다.
   ① 이름이 **답**에 있어야 한다 (사실 칸이나 발문에만 있는 것은 인출 대상이 아니다)
   ② **발문이 이름을 주면** 요구가 아니다 (X-BT-16 「파보바이러스(B19)는…」)
   이 둘을 안 걸면 숫자가 거짓이 된다 — 「GPCR 경로에서…」처럼 발문이 이름을 주는 카드까지
   「후크를 못 봤다」로 세게 된다. */
const asks = (c, name) => {
  const qq = strip(c.q), aa = strip(c.a);
  return spellings(name).some(sp => rx(sp).test(aa) && !rx(sp).test(qq));
};

/* ★ 「못 닿음」을 둘로 가른다 — 이 갈래가 없으면 숫자를 잘못 읽는다.
   `carries` 는 세 길로 통과한다: ① 후크 소품 ② **소품 칸이 이름을 글자로 적었다** ③ 음차.
   이 도구는 ①만 세므로, ②로 통과하는 카드가 「못 닿음」에 섞인다.
   그런데 ②는 잘못이 아니다 — 그 판은 <b>이름을 그대로 보여 주고</b> 있으므로 따로 외울 것이 없다.
   그래서 못 닿은 것을 「판이 글자로 준다」와 「아무 데도 없다(진짜 눈먼 자리)」로 가른다. */
const SYL = {A:'에이',B:'비',C:'씨',D:'디',E:'이',F:'에프',G:'지',H:'에이치',I:'아이',J:'제이',
             K:'케이',L:'엘',M:'엠',N:'엔',O:'오',P:'피',Q:'큐',R:'알',S:'에스',T:'티',U:'유',
             V:'브이',W:'더블유',X:'엑스',Y:'와이',Z:'제트'};
function namedBy(prop, name) {
  if (prop.toLowerCase().includes(name.toLowerCase())) return true;
  const kor = [...name.toUpperCase()].map(ch => SYL[ch] || '').join('');
  if (kor && prop.includes(kor)) return true;
  if (kor.length >= 4) for (let a = 0; a + 2 < kor.length; a++) if (prop.includes(kor.slice(a, a + 3))) return true;
  return false;
}
const evOf = cid => [...(CARDPANELS[cid] || [])].map(p => PROPS[p] || '').join(' ');

const rows = [], bonus = [];
for (const [name, hk] of Object.entries(HOOKS)) {
  if (EXEMPT.has(name)) { bonus.push(name); continue; }   /* 덱이 이미 「필요 없다」고 한 이름 */
  const props = hk.props || [];
  const panels = Object.keys(PROPS).filter(pid => props.some(w => PROPS[pid].includes(w)));
  const seen = new Set(panels.flatMap(pid => [...PCARDS[pid]]));
  const reached = [...seen].filter(cid => asks(CARDS[cid], name));
  const all = Object.keys(CARDS).filter(cid => asks(CARDS[cid], name));
  /* 걸린 데가 아예 없는 카드는 **후크 문제가 아니라 연결 문제**다 — 따로 센다. */
  const unlinked = all.filter(cid => !CARDPANELS[cid]);
  const missedAll = all.filter(cid => CARDPANELS[cid] && !seen.has(cid));
  const missed = missedAll.filter(cid => !spellings(name).some(sp => namedBy(evOf(cid), sp)));
  const named  = missedAll.filter(cid =>  spellings(name).some(sp => namedBy(evOf(cid), sp)));
  rows.push({ name, panels, nSeen: seen.size, reached, all: all.length, missed, named, unlinked });
}

const noPanel  = rows.filter(r => !r.panels.length);
const noCard   = rows.filter(r => r.panels.length && !r.all);
const noLinked = rows.filter(r => r.panels.length && r.all && r.all === r.unlinked.length);
const linkedAll = r => r.all - r.unlinked.length;   /* 어딘가에 걸려 있는, 그 이름을 묻는 카드 */
const reach0   = rows.filter(r => r.panels.length && linkedAll(r) > 0 && !r.reached.length);
const partial  = rows.filter(r => r.reached.length && r.missed.length);
const full     = rows.filter(r => r.reached.length && !r.missed.length);

if (process.argv.includes('--sum')) {
  console.log(`후크 ${rows.length}건 — 닿음 ${full.length + partial.length} · 아주 못 닿음 ${reach0.length} · 소품 없음 ${noPanel.length} · 묻는 카드 없음 ${noCard.length + noLinked.length} · 헛참조 ${dangling.length}`);
  process.exit(0);
}

console.log(`\n★ 후크 ${Object.keys(HOOKS).length}건 중 **의무가 있는** ${rows.length}건을 본다 · 카드 ${Object.keys(CARDS).length}장`);
console.log(`  (나머지 ${bonus.length}건은 KNOWN·면제 목록에 있는 이름이다 — 후크가 덤으로 붙어 있을 뿐 의무가 없다)\n`);
console.log(`  ✅ 온전히 닿음        ${String(full.length).padStart(3)}건  — 그 이름을 묻는 카드가 전부 후크 있는 판에 걸렸다`);
console.log(`  ◐ 일부만 닿음        ${String(partial.length).padStart(3)}건  — 닿은 카드도 있고 딴 판에만 걸린 카드도 있다`);
console.log(`  ⛔ 아주 못 닿음      ${String(reach0.length).padStart(3)}건  — 묻는 카드는 있는데 후크 있는 판에 하나도 안 걸렸다`);
console.log(`  ○ 묻는 카드가 없음   ${String(noCard.length).padStart(3)}건  — 후크는 그려져 있으나 인출을 요구하는 카드가 덱에 없다`);
console.log(`  ○ 묻는 카드가 다 미연결 ${String(noLinked.length).padStart(3)}건  — 카드는 있으나 어느 판에도 안 걸렸다 (연결 문제)`);
console.log(`  ✗ 소품이 아무 판에도 없음 ${String(noPanel.length).padStart(3)}건`);
console.log(`  ✗ 헛참조(없는 카드 ID) ${String(dangling.length).padStart(3)}건`);
const namedN = rows.reduce((a, r) => a + r.named.length, 0);
const blindN = rows.reduce((a, r) => a + r.missed.length, 0);
console.log(`\n  · 후크 아닌 판에 걸렸으나 **그 판이 이름을 글자로 적어 준다** ${namedN}장 — 따로 외울 것이 없다`);
console.log(`  · 어느 판도 그 이름을 안 나른다 (진짜 눈먼 자리)          ${blindN}장`);

const show = (t, list, f) => { if (!list.length) return;
  console.log('\n── ' + t + ' ──');
  for (const r of list.slice(0, 60)) console.log('  ' + f(r)); };

show('⛔ 아주 못 닿음', reach0, r =>
  `${r.name.padEnd(12)} 판[${r.panels.join(' ')}]  묻는 카드 ${r.all}장이 전부 딴 판: ${r.missed.slice(0,6).join(' ')}`);
show('◐ 일부만 닿음 (그 이름을 묻는데 딴 판에만 걸린 카드가 있다)',
  partial.filter(r=>r.missed.length).sort((a,b)=>b.missed.length-a.missed.length), r =>
  `${r.name.padEnd(12)} 닿음 ${String(r.reached.length).padStart(2)} / 걸린 것 중 묻는 카드 ${String(linkedAll(r)).padStart(2)}  못 닿은 것: ${r.missed.slice(0,8).join(' ')}`);
{ const blind=[];
  for (const r of rows) for (const cid of r.missed)
    blind.push(`${r.name.padEnd(10)} ${cid.padEnd(10)} 걸린 판[${[...(CARDPANELS[cid]||[])].join(' ')}]`);
  show('★ 진짜 눈먼 자리 — 어느 판도 그 이름을 안 나른다', blind.map(x=>({name:x})), r=>r.name); }
show('✗ 소품이 아무 판에도 없음', noPanel, r => `${r.name}  props=[${(HOOKS[r.name].props||[]).join(' · ')}]`);
show('✗ 헛참조', dangling.map(x=>({name:x})), r => r.name);
if (process.argv.includes('--nocard'))
  show('○ 묻는 카드가 없음', noCard, r => `${r.name.padEnd(12)} 판[${r.panels.slice(0,4).join(' ')}]`);
console.log('');
