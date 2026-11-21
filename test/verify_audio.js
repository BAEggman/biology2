/* verify_audio.js — 녹음 목록과 상태 글이 사실대로인지(보기 화면 명세 §1.9 · 낭독 명세 §7 · 2026-11-21)
   1. manifest 의 모든 항목: status ready · src 는 https://baeggman.github.io/biology2-audio/<과>_<sid>_v<판>.mp3 · 과 · sid 가 있음
   2. 항목의 text 가 지금 say 와 글자까지 같다 — 다르면 그 녹음은 재생기가 저절로 건너뛰므로, manifest 에서 빼고 검수 기록에 superseded 로 적어야 한다
   3. 항목마다 검수 기록(lesson/audio/reviews/)에 그 파일 이름이 있다 · sha256 이 기록과 같다
   4. heard.json 의 구간은 manifest 에 있다(들은 녹음만 「들어 봄」)
   5. 재생기 상태 글: 받는 동안 「준비 중」 → 「Gemini 녹음 · AI 검수」, heard 에 있으면 「Gemini 녹음 · 들어 봄」 */
const fs = require('fs'), path = require('path'), vm = require('vm');
const ROOT = path.join(__dirname, '..');
let bad = 0; const ok = (c, m) => { console.log(`  ${c ? '✓' : '✕'} ${m}`); if (!c) bad++; };
const M = JSON.parse(fs.readFileSync(path.join(ROOT, 'lesson/audio/manifest.json'), 'utf8'));
const heard = JSON.parse(fs.readFileSync(path.join(ROOT, 'lesson/audio/heard.json'), 'utf8'));
const revDir = path.join(ROOT, 'lesson/audio/reviews');
const revText = fs.readdirSync(revDir).filter(f => f.endsWith('.json')).map(f => fs.readFileSync(path.join(revDir, f), 'utf8')).join('\n');
let n = 0; const p1 = [], p2 = [], p3 = [];
for (const [id, segs] of Object.entries(M.lessons || {})) {
  const f = path.join(ROOT, 'lessons', id + '.json');
  const L = fs.existsSync(f) ? JSON.parse(fs.readFileSync(f, 'utf8')) : null;
  for (const [sid, e] of Object.entries(segs)) {
    n++;
    const st = L && L.stops.find(s => s.sid === sid);
    const re = new RegExp(`^https://baeggman\\.github\\.io/biology2-audio/${id}_${sid}_v\\d+\\.mp3$`);
    if (!L || !st || e.status !== 'ready' || !re.test(e.src || '')) p1.push(`${id} ${sid}`);
    if (st && e.text !== st.say) p2.push(`${id} ${sid}`);
    const base = (e.src || '').split('/').pop().replace(/\.mp3$/, '');
    if (!(e.sha256 && revText.includes(e.sha256)) && !(base && revText.includes(base))) p3.push(`${id} ${sid}`);
  }
}
ok(!p1.length, `manifest ${n} 항목 — ready · 음성 저장소 주소 · 과 · sid${p1.length ? ' — 어긋남: ' + p1.join(' · ') : ''}`);
ok(!p2.length, `text = 지금 say${p2.length ? ' — 다름(빼고 superseded 로 적을 것): ' + p2.join(' · ') : ''}`);
ok(!p3.length, `검수 기록에 그 녹음(sha256 또는 파일 이름)${p3.length ? ' — 없음: ' + p3.join(' · ') : ''}`);
const hbad = [];
for (const [id, sids] of Object.entries(heard)) { if (id.startsWith('_')) continue; for (const sid of sids) if (!M.lessons?.[id]?.[sid]) hbad.push(`${id} ${sid}`); }
ok(!hbad.length, `heard.json 의 구간은 모두 manifest 에 있음${hbad.length ? ' — 없음: ' + hbad.join(' · ') : ''}`);

function sandbox() {
  const log = { status: [] };
  class Audio { constructor() {} play() { return Promise.resolve(); } pause() {} load() {} remove() {} removeAttribute() {} }
  const window = { Audio, SpeechSynthesisUtterance: class {}, speechSynthesis: { speak() {}, cancel() {}, getVoices() { return []; } } };
  const ctx = { window, Audio, URL, setTimeout, clearTimeout, Promise, fetch: () => Promise.reject(new Error('no')), document: { baseURI: 'https://baeggman.github.io/biology2/lesson/L99a.html', body: { appendChild() {} } } };
  vm.createContext(ctx); vm.runInContext(fs.readFileSync(path.join(ROOT, 'lesson/narration-player.js'), 'utf8'), ctx);
  return { N: ctx.window.LessonNarration, log };
}
(async () => {
  const manifest = Promise.resolve({ lessons: { L99a: { s1: { src: 'https://baeggman.github.io/biology2-audio/L99a_s1_v1.mp3', text: '하나', status: 'ready' } } } });
  for (const [h, want] of [[{}, 'Gemini 녹음 · AI 검수'], [{ L99a: ['s1'] }, 'Gemini 녹음 · 들어 봄']]) {
    const { N, log } = sandbox(); const nar = new N('L99a', { manifest, hold: Promise.resolve({}), heard: Promise.resolve(h) });
    await nar.play({ sid: 's1', text: '하나', onend() {}, onblocked() {}, onstatus: s => log.status.push(s) });
    await new Promise(r => setTimeout(r, 5));
    ok(log.status[0] === '준비 중' && log.status[log.status.length - 1] === want, `상태 글 — 「준비 중」 → 「${want}」`); nar.stop();
  }
  console.log(bad ? `\n❌ 녹음 목록 실패 ${bad}` : '\n✅ 녹음 목록 · 상태 글 통과');
  process.exit(bad ? 1 : 0);
})();
