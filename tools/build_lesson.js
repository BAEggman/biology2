#!/usr/bin/env node
// build_lesson.js — lessons/<ID>.json + tools/lesson_player.html → lesson/<ID>.html (그림은 lesson/img/<ID>.webp) · lesson/index.html(과 목록 + 갈아엎기 진척)
// 사용: node tools/build_lesson.js L31a [L16a …] [--standalone DIR]   (인자 없으면 lessons/*.json 전부)
// 함께 쓰는 것: lesson/map.js(옛 판 → 새 과 — Sketchy 허브 sketchy.html 이 읽어 판마다 「새 과」 단추를 단다) · index.html(SRS) 「새 Sketchy 과」 배지의 숫자
//   --standalone DIR : 그림을 data: URI 로 안에 넣은 한 파일 <ID>_standalone.html 을 DIR 에 따로(저장소에는 안 둔다)
const fs = require('fs'), path = require('path'), { execSync } = require('child_process');
const { createHash } = require('node:crypto');
const { ROOT, panelIndex, resolveRef, strip, stopCards, deck } = require('./lesson_lib');
const tpl = fs.readFileSync(path.join(__dirname, 'lesson_player.html'), 'utf8');
const argv = process.argv.slice(2); const si = argv.indexOf('--standalone');
const standaloneDir = si >= 0 ? argv[si + 1] : null;
let ids = si >= 0 ? argv.filter((_, k) => k !== si && k !== si + 1) : argv;
if (!ids.length) ids = fs.readdirSync(path.join(ROOT, 'lessons')).filter(f => /^L\d{2}[a-z]?\.json$/.test(f)).map(f => f.slice(0, -5)).sort();
fs.mkdirSync(path.join(ROOT, 'lesson'), { recursive: true });
const idx = panelIndex();
const SITE = 'https://baeggman.github.io/biology2/';  // GitHub Pages 배포 주소 — 한 파일(standalone)의 바깥 링크에만 쓴다
// 카드(SRS) — 정거장이 카드를 곧장 가리킬 때(stops[].cards) 있는 카드인지 보고, 시험 화면의 「딸린 기출」 글을 싣는다
const CARDS = (() => { const m = fs.readFileSync(path.join(ROOT, 'index.html'), 'utf8').match(/<script[^>]*id=["']CARDS["'][^>]*>([\s\S]*?)<\/script>/); const o = {}; if (m) for (const c of JSON.parse(m[1])) o[c.id] = c; return o; })();
// 정거장의 카드 = 옛 판 행(src)에 딸린 카드 + 곧장 건 카드(cards — 옛 판에 없는 카드를 새 과에 걸 때)
const cardsOf = s => stopCards(s, idx);
const firstPanel = L => { for (const s of L.stops) for (const r of (s.src || [])) return r.split('#')[0]; return null; };
for (const id of ids) {
  const L = JSON.parse(fs.readFileSync(path.join(ROOT, 'lessons', id + '.json'), 'utf8'));
  if (L.id !== id) { console.error(`[${id}] json 의 id 가 ${L.id}`); process.exitCode = 1; continue; }
  const bad = [];
  L.stops.forEach((s, k) => {
    if (s.box) for (const [x, y, w, h] of (Array.isArray(s.box[0]) ? s.box : [s.box])) { if (x < 0 || y < 0 || x + w > L.w || y + h > L.h) bad.push(`${k}: 상자가 그림 밖 ${[x, y, w, h]}`); }
    if ((s.fact || '').length > 60) bad.push(`${k}: 사실 ${s.fact.length}자 (> 60)`);
    if (!s.say) bad.push(`${k}: say 없음`);
    if (!s.sid) bad.push(`${k}: sid 없음 — python3 tools/lesson_sid.py ${id}`);
    for (const r of (s.src || [])) { try { resolveRef(r, idx); } catch (e) { bad.push(`${k}: ${e.message}`); } }
    for (const c of (Array.isArray(s.cards) ? s.cards : [])) if (!CARDS[c]) bad.push(`${k}: 곧장 건 카드가 없다 ${c}`);
    if (s.cards !== undefined && !Array.isArray(s.cards)) bad.push(`${k}: cards 는 카드 ID 배열`);
    for (const c of (Array.isArray(s.drop) ? s.drop : [])) if (!CARDS[c]) bad.push(`${k}: 뗄 카드가 없다 ${c}`);
    s.cards = cardsOf(s);
  });
  { const sids = L.stops.map(s => s.sid); if (new Set(sids).size !== sids.length) bad.push('sid 가 겹친다'); }
  if (bad.length) { console.error(`[${id}] 검사 실패:\n  ` + bad.join('\n  ')); process.exitCode = 1; continue; }
  L.cq = {};  // 딸린 기출의 물음 · 답(시험 화면에서 답을 본 뒤 채점 기준으로 편다)
  for (const s of L.stops) for (const c of s.cards) { const C = CARDS[c]; if (C && !L.cq[c]) L.cq[c] = [strip(C.q), strip(Array.isArray(C.it) && C.it.length ? C.it.join(' · ') : C.a)]; }
  L.hubPanel = firstPanel(L);  // 「Sketchy 허브(옛 판)」 링크가 이 과의 첫 옛 판으로 간다
  const imgPath = path.join(ROOT, 'lesson', L.img);
  const webLesson = { ...L };
  if (fs.existsSync(imgPath)) {
    const revision = createHash('sha256').update(fs.readFileSync(imgPath)).digest('hex').slice(0, 12);
    webLesson.img += '?v=' + revision;
  }
  const html = tpl.replace('__TITLE__', L.title.replace(/[<&]/g, '')).replace('__DATA__', JSON.stringify(webLesson));
  fs.writeFileSync(path.join(ROOT, 'lesson', id + '.html'), html);
  const ncards = new Set(L.stops.flatMap(s => s.cards)).size;
  console.log(`[${id}] lesson/${id}.html · 정거장 ${L.stops.length} · 기출 카드 ${ncards} · 그림 ${fs.existsSync(imgPath) ? 'ok' : '없음: ' + L.img}`);
  if (standaloneDir && fs.existsSync(imgPath)) {
    const ext = path.extname(imgPath).slice(1); const b64 = fs.readFileSync(imgPath).toString('base64');
    const L2 = Object.assign({}, L, { img: `data:image/${ext};base64,${b64}`, home: SITE + 'lesson/index.html', hub: SITE + 'sketchy.html' + (L.hubPanel ? '#' + L.hubPanel : '') });
    const out = path.join(standaloneDir, `${id}_standalone.html`);
    fs.writeFileSync(out, tpl.replace('__TITLE__', L.title.replace(/[<&]/g, '')).replace('__DATA__', JSON.stringify(L2)));
    console.log(`  standalone → ${out} (${Math.round(fs.statSync(out).size / 1024)} KB)`);
  }
}
// ── lesson/index.html — 과 목록(있는 것) + 묶음별 진척(카드 많은 순)
const cover = JSON.parse(execSync('node ' + path.join(__dirname, 'lesson_cover.js') + ' --json', { encoding: 'utf8' }));
const all = fs.readdirSync(path.join(ROOT, 'lessons')).filter(f => /^L\d{2}[a-z]?\.json$/.test(f)).sort()
  .map(f => JSON.parse(fs.readFileSync(path.join(ROOT, 'lessons', f), 'utf8')));
const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;');
const tot = cover.reduce((a, x) => ({ r: a.r + x.rows, c: a.c + x.cards, rc: a.rc + x.rowsCovered, cc: a.cc + x.cardsCovered }), { r: 0, c: 0, rc: 0, cc: 0 });
// SRS 카드 전체(부모 기준)가 어디 있나 — 지은 과 · 과가 아직 없는 옛 s 판 · d 묶음 · 그림이 아무 데도 없음 (GPT 감사: 「67.2%」 하나로는 그림 없는 카드가 안 보인다)
const cardPlace = (() => {
  const covered = new Set(); for (const L of all) for (const st of L.stops) for (const r of (st.src || [])) covered.add(r);
  const direct = new Set(); for (const L of all) for (const st of L.stops) for (const c of (Array.isArray(st.cards) ? st.cards : [])) direct.add(c.replace(/#\d+$/, ''));
  const where = {};
  for (const sc of deck()) for (const P of sc.panels) { if (P.retired) continue; P.f.forEach((row, i) => { for (const c0 of (row[2] || [])) { const c = c0.replace(/#\d+$/, ''); const w = (where[c] = where[c] || new Set()); w.add(covered.has(P.id + '#' + i) ? 'built' : sc.id[0] === 'd' ? 'd' : 'pendS'); } }); }
  for (const c of direct) (where[c] = where[c] || new Set()).add('built');
  const cls = id => { const w = where[id]; if (!w) return null; return w.has('built') ? 'built' : w.has('pendS') ? 'pendS' : 'd'; };
  const T = { tot: 0, built: 0, pendS: 0, d: 0, none: 0 };
  for (const c of Object.values(CARDS)) { const st = cls(c.id) || (c.p && c.p !== c.id ? cls(c.p) : null) || 'none'; T.tot++; T[st]++; }
  return T;
})();
const idxHtml = `<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>과(lesson) 목록 — 생물 Sketchy</title>
<style>body{margin:0;font-family:-apple-system,"Apple SD Gothic Neo","Noto Sans KR",sans-serif;background:#f7f5ef;color:#1b1b1f}.wrap{max-width:900px;margin:0 auto;padding:16px}
h1{font-size:20px}h2{font-size:15px;margin-top:22px}.sub{color:#4b4b55;font-size:13px}a{color:#0f766e}table{border-collapse:collapse;width:100%;font-size:13px}td,th{border-bottom:1px solid #e3e1da;padding:5px 6px;text-align:left}th{color:#4b4b55;font-weight:600}
.card{display:block;border:1px solid #e3e1da;background:#fff;border-radius:12px;padding:12px 14px;margin:8px 0;text-decoration:none;color:inherit}.card b{color:#0f766e}.bar{height:6px;background:#e3e1da;border-radius:3px;overflow:hidden}.bar i{display:block;height:100%;background:#0f766e}</style></head><body><div class="wrap">
<h1>과(lesson) 목록</h1><p class="sub">Sketchy 식 — 한 장면 · 물건 하나 = 사실 하나 · 투어로 듣고 그림만으로 되찾는다. 옛 덱은 과가 다 설 때까지 그대로 — <a href="../sketchy.html">Sketchy 허브</a>(옛 그림 판 · 판마다 「새 과」 단추) · <a href="symbols.html">기호 사전</a>(같은 물건 = 같은 뜻) · <a href="../index.html">SRS</a>(기출 카드).</p>
${all.map(L => `<a class="card" href="${L.id}.html"><b>${esc(L.id)}</b> ${esc(L.title)}<div class="sub">정거장 ${L.stops.length} · 기출 카드 ${new Set(L.stops.flatMap(cardsOf)).size} · ${esc(L.sub || '')}</div></a>`).join('')}
<h2>SRS 카드 ${cardPlace.tot}장이 어디 있나</h2><p class="sub">지은 과 <b>${cardPlace.built}</b> · 과가 아직 없는 옛 s 판 <b>${cardPlace.pendS}</b> · d 묶음(도해) <b>${cardPlace.d}</b> · <b>그림이 아무 데도 없음 ${cardPlace.none}</b> — 아래 진척 막대는 옛 판에 딸린 카드만 센다.</p>\n<h2>갈아엎기 진척 — 행 ${tot.rc}/${tot.r} · 기출 카드 ${tot.cc}/${tot.c}</h2><div class="bar"><i style="width:${(100 * tot.cc / Math.max(1, tot.c)).toFixed(1)}%"></i></div>
<table><tr><th>묶음</th><th>단원</th><th>카드</th><th>행</th><th>덮인 행</th><th>덮인 카드</th><th>과</th></tr>
${cover.map(x => `<tr><td>${x.id}</td><td>${esc(x.unit)}</td><td>${x.cards}</td><td>${x.rows}</td><td>${x.rowsCovered}</td><td>${x.cardsCovered}</td><td>${x.lessons.map(l => `<a href="${l}.html">${l}</a>`).join(' ')}</td></tr>`).join('')}
</table><p class="sub">d 묶음(도해)은 s 묶음을 다 세운 뒤 결정(2026-11-08).</p></div></body></html>`;
fs.writeFileSync(path.join(ROOT, 'lesson', 'index.html'), idxHtml);
console.log(`lesson/index.html · 과 ${all.length} · 덮인 카드 ${tot.cc}/${tot.c}`);
// ── lesson/map.js — 옛 판(패널) id → 그 판의 행을 정거장 src 로 쓰는 과. Sketchy 허브가 읽는다(2026-11-10 · 사용자 「sketchy 허브에서 찾을 수가 없는데?」).
const panels = {}, names = {};
for (const L of all) {
  names[L.id] = String(L.title).split(' — ')[0].trim();
  for (const s of L.stops) for (const r of (s.src || [])) {
    const pid = String(r).split('#')[0];
    if (!idx[pid]) continue;
    (panels[pid] = panels[pid] || []).includes(L.id) || panels[pid].push(L.id);
  }
}
for (const k of Object.keys(panels)) panels[k].sort();
const map = { n: all.length, cards: `${tot.cc}/${tot.c}`, lessons: names, panels };
fs.writeFileSync(path.join(ROOT, 'lesson', 'map.js'),
  '/* build_lesson.js 생성물 — 손으로 고치지 말 것. 옛 판(패널) id → 그 판의 행을 정거장으로 쓰는 새 과. Sketchy 허브(sketchy.html)가 읽어 판마다 「새 과」 단추를 단다. */\n'
  + 'window.LESSON_MAP = ' + JSON.stringify(map) + ';\n');
console.log(`lesson/map.js · 과 ${all.length} · 옛 판 ${Object.keys(panels).length}`);
// ── index.html(SRS) 「새 Sketchy 과」 배지의 숫자 — 있으면 맞춘다
const IX = path.join(ROOT, 'index.html');
if (fs.existsSync(IX)) {
  const ix = fs.readFileSync(IX, 'utf8');
  const re = /(<a class="badge pic" id="lessonBtn"[^>]*>[\s\S]*?<b>)\d+(개<\/b>)/;
  if (re.test(ix)) { const nx = ix.replace(re, `$1${all.length}$2`); if (nx !== ix) { fs.writeFileSync(IX, nx); console.log(`index.html 「새 Sketchy 과」 배지 → ${all.length}개`); } }
}
// ── lesson/symbols.html — 기호 사전: 되풀이되는 물건 = 같은 뜻(tools/hooks.json 「_심볼예약」). 어느 과의 물건 · 고리에 그 물건 이름이 나오는지 함께 보인다(2026-11-11 감사 고침 5 · 심볼).
{
  const H = JSON.parse(fs.readFileSync(path.join(__dirname, 'hooks.json'), 'utf8'));
  const R = H['_심볼예약'] || {};
  const short = t => {  // 만든 사람의 메모(날짜 꼬리표 · 판 번호 · 【참조】)를 걷어 내고 첫 마디만
    let s = String(t).split('★')[0].replace(/\[\d{4}-\d{2}-\d{2}[^\]]*\]/g, '').replace(/【[^】]*】/g, '').replace(/\((?:[^()]*?(?:L\d{2}[a-z]?|s\d{2}[pu]\d{2})[^()]*)\)/g, '').replace(/\bs\d{2}[pu]\d{2}[a-z]?\S*/g, '').replace(/\s+/g, ' ').trim();
    const m = s.match(/^(.{4,80}?)(?:[.。:]\s|\s—\s|$)/); s = (m ? m[1] : s.slice(0, 80)).replace(/[\s·,:—-]+$/, '').trim();
    s = s.replace(/<[^>]+>/g, '').replace(/⚠+/g, '').replace(/\(\s*[·,\s]*\)/g, '').replace(/\s+/g, ' ').trim();
    if (s.length > 40) { const c = s.search(/\s[—(]|\s\(/); if (c >= 2) s = s.slice(0, c).trim(); }
    return s || String(t).slice(0, 60);
  };
  const rows = [];
  for (const [k, v] of Object.entries(R)) {
    const where = [];
    for (const L of all) L.stops.forEach((s, i) => { if (((s.obj || '') + ' ' + (s.hook || '')).includes(k)) where.push([L.id, i]); });
    if (!where.length) continue;
    rows.push({ k, m: short(v), where, n: new Set(where.map(w => w[0])).size });
  }
  rows.sort((a, b) => b.n - a.n || a.k.localeCompare(b.k, 'ko'));
  const symHtml = `<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>기호 사전</title>
<style>body{margin:0;font-family:-apple-system,"Apple SD Gothic Neo","Noto Sans KR",sans-serif;background:#f7f5ef;color:#1b1b1f}.wrap{max-width:900px;margin:0 auto;padding:16px}h1{font-size:20px}.sub{color:#4b4b55;font-size:13px}a{color:#0f766e}table{border-collapse:collapse;width:100%;font-size:13px}td,th{border-bottom:1px solid #e3e1da;padding:6px;text-align:left;vertical-align:top}th{color:#4b4b55;font-weight:600}td.k{font-weight:600;white-space:nowrap}td.w a{margin-right:6px}</style></head><body><div class="wrap">
<p><a href="index.html">← 과 목록</a></p><h1>기호 사전 — 같은 물건은 어느 과에서나 같은 뜻</h1>
<p class="sub">Sketchy 의 약속: 되풀이되는 물건은 덱 전체에서 한 뜻만 나른다. 아래는 만든 사람이 정해 둔 예약(${Object.keys(R).length}항) 가운데 지금 과에 나오는 ${rows.length}개 — 많이 나오는 순. 과 번호를 누르면 그 과로 간다.</p>
<table><tr><th>물건</th><th>뜻</th><th>나오는 과</th></tr>
${rows.map(r => `<tr><td class="k">${esc(r.k)}</td><td>${esc(r.m)}</td><td class="w">${[...new Set(r.where.map(w => w[0]))].map(id => `<a href="${id}.html">${id}</a>`).join('')}</td></tr>`).join('\n')}
</table></div></body></html>`;
  fs.writeFileSync(path.join(ROOT, 'lesson', 'symbols.html'), symHtml);
  console.log(`lesson/symbols.html · 기호 ${rows.length}/${Object.keys(R).length}`);
}
