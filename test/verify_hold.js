/* verify_hold.js — 검수 보류(lesson/audio/hold.json)가 대장과 같고, 재생기가 보류 구간을 스스로 읽지 않는지(2026-11-21 · 보기 화면 명세 §1.9 의 2)
   1. tools/audio/mkhold.py --check — hold.json 이 대장(issues.json)에서 만든 것과 같다
   2. lesson/narration-player.js 를 가짜 창에 올려 —
      보류 + 자동(투어 · 되짚기): 녹음도 기기 음성도 없이 「검수 보류」 상태 → 잠시 뒤 다음
      보류 + 손으로: 녹음을 건너뛰고 기기 음성만 · 상태 「기기 음성 · 검수 보류」
      보류 아님 + manifest ready · 글 같음: 녹음을 튼다
      보류 대기 중 멈춤: 다음으로 넘어가지 않는다 */
const fs = require('fs'), path = require('path'), vm = require('vm'), { execFileSync } = require('child_process');
const ROOT = path.join(__dirname, '..');
let bad = 0; const ok = (c, m) => { console.log(`  ${c ? '✓' : '✕'} ${m}`); if (!c) bad++; };
try { console.log('  ' + execFileSync('python3', [path.join(ROOT, 'tools/audio/mkhold.py'), '--check'], { encoding: 'utf8' }).trim()); }
catch (e) { console.log('  ' + String(e.stdout || e.message).trim()); bad++; }

function sandbox() {
  const log = { audio: 0, speak: [], status: [] };
  class Audio { constructor(src) { log.audio++; this.src = src; } play() { return Promise.resolve(); } pause() {} load() {} remove() {} removeAttribute() {} }
  class SpeechSynthesisUtterance { constructor(t) { this.text = t; } }
  const speechSynthesis = { speak(u) { log.speak.push(u.text); setTimeout(() => { u.onstart && u.onstart(); u.onend && u.onend(); }, 0); }, cancel() {}, getVoices() { return []; } };
  const window = { Audio, SpeechSynthesisUtterance, speechSynthesis };
  const ctx = { window, Audio, URL, setTimeout, clearTimeout, Promise, fetch: () => Promise.reject(new Error('no fetch')),
    document: { baseURI: 'https://baeggman.github.io/biology2/lesson/L99a.html', body: { appendChild() {} } } };
  vm.createContext(ctx);
  vm.runInContext(fs.readFileSync(path.join(ROOT, 'lesson/narration-player.js'), 'utf8'), ctx);
  return { N: ctx.window.LessonNarration, log };
}
const wait = ms => new Promise(r => setTimeout(r, ms));
(async () => {
  const manifest = Promise.resolve({ lessons: { L99a: { s1: { src: 'https://baeggman.github.io/biology2-audio/L99a_s1_v1.mp3', text: '하나', status: 'ready' },
                                                         s2: { src: 'https://baeggman.github.io/biology2-audio/L99a_s2_v1.mp3', text: '둘', status: 'ready' } } } });
  const hold = Promise.resolve({ _뜻: 'x', L99a: { s1: 'T-01' } });
  { const { N, log } = sandbox(); const n = new N('L99a', { manifest, hold, holdDelay: 20 }); let ended = 0;
    await n.play({ sid: 's1', text: '하나', auto: true, onend: () => ended++, onblocked() {}, onstatus: s => log.status.push(s) });
    await wait(60);
    ok(log.audio === 0 && log.speak.length === 0, '보류 + 자동 — 녹음 · 기기 음성 모두 안 함');
    ok(log.status[0] === '검수 보류 — 내용 확인 중' && ended === 1, '보류 + 자동 — 「검수 보류」 상태 뒤 한 번 넘어감'); }
  { const { N, log } = sandbox(); const n = new N('L99a', { manifest, hold, holdDelay: 20 }); let ended = 0;
    await n.play({ sid: 's1', text: '하나', auto: false, onend: () => ended++, onblocked() {}, onstatus: s => log.status.push(s) });
    await wait(30);
    ok(log.audio === 0 && log.speak.length === 1, '보류 + 손으로 — 녹음은 건너뛰고 기기 음성만');
    ok(log.status[0] === '기기 음성 · 검수 보류', '보류 + 손으로 — 상태 「기기 음성 · 검수 보류」'); }
  { const { N, log } = sandbox(); const n = new N('L99a', { manifest, hold, holdDelay: 20 });
    await n.play({ sid: 's2', text: '둘', auto: true, onend() {}, onblocked() {}, onstatus: s => log.status.push(s) });
    ok(log.audio === 1 && log.status[0] === 'Gemini 녹음', '보류 아님 · 글 같음 — 녹음을 튼다'); n.stop(); }
  { const { N, log } = sandbox(); const n = new N('L99a', { manifest, hold, holdDelay: 30 }); let ended = 0;
    await n.play({ sid: 's1', text: '하나', auto: true, onend: () => ended++, onblocked() {}, onstatus: s => log.status.push(s) });
    n.stop(); await wait(60);
    ok(ended === 0, '보류 대기 중 멈춤 — 넘어가지 않음'); }
  { const { N, log } = sandbox(); const n = new N('L99a', { manifest, hold: Promise.resolve({}), holdDelay: 20 });
    await n.play({ sid: 's1', text: '하나 바뀜', auto: true, onend() {}, onblocked() {}, onstatus: s => log.status.push(s) });
    await wait(20);
    ok(log.audio === 0 && log.speak.length === 1, '글이 바뀐 녹음은 틀지 않음(옛 규칙 그대로)'); n.stop(); }
  console.log(bad ? `\n❌ 검수 보류 실패 ${bad}` : '\n✅ 검수 보류 통과');
  process.exit(bad ? 1 : 0);
})();
