#!/usr/bin/env node
/* mkpacket.js <과>[,<과>…] [<날짜 MMDD>] [--words 낱말,낱말] [--name 일감이름]
 * 6+1 일감 꾸러미(tools/cue/README.md §2 · 지시서_Opus_이름고리 §4 · 2026-11-22 · Opus 5.5).
 *   tools/cue/jobs/<MMDD>_<이름>/packet.md · img/(과가 하나면 바로 · 여럿이면 img/<과>/)full.jpg · small.jpg · sN.jpg(· sN_k.jpg)
 *   과가 여럿이면 기호 일감(README §1 — 여러 과에 걸친 기호를 과보다 먼저): 같은 낱말이 나오는 과들을 한 꾸러미로.
 *   일감 표의 「고리가 필요한 낱말」은 이름 장부(tools/cue/names/장부.json)의 그 과 줄(갈래 ㉰ · ㉱ · ㉲ — 또는 --words)에서.
 *   과가 여럿이면 낱말이 걸린 정거장만 적는다(꾸러미가 커지지 않게).
 *   넣지 않는 것: 본 세션이 미리 생각한 안 · 다른 제안자의 글 · 채점표의 점수 항목 · 지난 회의 제안.
 */
const fs = require('fs'), path = require('path'), cp = require('child_process');
const ROOT = path.join(__dirname, '..', '..');
const { stopCards, panelIndex } = require('../lesson_lib');
const a = process.argv.slice(2);
const LS = (a[0] || '').split(',');
if (!LS.every(x => /^L\d\d[a-z]$/.test(x))) { console.error('쓰임: mkpacket.js <과>[,<과>…] [MMDD] [--words a,b] [--name 이름]'); process.exit(1); }
const day = (a[1] && /^\d{4}$/.test(a[1])) ? a[1] : (() => { const d = new Date(Date.now() + 9 * 3600e3); return String(d.getUTCMonth() + 1).padStart(2, '0') + String(d.getUTCDate()).padStart(2, '0'); })();
const opt = k => { const i = a.indexOf(k); return i >= 0 ? a[i + 1] : null; };
const job = `${day}_${opt('--name') || LS.join('_')}`;
const dir = path.join(ROOT, 'tools/cue/jobs', job); fs.mkdirSync(path.join(dir, 'img'), { recursive: true });
const strip = x => String(x == null ? '' : x).replace(/<[^>]+>/g, '').replace(/\s+/g, ' ').trim();
const H = JSON.parse(fs.readFileSync(path.join(ROOT, 'tools/hooks.json'), 'utf8'));
const CARDS = {}; for (const c of JSON.parse(fs.readFileSync(path.join(ROOT, 'index.html'), 'utf8').match(/id=["']CARDS["'][^>]*>([\s\S]*?)<\/script>/)[1])) if (c) CARDS[c.id] = c;
const LED = JSON.parse(fs.readFileSync(path.join(ROOT, 'tools/cue/names/장부.json'), 'utf8'));
const LOCK = JSON.parse(fs.readFileSync(path.join(ROOT, 'tools/cue/lock.json'), 'utf8'));
const CANON = JSON.parse(fs.readFileSync(path.join(ROOT, 'tools/cue/canon.json'), 'utf8'));
const want = opt('--words') ? opt('--words').split(',') : null;
const idx = panelIndex();
const syl = w => /[가-힣]/.test(w) ? [...w].join(' · ') : w.split('').join(' ');
const multi = LS.length > 1;
const o = [], allRows = [], allWords = new Set();
o.push(`# 일감 ${job} — ${multi ? '기호 일감(여러 과): ' + LS.join(' · ') : LS[0]}`, '', '> 6+1 꾸러미(tools/cue/README.md §2). 여섯 제안자에게 똑같이 준다. 이 파일과 img/ 만 읽는다.', '');
if (multi) o.push('> **기호 일감**: 같은 개념이 여러 과에 나온다. 덱 전체에서 한 개념 = 한 기호(채점표 P7) — 과마다 따로 짓지 말고, 어느 과에서나 같은 물건 · 같은 꼴로 쓸 안을 내라. 과마다 그 기호가 들어갈 자리(이미 있는 소품에 얹을지 · 작은 새 소품인지)도 적는다.', '');
for (const L of LS) {
  const d = JSON.parse(fs.readFileSync(path.join(ROOT, 'lessons', L + '.json'), 'utf8'));
  const sub = multi ? L + '/' : '';
  const idir = path.join(dir, 'img', multi ? L : ''); fs.mkdirSync(idir, { recursive: true });
  cp.execFileSync('python3', [path.join(ROOT, 'tools/prompts/mkcheck2.py'), L, idir, d.stops.filter(s => s.box).map(s => s.sid).join(',')], { stdio: 'ignore' });
  try { fs.unlinkSync(path.join(idir, 'stops.tsv')); } catch (e) {}
  cp.execFileSync('python3', ['-c', `from PIL import Image\nim=Image.open('${ROOT}/lesson/img/${L}.webp').convert('RGB')\nim.resize((780,round(im.height*780/im.width)),Image.LANCZOS).save('${idir}/small.jpg',quality=88)`]);
  const imgs = fs.readdirSync(idir).filter(f => f.endsWith('.jpg')).sort();
  const rows = Object.values(LED).filter(e => e.과 === L && e.출처 === '못 꺼냄' && (want ? want.includes(e.낱말) : ['㉰', '㉱', '㉲'].includes(e.갈래)));
  allRows.push(...rows); rows.forEach(e => allWords.add(e.낱말));
  const bySid = {}; for (const e of rows) for (const s of e.구간) (bySid[s] = bySid[s] || []).push(e);
  o.push(`## ${multi ? L + ' — ' : '1. 세계 — '}${strip(d.title)}`, `- 한 줄: ${strip(d.sub)}`, `- 그림: \`img/${sub}full.jpg\`(1400 px) · \`img/${sub}small.jpg\`(780 px — 작은 화면) · 정거장 조각 ${imgs.filter(f => /^s\d/.test(f)).map(f => '`img/' + sub + f + '`').join(' ')}`, '');
  o.push(multi ? `### ${L} 일감 표` : '## 2. 일감 표 — 정거장마다', '');
  for (const s of d.stops) {
    const ws = bySid[s.sid] || [];
    if (multi && !ws.length) { o.push(`- ${L} ${s.sid}(그대로 둘 것): ${strip(s.obj)}`); continue; }
    o.push(`${multi ? '####' : '###'} ${L} ${s.sid}${ws.length ? ' ★ 고리가 필요한 낱말: ' + [...new Set(ws.map(e => e.낱말))].join(' · ') : ''}`);
    o.push(`- 지금 그려진 것(obj): ${strip(s.obj)}`, `- 사실(fact): ${strip(s.fact)}`, `- 지금 고리 문장(hook): ${strip(s.hook)}`);
    if (ws.length) {
      for (const id of stopCards(s, idx).slice(0, 8)) { const c = CARDS[id.split('#')[0]]; if (c) o.push(`- 카드 ${id}: ${strip(c.q)} → ${strip(c.a)}${c.it ? ' · ' + c.it.map(strip).join(' / ') : ''}`); }
      o.push(`- 지금 낭독(say): ${strip(s.say)}`);
    }
    for (const e of ws) {
      o.push(`- **${e.낱말}** — 쪼개기: ${syl(e.낱말)} · 걸린 카드(답) ${e.카드.답}`);
      o.push(`  - 지금 고리와 안 된 까닭: 글을 받지 않은 독자가 그림만 보고 이 낱말을 이 정거장에서 꺼내지 못했다(N${e.사전 ? '′ — 사전엔 고리가 있는데 이 과에서 흘림' : ''}). 독자의 답: ${e['독자 ㄴ'] || '없음'}`);
      if (e.사전) o.push(`  - 고리 사전(hooks.json)에 이미 있는 것 — 되살릴 수 있는 안: ${(e.사전.props || []).join(' / ')} (${e.사전.형태 || ''})`);
      const g = (e['독자 ㄱ'] || {})[s.sid] || []; if (g.length) o.push(`  - 글을 안 본 독자가 이 조각의 물건을 부른 이름: ${g.join(' ‖ ')}`);
    }
    o.push('');
  }
  if (LOCK[L]) o.push(`- 잠긴 과(tools/cue/lock.json): ${L} — 잠긴 구역 ${JSON.stringify(LOCK[L].그림영역 || {})}. 잠긴 글 · 그림은 바꾸지 않는다.`, '');
  o.push('');
}
o.push('## 3. 그대로 둘 것', `- 각 과의 다른 정거장 물건은 위 표의 obj 그대로 — 새 고리 물건이 이것들과 겹치거나 뜻을 빼앗으면 안 된다.`);
o.push('- 사용자가 좋다고 한 고리(RUBRIC §5): 낫 = 레닌 · 에이스 카드 = DnaA · 빗자루 = DnaB · 소금 알갱이를 도로 담는 인부 = 알도스테론 · 퀸 카드 = PQ · 컴퓨터 = PC · 플로피디스크 = Fd · 파라솔 · 토르의 망치 · 몬스터 = 파라토르몬 …(쓰려면 같은 뜻으로만).', '');
o.push('## 4. 임자 있는 기호', '- 덱 약속(같은 뜻으로만 다시 쓴다): 칼 = K⁺ · 소금 자루 = Na⁺ · 염소 = Cl⁻ · 자갈 = Ca²⁺ · 금색 자물쇠 = 약물 · 독 · 빨간 도장 = 인산화 · 동전 = ATP · 짙은 회색 네모 칩 = GTP · 알/베의 개수 = α₁ · α₂ / β₁ · β₂ · 레몬 = H⁺ · 분필 = HCO₃⁻.');
o.push('- 예약 기호 전체 목록은 길다 — 쓰려는 물건 · 소리마다 `python3 tools/cue/reserved.py <낱말>` 로 직접 찾아 그 결과를 안에 적는다(예: `reserved.py 사다리` · `reserved.py 모자`). 찾지 않은 물건은 쓰지 마라.');
for (const r of (CANON.규칙 || []).filter(r => [...allWords].some(w => JSON.stringify(r).includes(w)))) o.push(`- [정본] ${r.개념} = ${r.있어야.join(' / ')}`);
o.push('');
o.push('## 5. 그림 조건', '- 글자 · 숫자 · 판(간판 · 말풍선 · 확대경 · 포스터 · 화면) 없음 · 화살표 · 칸 · 범례 없음 · 한 장면 한 사건 · 아는 캐릭터 · 실존 인물 · 상표 없음.', '- 고리 물건은 짧은 변 110 px 이상(2048 px 그림 기준) · 780 px 로 줄여도 무엇인지 말할 수 있어야 한다 · 되도록 구역 편집 한 번으로 들어갈 것.');
o.push('- 이번 일감은 **두 길을 다** 낸다(낱말마다): **(글)** 이미 그려져 있고 독자가 알아본 소품의 일상 이름에 그 낱말을 잇기 — 낭독에 한 문장만 보태고 그림은 그대로 / **(그림)** 작은 새 소품 하나 또는 있는 소품을 알아보게 키우기. 같은 소품에 뜻을 둘 얹지 않는다(이미 다른 이름을 나르는 소품에는 얹지 않는다).', '');
fs.writeFileSync(path.join(dir, 'packet.md'), o.join('\n') + '\n');
console.log(job, '· 과', LS.length, '· 낱말', allRows.length, '→', path.relative(ROOT, dir));
