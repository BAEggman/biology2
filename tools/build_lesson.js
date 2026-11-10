#!/usr/bin/env node
// build_lesson.js — lessons/<ID>.json + tools/lesson_player.html → lesson/<ID>.html (그림은 lesson/img/<ID>.webp) · lesson/index.html(과 목록 + 갈아엎기 진척)
// 사용: node tools/build_lesson.js L31a [L16a …] [--standalone DIR]   (인자 없으면 lessons/*.json 전부)
// 함께 쓰는 것: lesson/map.js(옛 판 → 새 과 — Sketchy 허브 sketchy.html 이 읽어 판마다 「새 과」 단추를 단다) · index.html(SRS) 「새 Sketchy 과」 배지의 숫자
//   --standalone DIR : 그림을 data: URI 로 안에 넣은 한 파일 <ID>_standalone.html 을 DIR 에 따로(저장소에는 안 둔다)
const fs = require('fs'), path = require('path'), { execSync } = require('child_process');
const { ROOT, panelIndex, resolveRef, strip } = require('./lesson_lib');
const tpl = fs.readFileSync(path.join(__dirname, 'lesson_player.html'), 'utf8');
const argv = process.argv.slice(2); const si = argv.indexOf('--standalone');
const standaloneDir = si >= 0 ? argv[si + 1] : null;
let ids = si >= 0 ? argv.filter((_, k) => k !== si && k !== si + 1) : argv;
if (!ids.length) ids = fs.readdirSync(path.join(ROOT, 'lessons')).filter(f => /^L\d{2}[a-z]?\.json$/.test(f)).map(f => f.slice(0, -5)).sort();
fs.mkdirSync(path.join(ROOT, 'lesson'), { recursive: true });
const idx = panelIndex();
const SITE = 'https://baeggman.github.io/biology2/';  // GitHub Pages 배포 주소 — 한 파일(standalone)의 바깥 링크에만 쓴다
const firstPanel = L => { for (const s of L.stops) for (const r of (s.src || [])) return r.split('#')[0]; return null; };
for (const id of ids) {
  const L = JSON.parse(fs.readFileSync(path.join(ROOT, 'lessons', id + '.json'), 'utf8'));
  if (L.id !== id) { console.error(`[${id}] json 의 id 가 ${L.id}`); process.exitCode = 1; continue; }
  const bad = [];
  L.stops.forEach((s, k) => {
    if (s.box) for (const [x, y, w, h] of (Array.isArray(s.box[0]) ? s.box : [s.box])) { if (x < 0 || y < 0 || x + w > L.w || y + h > L.h) bad.push(`${k}: 상자가 그림 밖 ${[x, y, w, h]}`); }
    if ((s.fact || '').length > 60) bad.push(`${k}: 사실 ${s.fact.length}자 (> 60)`);
    if (!s.say) bad.push(`${k}: say 없음`);
    s.cards = [];
    for (const r of (s.src || [])) { try { s.cards.push(...(resolveRef(r, idx).row[2] || [])); } catch (e) { bad.push(`${k}: ${e.message}`); } }
    s.cards = [...new Set(s.cards)];
  });
  if (bad.length) { console.error(`[${id}] 검사 실패:\n  ` + bad.join('\n  ')); process.exitCode = 1; continue; }
  L.hubPanel = firstPanel(L);  // 「Sketchy 허브(옛 판)」 링크가 이 과의 첫 옛 판으로 간다
  const html = tpl.replace('__TITLE__', L.title.replace(/[<&]/g, '')).replace('__DATA__', JSON.stringify(L));
  fs.writeFileSync(path.join(ROOT, 'lesson', id + '.html'), html);
  const imgPath = path.join(ROOT, 'lesson', L.img);
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
const idxHtml = `<!DOCTYPE html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>과(lesson) 목록 — 생물 Sketchy</title>
<style>body{margin:0;font-family:-apple-system,"Apple SD Gothic Neo","Noto Sans KR",sans-serif;background:#f7f5ef;color:#1b1b1f}.wrap{max-width:900px;margin:0 auto;padding:16px}
h1{font-size:20px}h2{font-size:15px;margin-top:22px}.sub{color:#4b4b55;font-size:13px}a{color:#0f766e}table{border-collapse:collapse;width:100%;font-size:13px}td,th{border-bottom:1px solid #e3e1da;padding:5px 6px;text-align:left}th{color:#4b4b55;font-weight:600}
.card{display:block;border:1px solid #e3e1da;background:#fff;border-radius:12px;padding:12px 14px;margin:8px 0;text-decoration:none;color:inherit}.card b{color:#0f766e}.bar{height:6px;background:#e3e1da;border-radius:3px;overflow:hidden}.bar i{display:block;height:100%;background:#0f766e}</style></head><body><div class="wrap">
<h1>과(lesson) 목록</h1><p class="sub">Sketchy 식 — 한 장면 · 물건 하나 = 사실 하나 · 투어로 듣고 그림만으로 되찾는다. 옛 덱은 과가 다 설 때까지 그대로 — <a href="../sketchy.html">Sketchy 허브</a>(옛 그림 판 · 판마다 「새 과」 단추) · <a href="../index.html">SRS</a>(기출 카드).</p>
${all.map(L => `<a class="card" href="${L.id}.html"><b>${esc(L.id)}</b> ${esc(L.title)}<div class="sub">정거장 ${L.stops.length} · 기출 카드 ${new Set(L.stops.flatMap(s => (s.src || []).flatMap(r => { try { return resolveRef(r, idx).row[2] || []; } catch (e) { return []; } }))).size} · ${esc(L.sub || '')}</div></a>`).join('')}
<h2>갈아엎기 진척 — 행 ${tot.rc}/${tot.r} · 기출 카드 ${tot.cc}/${tot.c}</h2><div class="bar"><i style="width:${(100 * tot.cc / Math.max(1, tot.c)).toFixed(1)}%"></i></div>
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
