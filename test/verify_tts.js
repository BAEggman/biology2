/* verify_tts.js — 낭독 입력(ttsNorm(say))의 문(보기 화면 명세 §2.5 · 2026-11-21)
   1. 모든 say 를 ttsNorm 한 결과에 로마자 · 그리스 글자 · 첨자 · 과 번호가 하나도 없다
   2. 소문자 세 글자 이상이 든 낱말은 기본값(글자 이름)이 아니라 사전이 잡았다
   3. test/tts_cases.json 의 본보기 쌍이 맞는다
   4. 과 화면(lesson/*.html)에 끼워 넣은 사전 · 함수가 지금 것과 같다(빌드를 다시 돌렸나) */
const fs = require('fs'), path = require('path');
const ROOT = path.join(__dirname, '..');
const { ttsNorm, classify, FIXED } = require(path.join(ROOT, 'tools/tts_norm'));
const lex = JSON.parse(fs.readFileSync(path.join(ROOT, 'tools/tts_lexicon.json'), 'utf8'));
const order = require(path.join(ROOT, 'tools/tts_order'))();
let bad = 0; const fail = m => { console.log('  ✕ ' + m); bad++; };
let n = 0; const left = [], low = {};
for (const f of fs.readdirSync(path.join(ROOT, 'lessons')).filter(f => /^L\d{2}[a-z]?\.json$/.test(f))) {
  const L = JSON.parse(fs.readFileSync(path.join(ROOT, 'lessons', f), 'utf8'));
  for (const s of L.stops) {
    n++;
    const o = ttsNorm(s.say, lex, order, L.id);
    const m = o.match(/[A-Za-zα-ωΑ-ΩΨΔ₀-₉⁰-⁹¹²³]+|L\d{2}/g);
    if (m) left.push(`${L.id} ${s.sid}: ${m.join(',')}`);
    let t = s.say; for (const [a, b] of [...(lex.fixed || []), ...FIXED]) t = t.split(a).join(b);
    for (const k of t.matchAll(/[A-Za-z][A-Za-z0-9\-]*/g)) if (/[a-z]{3,}/.test(k[0]) && classify(k[0], lex) !== 'lex') (low[k[0]] = low[k[0]] || []).push(L.id);
  }
}
if (left.length) fail(`로마자 · 그리스 · 첨자 · 과 번호가 남음 ${left.length} 구간 — ${left.slice(0, 5).join(' | ')}`); else console.log(`  ✓ 낭독 입력에 로마자 · 그리스 · 첨자 · 과 번호 0 (정거장 ${n})`);
const lowK = Object.keys(low);
if (lowK.length) fail(`소문자 세 글자 이상 낱말이 사전에 없음 — ${lowK.map(k => k + '(' + low[k][0] + ')').join(' · ')}`); else console.log('  ✓ 소문자 세 글자 이상 낱말은 모두 사전이 잡음');
const cases = JSON.parse(fs.readFileSync(path.join(__dirname, 'tts_cases.json'), 'utf8'));
let cbad = 0;
for (const [inp, want, lesson] of cases.cases) { const got = ttsNorm(inp, lex, order, lesson || 'L99a'); if (got !== want) { cbad++; fail(`본보기 「${inp}」 → 「${got}」 (기대 「${want}」)`); } }
if (!cbad) console.log(`  ✓ 본보기 ${cases.cases.length} 쌍`);
// 4. 빌드에 끼워 넣은 것
const probe = fs.readFileSync(path.join(ROOT, 'lesson/L17e.html'), 'utf8');
const lexJ = JSON.stringify(lex.words);
if (!probe.includes('TTS_LEX') || !probe.includes(lexJ.slice(0, 200)) || !probe.includes('function ttsNorm(')) fail('lesson/L17e.html 에 지금 사전 · ttsNorm 이 안 들어 있다 — node tools/build_lesson.js');
else console.log('  ✓ 과 화면에 사전 · ttsNorm 이 들어 있음(L17e 로 봄)');
console.log(bad ? `\n❌ 낭독 입력 실패 ${bad}` : '\n✅ 낭독 입력 통과');
process.exit(bad ? 1 : 0);
