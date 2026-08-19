#!/usr/bin/env node
/* phonetics 전수조사 — Sketchy 원칙 1 「이름은 소리로 붙잡는다」.
 *
 * ★ 무엇을 위반으로 보는가
 *   사실 칸에 **임의 라벨**(로마자 약어 · 인명 · 그리스문자 · 외래 고유명사)이 있는데
 *   소품 칸이 그 이름을 **소리로도 형태로도 안 나르면** 위반이다.
 *   그런 행은 그림을 외운 뒤 이름을 따로 외워야 해서 Sketchy가 아니다.
 *
 * ★ 무엇을 위반으로 보지 않는가
 *   ① 학생이 이미 낱말처럼 아는 것(DNA·RNA·ATP…) — 후크 없이도 인출된다
 *   ② 라벨이 아니라 표·칸 번호인 것
 *   ③ 소품이 이미 이름을 나르는 것(음차가 소품에 들어 있다)
 */
const fs = require('fs');
const s = fs.readFileSync(__dirname + '/../sketchy.html', 'utf8');
const i = s.indexOf('[', s.indexOf('const DATA'));
let d = 0, q = null, e = false, end = 0;
for (let k = i; k < s.length; k++) {
  const c = s[k];
  if (q) { if (e) { e = false; continue } if (c === '\\') { e = true; continue } if (c === q) q = null; continue }
  if (c === '"' || c === "'" || c === '`') { q = c; continue }
  if (c === '[') d++; else if (c === ']') { d--; if (!d) { end = k + 1; break } }
}
const DATA = eval('(' + s.slice(i, end) + ')');
const strip = x => String(x == null ? '' : x).replace(/<[^>]+>/g, '');

/* ① 낱말처럼 굳은 것 — 후크 없이도 인출된다 */
const KNOWN = new Set(`
Na K Ca Cl Mg Fe Cu Zn Mn Mo Co Ni Se H2O CO2 O2 N2 H2 NH3 NH4 NO2 NO3 HCO3 OH PO4 SO4 CaCO3 NaCl KCl HCl NaOH CH4 C6H12O6
Type Group Phase Cis Trans Ori Pol Km Vmax pI pKa Da kDa nm um mm cm mL uL mol mM uM nM
BM Ig IgG IgM IgA IgE IgD Th Tc Treg NK B T
DNA RNA mRNA tRNA rRNA ATP ADP AMP NAD NADH NADP NADPH FAD FADH GTP GDP
RNAi cDNA snRNA miRNA siRNA hnRNA PCR ATPase pH ABO Rh X Y Z W A B C D E F G H I S M N O P T U V
XX XY XO ZZ ZW II III IV VI VII VIII IX XI XII`.split(/\s+/));

/* 로마자 라벨: 대문자 하나 이상 · 두 글자 이상 · 숫자/붙임표 허용 */
const ROMAN = /\b[A-Za-z][A-Za-z0-9]*(?:\d)?\b/g;
const GREEK = /[αβγδεζηθικλμνξοπρστυφχψωΑΒΓΔΕΘΛΠΣΦΨΩ]/g;

/* ③ 인명·지명 유래 — 한국어 표기로 굳은 것들. 이름 자체가 뜻을 안 가르쳐 준다 */
const EPONYM = `멘델 모건 왓슨 크릭 골지체 하버스 랑비에 파치니 마이스너 메르켈 루피니
슈반 헨레 보먼 말피기 크렙스 캘빈 미카엘리스 멘텐 라마르크 하디 바인베르크
바이스만 서턴 플레밍 슐라이덴 피르호 파스퇴르 오파린
그람양성 그람음성 그람염색 코흐 제너 에이버리 허시 체이스 그리피스 샤가프 프랭클린 메셀슨
니런버그 자코브 모노 테민 볼티모어 생어 멀리스 서던블롯 노던블롯 웨스턴블롯 엘리사
퍼킨지 방실결절 동방결절 베르니케 브로카
데이비슨 다니엘리 싱어 니컬슨 미첼 잉엔하우스 프리스틀리
바르소체 클라인펠터 터너증후군 다운증후군 에드워드증후군 파타우 헌팅턴 테이삭스 뒤센 마르판
맬서스 월리스 린네 라이엘 퀴비에 헤켈 폰베어
니슬 카할 셰링턴 로위 에클스 호지킨 헉슬리
로렌츠 틴베르헌 폰프리슈 해밀턴 매클린톡
베르그만 글로거 홀데인 피셔 도브잔스키 마이어 우즈 마굴리스 기무라`.split(/\s+/).filter(Boolean);
const EPO = [...new Set(EPONYM)];

/* 소품이 이름을 나르는가 — 보수적 판정
 *   ⓐ 소품에 그 로마자가 그대로 있다
 *   ⓑ 소품에 그 라벨의 한글 음차 후보가 들어 있다
 *   ⓒ 인명이면 소품에 그 인명 두 글자가 들어 있다
 */
