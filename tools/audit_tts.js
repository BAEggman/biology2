#!/usr/bin/env node
/* audit_tts.js — 낭독 입력(ttsNorm) 감사(보기 화면 명세 §2.4)
   --sum            안 풀린 것의 수(로마자 · 그리스 · 첨자 · 과 번호가 남은 구간 · 사전에 없는 소문자 낱말)
   --tokens         낱말마다 빈도 · 지금 읽기 · 잡은 규칙(lex/default)
   --roman          로마 숫자가 나온 자리마다 앞뒤 12자와 읽기
   --preview <과>   정거장마다 낭독 입력을 그대로(눈으로 읽어 본다) */
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
const { ttsNorm, classify, FIXED } = require('./tts_norm');
const lex = JSON.parse(fs.readFileSync(path.join(__dirname, 'tts_lexicon.json'), 'utf8'));
const order = require('./tts_order')();
const lessons = fs.readdirSync(path.join(ROOT, 'lessons')).filter(f => /^L\d{2}[a-z]?\.json$/.test(f)).sort().map(f => JSON.parse(fs.readFileSync(path.join(ROOT, 'lessons', f), 'utf8')));
const arg = process.argv[2] || '--sum';
if (arg === '--preview') {
  const L = lessons.find(x => x.id === process.argv[3]); if (!L) { console.error('과를 주세요: --preview L17e'); process.exit(1); }
  for (const s of L.stops) console.log(`── ${s.sid}\n${ttsNorm(s.say, lex, order, L.id)}\n`);
} else if (arg === '--tokens') {
  const C = {};
  for (const L of lessons) for (const s of L.stops) {
    let t = s.say; for (const [a, b] of [...(lex.fixed || []), ...FIXED]) t = t.split(a).join(b);
    for (const m of t.matchAll(/[A-Za-zα-ωΑ-ΩΨΔ0-9₀-₉][A-Za-zα-ωΑ-ΩΨΔ0-9₀-₉\-]*/g)) if (/[A-Za-zα-ω]/.test(m[0])) { const k = m[0]; C[k] = C[k] || { n: 0, L: L.id }; C[k].n++; }
  }
  for (const [k, v] of Object.entries(C).sort((a, b) => b[1].n - a[1].n)) console.log(`${String(v.n).padStart(4)}  ${k}  →  ${ttsNorm(k, lex, order, v.L)}  [${classify(k, lex)}]`);
} else if (arg === '--roman') {
  for (const L of lessons) for (const s of L.stops) for (const m of s.say.matchAll(/(?<![A-Za-z0-9])(VII|VI|IV|V|III|II|I)(b|x)?(?![A-Za-z0-9])/g))
    console.log(`${L.id} ${s.sid}  …${s.say.slice(Math.max(0, m.index - 12), m.index)}[${m[0]}]${s.say.slice(m.index + m[0].length, m.index + m[0].length + 12)}…  →  ${ttsNorm(s.say.slice(Math.max(0, m.index - 12), m.index + m[0].length + 12), lex, order, L.id)}`);
} else {
  let left = 0, low = new Set(), n = 0;
  for (const L of lessons) for (const s of L.stops) {
    n++; if (/[A-Za-zα-ωΑ-ΩΨΔ₀-₉]|L\d{2}/.test(ttsNorm(s.say, lex, order, L.id))) left++;
    let t = s.say; for (const [a, b] of [...(lex.fixed || []), ...FIXED]) t = t.split(a).join(b);
    for (const m of t.matchAll(/[A-Za-z][A-Za-z0-9\-]*/g)) if (/[a-z]{3,}/.test(m[0]) && classify(m[0], lex) !== 'lex') low.add(m[0]);
  }
  console.log(`정거장 ${n} · 남은 로마자 등 ${left} 구간 · 사전에 없는 소문자 낱말 ${low.size}${low.size ? ' — ' + [...low].join(' · ') : ''}`);
}
