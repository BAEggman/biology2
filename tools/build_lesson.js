#!/usr/bin/env node
// build_lesson.js — lessons/<ID>.json + tools/lesson_player.html → lesson/<ID>.html (자급자족 한 파일 · 그림은 ../img/<ID>.webp)
// 사용: node tools/build_lesson.js L31 [L32 …]   (인자 없으면 lessons/*.json 전부)
const fs = require('fs'), path = require('path');
const root = path.join(__dirname, '..');
const tpl = fs.readFileSync(path.join(__dirname, 'lesson_player.html'), 'utf8');
const argv = process.argv.slice(2); const si0 = argv.indexOf('--standalone');
let ids = si0 >= 0 ? argv.filter((_, k) => k !== si0 && k !== si0 + 1) : argv;
if (!ids.length) ids = fs.readdirSync(path.join(root, 'lessons')).filter(f => f.endsWith('.json')).map(f => f.slice(0, -5));
fs.mkdirSync(path.join(root, 'lesson'), { recursive: true });
for (const id of ids) {
  const L = JSON.parse(fs.readFileSync(path.join(root, 'lessons', id + '.json'), 'utf8'));
  // 검사: 상자는 그림 안 · 사실 칸은 짧게(Sketchy: 물건 하나 = 사실 하나)
  const bad = [];
  L.stops.forEach((s, k) => {
    if (s.box) { const [x, y, w, h] = s.box; if (x < 0 || y < 0 || x + w > L.w || y + h > L.h) bad.push(`${k}: 상자가 그림 밖 ${s.box}`); }
    if ((s.fact || '').length > 60) bad.push(`${k}: 사실 ${s.fact.length}자 (> 60)`);
    if (!s.say) bad.push(`${k}: say 없음`);
  });
  if (bad.length) { console.error(`[${id}] 검사 실패:\n  ` + bad.join('\n  ')); process.exitCode = 1; continue; }
  const html = tpl.replace('__TITLE__', L.title.replace(/[<&]/g, '')).replace('__DATA__', JSON.stringify(L));
  fs.writeFileSync(path.join(root, 'lesson', id + '.html'), html);
  const imgPath = path.join(root, "lesson", L.img);
  console.log(`[${id}] lesson/${id}.html · 정거장 ${L.stops.length} · 그림 ${fs.existsSync(imgPath) ? 'ok' : '없음: ' + L.img}`);
  // --standalone DIR : 그림을 data: URI 로 안에 넣은 한 파일(아무 데서나 두 번 눌러 열기 · 저장소에는 안 둔다)
  const si = process.argv.indexOf('--standalone');
  if (si > 0 && fs.existsSync(imgPath)) {
    const ext = path.extname(imgPath).slice(1); const b64 = fs.readFileSync(imgPath).toString('base64');
    const L2 = Object.assign({}, L, { img: `data:image/${ext};base64,${b64}` });
    const out = path.join(process.argv[si + 1], `${id}_standalone.html`);
    fs.writeFileSync(out, tpl.replace('__TITLE__', L.title.replace(/[<&]/g, '')).replace('__DATA__', JSON.stringify(L2)));
    console.log(`  standalone → ${out} (${Math.round(fs.statSync(out).size / 1024)} KB)`);
  }
}
