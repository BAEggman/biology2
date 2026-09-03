#!/usr/bin/env node
/* ★ 셈 훑기 (2026-09-02 신설 · _후크대기 48)
 *
 * 왜 필요한가 — **사용자가 s45p02 의 쟁반 칸을 세어 주었다.**
 *   사실 칸은 「칸이 여섯」이라 적혀 있었는데 그림은 다섯이었다.
 *   덱의 검사는 전부 **글 대 글**이다 — 후크가 있나 · 답의 이름이 소품 칸에 있나 · 사전의 말과 판의 말이 같나.
 *   **글이 센 수와 그림이 센 수가 같은가**를 보는 검사는 하나도 없었다.
 *
 * ★ 이 도구는 세지 않는다. **어디를 세야 하는지**만 알려 준다.
 *   세는 일은 사람이 그림을 열어서 한다 — 기계가 할 수 있는 것은 「여기에 수가 적혀 있다」까지다.
 *
 * 쓰는 법
 *   node tools/counts.js            수를 말하는 자리를 판별로 다 뽑는다
 *   node tools/counts.js <판 id> …  그 판만
 *   node tools/counts.js --big      다섯보다 큰 수만 (Gemini 가 가장 잘 틀리는 자리)
 *   node tools/counts.js --pic      도해(SVG 에 수가 글자로 적힌 판)를 뺀다 — 그림에서 세어야 하는 자리만
 */
const fs = require('fs'), path = require('path');
const R = f => fs.readFileSync(path.join(__dirname, '..', f), 'utf8');
const strip = x => String(x == null ? '' : x).replace(/<[^>]+>/g, '');

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

/* 수를 말하는 말 — 한글 수사와 아라비아 숫자 둘 다 */
const WORD = { '하나':1,'한':1,'둘':2,'두':2,'셋':3,'세':3,'넷':4,'네':4,'다섯':5,'여섯':6,'일곱':7,'여덟':8,'아홉':9,
               '한 마리':1,'두 마리':2 };
const NUM = new RegExp('(' + Object.keys(WORD).sort((a,b)=>b.length-a.length).join('|') + '|\\d+)\\s*(개|장|칸|줄|겹|마리|자루|짝|벌|층|칸짜리|가닥|점|구멍|바퀴|채|)', 'g');

/* 셈이 아닌 자리 — 이름·화학식·관용구 */
const SKIP = /(면 블록|면체|×|배수|하나하나|하나씩|한꺼번에|한자리|한 눈|한눈|한 화면|한 줄로 읽|둘 다|두고|세우|세워|세운|네모|넷째|셋째|둘째|첫째|열리|열어|열고|열린|열쇠|한 번|두 번|세 번|한 가지|하나로|한 마디|한 몫)/;

const args = process.argv.slice(2);
const onlyBig = args.includes('--big');
const onlyPic = args.includes('--pic');
const want = args.filter(a => !a.startsWith('--'));

let nPanel = 0, nHit = 0;
for (const sc of DATA) for (const p of (sc.panels || [])) {
  if (want.length && !want.includes(p.id)) continue;
  if (onlyPic && p.svg) continue;   // 도해는 수가 그림 속 글자로 적혀 있어 사람이 셀 일이 아니다
  const hits = [];
  (p.f || []).forEach((row, ri) => {
    const prop = strip(row[0]);
    for (const m of prop.matchAll(NUM)) {
      const raw = m[1], unit = m[2] || '';
      const n = WORD[raw] !== undefined ? WORD[raw] : parseInt(raw, 10);
      if (!n || n > 30) continue;
      if (onlyBig && n <= 5) continue;
      const win = prop.slice(Math.max(0, m.index - 10), m.index + m[0].length + 10);
      if (/[sd]\d*$/.test(prop.slice(Math.max(0,m.index-3), m.index))) continue;  // 판 번호(s12p04)의 숫자는 셈이 아니다
      if (SKIP.test(win)) continue;
      hits.push({ ri: ri + 1, n, txt: m[0].trim(), win: prop.slice(Math.max(0, m.index - 22), m.index + m[0].length + 22) });
    }
  });
  if (!hits.length) continue;
  nPanel++; nHit += hits.length;
  console.log('\n■ ' + p.id + '  「' + (p.t || '') + '」' + (p.svg ? '  [도해]' : ''));
  for (const h of hits) console.log('   ' + String(h.ri).padStart(2) + '행  ' + String(h.n).padStart(2) + ' ' + (h.txt.replace(/^\S+\s*/, '') || '개') + '   …' + h.win + '…');
}
console.log('\n수를 말하는 자리 — 판 ' + nPanel + '개 · ' + nHit + '군데' + (onlyBig ? ' (다섯 초과만)' : ''));
console.log('★ 이 도구는 세지 않는다. 그림을 열어 세는 것은 사람이 한다.');