const SYL = {A:'에이',B:'비',C:'씨',D:'디',E:'이',F:'에프',G:'지',H:'에이치',I:'아이',J:'제이',
             K:'케이',L:'엘',M:'엠',N:'엔',O:'오',P:'피',Q:'큐',R:'알',S:'에스',T:'티',U:'유',
             V:'브이',W:'더블유',X:'엑스',Y:'와이',Z:'제트'};
function carries(prop, name) {
  const P = prop.toLowerCase();
  if (P.includes(name.toLowerCase())) return true;
  // 통음 음차: ENaC→이낙/에낙, ROMK→롬크, CFTR→씨에프티알 …
  const kor = [...name.toUpperCase()].map(ch => SYL[ch] || '').join('');
  if (kor && prop.includes(kor)) return true;
  for (let a = 0; a + 1 < kor.length; a++)
    if (kor.length >= 4 && prop.includes(kor.slice(a, a + 3))) return true;
  return false;
}

const rows = [];
for (const sc of DATA) for (const p of (sc.panels || [])) for (const r of (p.f || [])) {
  const prop = strip(r[0]), fact = strip(r[1]), cards = (r[2] || []);
  const names = new Set();
  for (const m of (fact.match(ROMAN) || [])) {
    if (m.length < 2) continue;
    if (!/[A-Z]/.test(m)) continue;
    if (KNOWN.has(m)) continue;
    if (/^[IVX]+$/.test(m)) continue;                 // 로마숫자
    names.add(m);
  }
  for (const m of (fact.match(GREEK) || [])) names.add(m);
  for (const n of EPO) if (fact.includes(n)) names.add(n);
  if (!names.size) continue;
  const bad = [...names].filter(n => !carries(prop, n));
  rows.push({gate: sc.gate, scene: sc.id, panel: p.id, prop, fact,
             nc: cards.length, names: [...names], bad});
}

const viol = rows.filter(r => r.bad.length);
const byPanel = {};
for (const r of viol) {
  const v = byPanel[r.panel] = byPanel[r.panel] || {gate: r.gate, rows: [], cards: 0};
  v.rows.push(r); v.cards += r.nc;
}
const ent = Object.entries(byPanel).sort((a, b) => b[1].cards - a[1].cards);

const arg = process.argv[2];
if (arg === '--sum') {
  console.log(`임의 라벨을 담은 행 ${rows.length}`);
  console.log(`그중 소품이 이름을 안 나르는 행 ${viol.length}  ·  패널 ${ent.length}개  ·  카드 ${ent.reduce((a,[,v])=>a+v.cards,0)}장`);
  // 라벨별 빈도
  const cnt = {};
  for (const r of viol) for (const n of r.bad) cnt[n] = (cnt[n] || 0) + 1;
  const top = Object.entries(cnt).sort((a, b) => b[1] - a[1]).slice(0, 40);
  console.log('\n가장 자주 나오는 임의 라벨 40:');
  console.log(top.map(([n, c]) => `${n}(${c})`).join(' · '));
  console.log('\n패널 순위 (카드 수):');
  for (const [pid, v] of ent.slice(0, 40))
    console.log(`  ${pid.padEnd(8)} [${(v.gate||'').padEnd(4)}] ${String(v.rows.length).padStart(2)}행 ${String(v.cards).padStart(3)}장`);
} else if (arg) {
  for (const r of viol.filter(x => x.panel.startsWith(arg) || x.gate === arg)) {
    console.log(`\n${r.panel}  [${r.gate}]  ${r.nc}장   라벨: ${r.bad.join(' · ')}`);
    console.log(`  소품: ${r.prop}`);
    console.log(`  사실: ${r.fact.slice(0, 160)}`);
  }
} else {
  for (const [pid, v] of ent) {
    console.log(`\n${pid}  [${v.gate}]  ${v.rows.length}행 · ${v.cards}장`);
    for (const r of v.rows)
      console.log(`   ${String(r.nc).padStart(2)}장  ${r.bad.join('·').padEnd(18)}  ${r.prop.slice(0, 56)}`);
  }
}

/* --labels : 라벨별 집계 — 후크 사전을 짓는 입력 */
if (process.argv[2] === '--labels') {
  const L = {};
  for (const r of viol) for (const n of r.bad) {
    const v = L[n] = L[n] || {rows: 0, cards: 0, panels: new Set()};
    v.rows++; v.cards += r.nc; v.panels.add(r.panel);
  }
  const out = Object.entries(L).sort((a, b) =>
    (b[1].cards - a[1].cards) || (b[1].rows - a[1].rows));
  console.log('고유 임의 라벨 ' + out.length + '개');
  for (const [n, v] of out)
    console.log(`${n.padEnd(12)} ${String(v.cards).padStart(3)}장 ${String(v.rows).padStart(2)}행  ${[...v.panels].join(' ')}`);
}
