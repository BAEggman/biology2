/* tts_norm.js — 낭독 입력 = ttsNorm(say) (보기 화면 명세 §2 · 낭독 명세 §2)
   화면 글(say)은 그대로 두고, 읽을 때만 로마자 · 그리스 글자 · 첨자 · 기호 · 과 번호를 말로 푼다.
   한 군데서만 정한다 — 과 화면(빌드가 이 함수와 사전을 끼워 넣음) · 기기 음성 · Gemini 에 주는 글 · 테스트가 모두 이것을 쓴다.
   차례: ① 과 번호 → 짧은 제목 「… 그림」 ② 로마 숫자(문맥) ③ 고정 표(이온 · 화학식 · 기호) ④ 낱말 사전 ⑤ 기본값(글자 이름 · 붙은 숫자)
   쓰는 법: const { ttsNorm } = require('./tts_norm'); ttsNorm(글, 사전(tools/tts_lexicon.json), 차례({과: 짧은 제목}), 과)
*/
(function (root, factory) {
  const api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  else root.TTSNorm = api;
})(typeof self !== 'undefined' ? self : this, function () {
  'use strict';
  const LETTER = { A: '에이', B: '비', C: '씨', D: '디', E: '이', F: '에프', G: '지', H: '에이치', I: '아이', J: '제이', K: '케이', L: '엘', M: '엠',
    N: '엔', O: '오', P: '피', Q: '큐', R: '알', S: '에스', T: '티', U: '유', V: '브이', W: '더블유', X: '엑스', Y: '와이', Z: '제트' };
  const EN = ['영', '원', '투', '쓰리', '포', '파이브', '식스', '세븐', '에이트', '나인'];
  const SINO_D = ['', '일', '이', '삼', '사', '오', '육', '칠', '팔', '구'];
  const GREEK = { α: '알파', β: '베타', γ: '감마', δ: '델타', ε: '엡실론', κ: '카파', λ: '람다', μ: '뮤', σ: '시그마', τ: '타우', ψ: '프사이', Ψ: '프사이', Δ: '델타', ω: '오메가', π: '파이', θ: '세타', χ: '카이', ρ: '로', φ: '파이', ζ: '제타' };
  const SUB = { '₀': '0', '₁': '1', '₂': '2', '₃': '3', '₄': '4', '₅': '5', '₆': '6', '₇': '7', '₈': '8', '₉': '9' };
  const SUP = { '⁰': '0', '¹': '1', '²': '2', '³': '3', '⁴': '4', '⁵': '5', '⁶': '6', '⁷': '7', '⁸': '8', '⁹': '9' };
  const ROMAN = { I: 1, II: 2, III: 3, IV: 4, V: 5, VI: 6, VII: 7 };
  // 고정 표 — 긴 것부터. 이온 · 화학식은 낱말로(명세 §2.3 「화학식」)
  const FIXED = [
    ['Na⁺-K⁺', '나트륨 칼륨'], ['Na⁺/K⁺', '나트륨 칼륨'], ['Na⁺/Ca²⁺', '나트륨 칼슘'], ['H⁺-ATPase', '수소 이온 에이 티 피 에이스'], ['K⁺-ATPase', '칼륨 이온 에이 티 피 에이스'],
    ['Na⁺', '나트륨 이온'], ['K⁺', '칼륨 이온'], ['Ca²⁺', '칼슘 이온'], ['Mg²⁺', '마그네슘 이온'], ['Fe²⁺', '철 이온'], ['Fe³⁺', '철 이온'], ['H⁺', '수소 이온'], ['Cl⁻', '염소 이온'],
    ['HCO₃⁻', '탄산수소 이온'], ['NH₄⁺', '암모늄 이온'], ['NO₃⁻', '질산 이온'], ['NO₂⁻', '아질산 이온'], ['NADP⁺', '엔 에이 디 피 플러스'], ['NAD⁺', '엔 에이 디 플러스'],
    ['FADH₂', '에프 에이 디 에이치 투'], ['QH₂', '큐 에이치 투'], ['2H₂O₂', '과산화수소 두 분자'], ['H₂O₂', '과산화수소'], ['2H₂O', '물 두 분자'],
    ['CO₂', '이산화탄소'], ['H₂O', '물'], ['O₂', '산소'], ['NH₃', '암모니아'], ['NO₃', '질산'], ['NO₂', '아질산'], ['NH₄', '암모늄'], ['N₂', '질소 기체'], ['NaCl', '염화나트륨'],
    ['5′', '오 프라임'], ['3′', '삼 프라임'], ['2′', '이 프라임'], ['′', ' 프라임'],
    ['→', ' 다음 '], ['≈', '약 '], ['↑', ' 증가'], ['↓', ' 감소'], ['↔', ' 그리고 '], ['⁺', ' 플러스'], ['⁻', ' 마이너스']];

  function sino(n) {  // 0 ~ 9999
    n = Number(n); if (!Number.isFinite(n)) return String(n); if (n === 0) return '영';
    let s = ''; const u = [[1000, '천'], [100, '백'], [10, '십']];
    for (const [v, w] of u) { const d = Math.floor(n / v) % 10; if (d) s += (d === 1 ? '' : SINO_D[d]) + w; }
    return s + SINO_D[n % 10];
  }
  const tailNum = d => d.length === 1 ? EN[+d] : sino(d);   // 글자 뒤에 붙은 수 — 한 자리는 원 · 투 …, 두 자리부터 한자어
  const lettersOf = s => [...s].map(ch => LETTER[ch.toUpperCase()] || ch).join(' ');

  // 낱말 하나(사전에 없을 때) — 글자 이름 · 붙은 숫자 · 그리스 · 첨자
  function spell(tok) {
    const parts = []; let m; const re = /([0-9]+)|([A-Za-z]+)|([α-ωΑ-ΩΨΔ])|([₀-₉]+)|([⁰-⁹¹²³]+)/g; let prevLetter = false;
    while ((m = re.exec(tok))) {
      if (m[1]) { parts.push(prevLetter ? tailNum(m[1]) : sino(m[1])); prevLetter = false; }
      else if (m[2]) { parts.push(lettersOf(m[2])); prevLetter = true; }
      else if (m[3]) { parts.push(GREEK[m[3]] || m[3]); prevLetter = true; }
      else if (m[4]) { const d = [...m[4]].map(c => SUB[c]).join(''); parts.push(tailNum(d)); prevLetter = false; }
      else if (m[5]) { const d = [...m[5]].map(c => SUP[c]).join(''); parts.push(tailNum(d)); prevLetter = false; }
    }
    return parts.join(' ');
  }

  const TOKEN = /[A-Za-zα-ωΑ-ΩΨΔ0-9₀-₉⁰-⁹¹²³][A-Za-zα-ωΑ-ΩΨΔ0-9₀-₉⁰-⁹¹²³\-]*/g;
  const HAS = /[A-Za-zα-ωΑ-ΩΨΔ₀-₉⁰-⁹¹²³]/;
  const ROMAN_EN_BEFORE = /(복합체|MHC|Type|타입|기계|중합효소|광계|클래스|폴|Pol|전기|중기|후기|말기|안지오텐신|Ⅰ)\s*$/;

  // 바뀐 읽기 뒤에 바로 붙은 조사를 받침에 맞춘다(「Ca²⁺가」 → 「칼슘 이온이」) — 띄어쓰기 · 문장부호 앞의 조사만
  const PAIR = { '가': ['이', '가'], '이': ['이', '가'], '를': ['을', '를'], '을': ['을', '를'], '는': ['은', '는'], '은': ['은', '는'], '와': ['과', '와'], '과': ['과', '와'] };
  const PART = /^(으로|로|가|이|를|을|는|은|와|과)(?=[\s,.·)」'"!?:;]|$)/;
  function particle(reading, p) {
    const c = reading.slice(-1).charCodeAt(0);
    if (!(c >= 0xAC00 && c <= 0xD7A3)) return p;
    const jong = (c - 0xAC00) % 28;
    if (p === '로' || p === '으로') return (jong === 0 || jong === 8) ? '로' : '으로';
    return PAIR[p][jong ? 0 : 1];
  }
  function rep(t, from, to) {   // from 을 to 로 — 바로 뒤 조사도 맞춘다
    let out = '', i = 0, k;
    while ((k = t.indexOf(from, i)) >= 0) {
      out += t.slice(i, k) + to; i = k + from.length;
      const m = PART.exec(t.slice(i)); if (m) { out += particle(to, m[1]); i += m[1].length; }
    }
    return out + t.slice(i);
  }
  function ttsNorm(text, lex, order, lesson) {
    const W = (lex && lex.words) || {};
    let t = String(text);
    // ① 과 번호
    t = t.replace(/L(\d{2})([a-z]?)(?![A-Za-z0-9])((?:으로|로|가|이|를|을|는|은|와|과)(?=[\s,.·)」'"!?:;]|$))?/g, (all, n, c, pp) => {
      const id = 'L' + n + c; const title = order && order[id];
      const w = title ? `「${title}」 그림` : '다른 그림';
      return pp ? w + particle('그림', pp) : w;   // 「… 그림」 뒤 조사는 받침에 맞춤(그림와 → 그림과)
    });
    // ①-2 화학 위치 번호 「1,6-」 「1,3-」 → 「일 육 」(쉼표를 「콤마」로 읽지 않게)
    t = t.replace(/(?<![\d.])(\d),(\d)-/g, (all, a, b) => sino(+a) + ' ' + sino(+b) + ' ');
    // ② 로마 숫자(문맥) — 볼티모어 군 · 부두 번호는 한자어 수, 나머지는 영어 수. 대 · 자 · 선 · 기가 붙으면 글자
    const baltimore = /^L01/.test(lesson || '');
    t = t.replace(/(?<![A-Za-z0-9])(VII|VI|IV|V|III|II|I)(b|x)?(?![A-Za-z0-9₀-₉])((?:으로|로|가|이|를|을|는|은|와|과)(?=[\s,.·)」'"!?:;]|$))?/g, (all0, r, suf, pp, off, str) => {
      const all = r + (suf || ''); const P = x => x === all ? all0 : x + (pp ? particle(x, pp) : '');
      const after = str.slice(off + all.length, off + all.length + 3), before = str.slice(Math.max(0, off - 12), off);
      if (/^\s?(대|자|선)/.test(after)) return all0;                       // I대 · V자 · Z선 → 글자(기본값)
      const n = ROMAN[r];
      if (/^\s?(번|군)/.test(after) || (baltimore && !suf)) return P(sino(n) + (suf ? ' ' + lettersOf(suf) : ''));
      if (r === 'V' || (r === 'I' && !suf && !ROMAN_EN_BEFORE.test(before) && !/^\s?(→|·|,)/.test(after) && !/(→|·)\s*$/.test(before))) return all0;  // 글자 V · I
      return P(EN[n] + (suf ? ' ' + lettersOf(suf) : ''));
    });
    // ③ 고정 표(사전의 fixed 가 먼저)
    for (const [a, b] of [...((lex && lex.fixed) || []), ...FIXED]) t = rep(t, a, b);
    t = t.replace(/이온 이온/g, '이온');
    // ④ · ⑤ 낱말
    const readTok = tok => {
      const core = tok.replace(/^-+|-+$/g, '');
      if (!HAS.test(core)) return tok;                                    // 수만 — 그대로
      if (W[core] !== undefined) return tok.replace(core, W[core]);
      const lower = core.toLowerCase();
      if (W[lower] !== undefined && /^[a-z]/.test(core)) return tok.replace(core, W[lower]);
      let prevWord = false;
      return tok.replace(core, core.split('-').filter(Boolean).map(p => {
        const r = W[p] !== undefined ? W[p] : (/^[0-9]+$/.test(p) && prevWord ? tailNum(p) : spell(p));
        prevWord = /[A-Za-zα-ωΑ-ΩΨΔ]/.test(p); return r;
      }).join(' '));
    };
    const TOKP = new RegExp('(' + TOKEN.source + ')((?:으로|로|가|이|를|을|는|은|와|과)(?=[\\s,.·)」\'"!?:;]|$))?', 'g');
    t = t.replace(TOKP, (all, tok, p) => { const r = readTok(tok); return p && r !== tok ? r + particle(r, p) : r + (p || ''); });
    // 남은 그리스 · 첨자
    t = t.replace(/[α-ωΑ-ΩΨΔ]/g, g => GREEK[g] || g).replace(/[₀-₉]/g, c => SUB[c]);
    return t.replace(/ {2,}/g, ' ');
  }
  // 감사용 — 낱말마다 어느 규칙이 잡았나(사전 · 기본값)
  function classify(tok, lex) {
    const W = (lex && lex.words) || {}; const core = tok.replace(/^-+|-+$/g, '');
    if (W[core] !== undefined) return 'lex';
    // 소문자 세 글자 이상이 든 조각은 사전이 잡아야 한다(나머지 조각은 글자 이름이어도 된다)
    return core.split('-').filter(Boolean).every(p => W[p] !== undefined || !/[a-z]{3,}/.test(p)) ? 'lex' : 'default';
  }
  return { ttsNorm, spell, sino, classify, LETTER, FIXED, TOKEN_RE: TOKEN };
});
