/* verify_lessonui.js — 과 목록 · 과 화면의 보기 기능(보기 화면 명세 §1 · §1.7). jsdom 하나로 돈다.
   ① 별표(목록 · 과 화면) ② 썸네일 · 큰 보기 · order.js · 저장 열쇠
   (③ 반복 재생 · ④ 다음 그림 자동 넘김은 그 기능을 넣을 때 이 파일 아래에 보탠다) */
const fs = require('fs'), path = require('path'), crypto = require('crypto');
const { JSDOM, VirtualConsole } = require('jsdom');
const ROOT = path.join(__dirname, '..');
const LES = path.join(ROOT, 'lesson');
let pass = 0, fail = 0;
const T = async (name, fn) => { try { const m = await fn(); console.log('  ✓', name, m === undefined ? '' : '— ' + m); pass++; } catch (e) { console.log('  ✗', name, '—', e.message); fail++; } };
const eq = (a, b, m) => { if (JSON.stringify(a) !== JSON.stringify(b)) throw new Error((m || '') + ' 기대 ' + JSON.stringify(b) + ' 실제 ' + JSON.stringify(a)); return true; };
const yes = (c, m) => { if (!c) throw new Error(m || '거짓'); return true; };
const tick = (ms = 0) => new Promise(r => setTimeout(r, ms));

function boot(file, { store = {}, brokenStorage = false, url } = {}) {
  let html = fs.readFileSync(path.join(LES, file), 'utf8');
  // 바깥 스크립트(order.js)는 같은 내용을 안에 넣는다 — 파일 주소 해석에 기대지 않는다
  html = html.replace(/<script src="order\.js"><\/script>/, () => '<script>' + fs.readFileSync(path.join(LES, 'order.js'), 'utf8') + '</script>');
  const errs = []; const vc = new VirtualConsole(); vc.on('jsdomError', e => errs.push(e.message.split('\n')[0]));
  const dom = new JSDOM(html, { runScripts: 'dangerously', pretendToBeVisual: true, virtualConsole: vc, url: url || 'https://baeggman.github.io/biology2/lesson/' + file,
    beforeParse(w) {
      if (brokenStorage) Object.defineProperty(w, 'localStorage', { get() { throw new Error('storage blocked'); } });
      else for (const k in store) w.localStorage.setItem(k, store[k]);
    } });
  return { w: dom.window, d: dom.window.document, errs };
}
// ── 과 화면 · 가짜 환경 ────────────────────────────────
// 가상 시계(setTimeout · setInterval · Date.now) · 가짜 fetch(과 쪽 · audio/*.json) · 가짜 Audio · 가짜 기기 음성.
// 틀의 스크립트는 그대로 돌고, 시간만 우리가 흘린다 — 5초 알림 · 0.7초 · 3.5초를 기다리지 않고 잰다.
function bootLesson(id, { store = {}, brokenStorage = false, manifest = { lessons: {} }, hold = {}, heard = {}, speech = 'auto', speakMs = 10, url, now = 1.8e12, noFetchLessons = false, noImgLoad = false, mutate = null } = {}) {
  let html = fs.readFileSync(path.join(LES, id + '.html'), 'utf8');
  html = html.replace(/<script src="narration-player\.js[^"]*"><\/script>/, () => '<script>' + fs.readFileSync(path.join(LES, 'narration-player.js'), 'utf8') + '</script>')
             .replace(/<script src="order\.js"><\/script>/, () => '<script>' + fs.readFileSync(path.join(LES, 'order.js'), 'utf8') + '</script>');
  if (mutate) html = mutate(html);
  const errs = [], vc = new VirtualConsole(); vc.on('jsdomError', e => errs.push(e.message.split('\n')[0]));
  const env = { errs, fetched: [], audios: [], spoken: [], pending: [], q: [], nowMs: 0, seq: 0, nav: [] };
  const dom = new JSDOM(html, { runScripts: 'dangerously', pretendToBeVisual: false, virtualConsole: vc, url: url || 'https://baeggman.github.io/biology2/lesson/' + id + '.html',
    beforeParse(w) {
      if (brokenStorage) Object.defineProperty(w, 'localStorage', { get() { throw new Error('storage blocked'); } });
      else for (const k in store) w.localStorage.setItem(k, store[k]);
      const add = (fn, ms, rep) => { const t = { id: ++env.seq, at: env.nowMs + Math.max(0, +ms || 0), fn, rep: rep ? Math.max(1, +ms || 1) : 0 }; env.q.push(t); return t.id; };
      w.setTimeout = (fn, ms, ...a) => add(() => fn(...a), ms, false);
      w.setInterval = (fn, ms, ...a) => add(() => fn(...a), ms, true);
      w.clearTimeout = w.clearInterval = tid => { env.q = env.q.filter(t => t.id !== tid); };
      const D = w.Date; w.Date = class extends D { constructor(...a) { if (a.length) super(...a); else super(now + env.nowMs); } static now() { return now + env.nowMs; } };
      w.Element.prototype.scrollIntoView = function () {};
      w.__navigate = u => env.nav.push(u);   // 쪽 옮기기를 가로챈다(jsdom 은 실제로 옮기지 못한다)
      w.fetch = async u => {
        const name = String(u).split('?')[0].split('/').slice(-2).join('/'); env.fetched.push(name);
        const json = o => ({ ok: true, json: async () => o, text: async () => JSON.stringify(o) });
        if (name.endsWith('audio/manifest.json')) return json(manifest);
        if (name.endsWith('audio/hold.json')) return json(hold);
        if (name.endsWith('audio/heard.json')) return json(heard);
        const m = /(?:^|\/)(L\d{2}[a-z]?)\.html$/.exec(name);
        if (m && !noFetchLessons && fs.existsSync(path.join(LES, m[1] + '.html'))) { const t = fs.readFileSync(path.join(LES, m[1] + '.html'), 'utf8'); return { ok: true, text: async () => t, json: async () => { throw new Error('html'); } }; }
        return { ok: false, status: 404, json: async () => ({}), text: async () => '' };
      };
      w.Audio = class { constructor(src) { this.src = src; this.paused = true; env.audios.push(this); } play() { this.paused = false; return Promise.resolve(); } pause() { this.paused = true; } load() {} remove() {} removeAttribute() {} };
      w.SpeechSynthesisUtterance = class { constructor(t) { this.text = t; } };
      w.speechSynthesis = { speak(u) { env.spoken.push(u.text); u.__live = true; env.pending.push(u); if (speech === 'auto') w.setTimeout(() => { if (u.__live) { u.onstart && u.onstart(); u.onend && u.onend(); } }, speakMs); },
        cancel() { for (const u of env.pending) u.__live = false; env.pending = []; }, getVoices() { return []; }, onvoiceschanged: null };
      void noImgLoad;
    } });
  const w = dom.window, d = w.document;
  // 시계를 흘린다 — 때가 된 것부터 차례로, 한 걸음마다 약속(microtask)을 비운다
  const flush = () => new Promise(r => setImmediate(r));
  env.tick = async ms => {
    const end = env.nowMs + ms; await flush();
    for (;;) {
      const due = env.q.filter(t => t.at <= end).sort((a, b) => a.at - b.at || a.id - b.id)[0]; if (!due) break;
      env.nowMs = Math.max(env.nowMs, due.at);
      if (due.rep) due.at = env.nowMs + due.rep; else env.q = env.q.filter(t => t !== due);
      due.fn(); await flush();
    }
    env.nowMs = end; await flush();
  };
  env.flush = flush; env.w = w; env.d = d;
  env.imgLoad = () => { d.getElementById('img').dispatchEvent(new w.Event('load')); };
  env.finishSpeech = () => { const u = env.pending.shift(); if (u && u.__live) { u.onstart && u.onstart(); u.onend && u.onend(); } };
  return env;
}
const click = (w, el) => el.dispatchEvent(new w.MouseEvent('click', { bubbles: true, cancelable: true }));
const key = (w, k) => w.document.dispatchEvent(new w.KeyboardEvent('keydown', { key: k, bubbles: true, cancelable: true }));
const stars = w => JSON.parse(w.localStorage.getItem('lesson_stars') || '{}');
const prefs = w => JSON.parse(w.localStorage.getItem('lesson_prefs') || '{}');
const sha12 = f => crypto.createHash('sha256').update(fs.readFileSync(f)).digest('hex').slice(0, 12);

(async () => {
  console.log('\n── ① 별표 · ② 썸네일 — 과 목록 ──');
  const lessons = fs.readdirSync(path.join(ROOT, 'lessons')).filter(f => /^L\d{2}[a-z]?\.json$/.test(f)).map(f => JSON.parse(fs.readFileSync(path.join(ROOT, 'lessons', f), 'utf8')));
  const idxText = fs.readFileSync(path.join(LES, 'index.html'), 'utf8');

  await T('썸네일 원본 해시가 지금 그림과 같다(lesson/thumb/manifest.json · 142장 · 파일 있음)', () => {
    const man = JSON.parse(fs.readFileSync(path.join(LES, 'thumb', 'manifest.json'), 'utf8')), bad = [];
    for (const L of lessons) {
      const f = path.join(LES, 'thumb', L.id + '.webp');
      if (!fs.existsSync(f)) bad.push(L.id + ' 없음'); else if (man[L.id] !== sha12(path.join(LES, L.img))) bad.push(L.id + ' 낡음');
    }
    eq(bad, []); return Object.keys(man).length + '장';
  });

  const A = boot('index.html');
  const rows = [...A.d.querySelectorAll('.row')];
  await T('런타임 오류 0 · 줄 142 (과마다 한 줄)', () => { eq(A.errs, []); eq(rows.length, lessons.length); });
  await T('줄마다 썸네일 · lazy · 폭/높이 · 파일이 있음 / 별표 ☆ / 제목 칸 링크', () => {
    for (const r of rows) {
      const id = r.dataset.id, im = r.querySelector('.thumb img');
      yes(im && im.getAttribute('loading') === 'lazy' && im.getAttribute('width') === '160' && im.getAttribute('height') === '90' && im.getAttribute('decoding') === 'async', id + ' 썸네일 태그');
      yes(fs.existsSync(path.join(LES, im.getAttribute('src').split('?')[0])), id + ' 썸네일 파일');
      yes(/\?v=[0-9a-f]{12}$/.test(im.getAttribute('src')), id + ' 썸네일 ?v=');
      eq([r.querySelector('.star').getAttribute('aria-pressed'), r.querySelector('.star').textContent], ['false', '☆'], id + ' 별표');
      eq(r.querySelector('a.card').getAttribute('href'), id + '.html', id + ' 제목 칸');
      yes(r.querySelector('.thumb').tagName === 'BUTTON' && r.querySelector('.star').tagName === 'BUTTON', id + ' 단추 · 링크 안에 단추 없음');
      yes(!r.querySelector('a button'), id + ' 링크 안의 단추');
    }
  });
  await T('order.js — 모든 과가 꼭 한 번 · 목록의 줄 차례와 같음 · t · u 가 있음', () => {
    const O = A.w.LESSON_ORDER, ids = O.map(o => o.id);
    eq(ids.length, lessons.length); eq(new Set(ids).size, lessons.length); eq(ids, rows.map(r => r.dataset.id));
    yes(O.every(o => o.t && o.u && !o.t.includes(' — ')), 't · u 칸');
    eq(lessons.filter(L => !ids.includes(L.id)).map(L => L.id), []);
  });

  const first = rows[0], second = rows[1], third = rows[2];
  await T('별표를 누르면 aria-pressed · ★ · lesson_stars 가 바뀌고 쪽이 옮겨 가지 않음', () => {
    const href0 = A.w.location.href;
    click(A.w, first.querySelector('.star'));
    eq([first.querySelector('.star').getAttribute('aria-pressed'), first.querySelector('.star').textContent, first.classList.contains('starred')], ['true', '★', true]);
    const s = stars(A.w); eq(Object.keys(s), [first.dataset.id]); yes(typeof s[first.dataset.id] === 'number' && s[first.dataset.id] > 1e12, '찍은 때(ms)');
    eq(A.w.location.href, href0, '쪽이 옮겨 감');
  });
  await T('다시 누르면 지워지고 열쇠도 빠진다(마지막 하나면 lesson_stars 자체가 없어짐)', () => {
    click(A.w, first.querySelector('.star'));
    eq(first.querySelector('.star').getAttribute('aria-pressed'), 'false'); eq(A.w.localStorage.getItem('lesson_stars'), null);
  });
  await T('거르기 — 켜면 별표 없는 줄 · 빈 단원 · 목차 항목이 감춰지고 (n) 이 맞음 · 설정이 lesson_prefs 에 남음', () => {
    click(A.w, second.querySelector('.star')); click(A.w, third.querySelector('.star'));
    eq(A.d.getElementById('fStar').textContent, '★ 표시한 것만 (2)');
    click(A.w, A.d.getElementById('fStar'));
    eq([...A.d.querySelectorAll('.row')].filter(r => !r.hidden).map(r => r.dataset.id), [second.dataset.id, third.dataset.id]);
    eq(A.d.getElementById('fStar').getAttribute('aria-pressed'), 'true'); eq(prefs(A.w).onlyStar, true);
    const chapters = [...A.d.querySelectorAll('.chapter')]; yes(chapters.filter(c => !c.hidden).length >= 1 && chapters.filter(c => c.hidden).length > 10, '빈 단원이 감춰짐');
    yes([...A.d.querySelectorAll('.unit')].some(u => u.hidden), '빈 단원 묶음이 감춰짐');
    const shownToc = [...A.d.querySelectorAll('.toc-group li')].filter(li => !li.hidden).length; yes(shownToc >= 1 && shownToc < 20, '목차 항목 ' + shownToc);
  });
  await T('거르기를 끄면 모두 보임 · 별표는 그대로', () => {
    click(A.w, A.d.getElementById('fStar'));
    eq([...A.d.querySelectorAll('.row')].filter(r => r.hidden).length, 0); eq(prefs(A.w).onlyStar, false); eq(Object.keys(stars(A.w)).length, 2);
    eq([...A.d.querySelectorAll('.chapter, .unit')].filter(e => e.hidden).length, 0);
  });
  await T('저장한 별표 · 거르기가 새로 열어도 되살아남(저장 열쇠 꼴)', () => {
    const B = boot('index.html', { store: { lesson_stars: JSON.stringify({ [rows[5].dataset.id]: 111 }), lesson_prefs: JSON.stringify({ onlyStar: true }) } });
    eq(B.errs, []); eq([...B.d.querySelectorAll('.row')].filter(r => !r.hidden).map(r => r.dataset.id), [rows[5].dataset.id]);
    eq(B.d.getElementById('fStar').textContent, '★ 표시한 것만 (1)');
  });

  console.log('\n── ② 썸네일을 눌러 그 자리에서 크게 ──');
  const dlg = A.d.getElementById('big'), bigTitle = () => A.d.getElementById('bigTitle').textContent;
  await T('썸네일을 누르면 큰 보기가 열림 — 큰 그림은 그때 부름 · 제목 · 공부하기 링크 · 별표 상태', () => {
    eq(A.d.getElementById('bigImg').getAttribute('src'), null, '열기 전에는 큰 그림을 부르지 않음');
    click(A.w, first.querySelector('.thumb'));
    yes(dlg.open, '열림'); eq(A.d.getElementById('bigImg').getAttribute('src'), first.dataset.img); yes(/^img\/L\d{2}[a-z]?\.webp\?v=[0-9a-f]{12}$/.test(first.dataset.img), '큰 그림 주소');
    yes(fs.existsSync(path.join(LES, first.dataset.img.split('?')[0])), '큰 그림 파일');
    eq(bigTitle(), first.dataset.id + ' ' + first.dataset.title); eq(A.d.getElementById('bigGo').getAttribute('href'), first.dataset.id + '.html');
    eq(A.d.getElementById('bigStar').getAttribute('aria-pressed'), 'false'); eq(A.d.getElementById('bigPrev').disabled, true); eq(A.d.getElementById('bigNext').disabled, false);
  });
  await T('요약(sub)은 접혀 있고 「요약 보기」를 눌러야 펼쳐짐', () => {
    eq(A.d.getElementById('bigSub').hidden, true); eq(A.d.getElementById('bigSub').textContent, '');
    click(A.w, A.d.getElementById('bigSubBtn')); eq(A.d.getElementById('bigSub').hidden, false); yes(A.d.getElementById('bigSub').textContent.includes('정거장'), '요약 글');
    click(A.w, A.d.getElementById('bigSubBtn')); eq(A.d.getElementById('bigSub').hidden, true);
  });
  await T('다음 그림 ▶ · ◀ 앞 그림 — 줄 차례 그대로(끝에서는 막힘) · 글쇠 ← → ', () => {
    click(A.w, A.d.getElementById('bigNext')); eq(bigTitle(), second.dataset.id + ' ' + second.dataset.title); eq(A.d.getElementById('bigImg').getAttribute('src'), second.dataset.img);
    key(A.w, 'ArrowRight'); eq(bigTitle().split(' ')[0], third.dataset.id);
    key(A.w, 'ArrowLeft'); eq(bigTitle().split(' ')[0], second.dataset.id);
    click(A.w, A.d.getElementById('bigPrev')); eq(A.d.getElementById('bigPrev').disabled, true);
    key(A.w, 'ArrowLeft'); eq(bigTitle().split(' ')[0], first.dataset.id, '처음에서 더 안 감');
  });
  await T('큰 보기 안의 ☆ — 같은 열쇠 · 목록의 별표도 따라 바뀜', () => {
    click(A.w, A.d.getElementById('bigStar'));
    eq([A.d.getElementById('bigStar').getAttribute('aria-pressed'), first.querySelector('.star').getAttribute('aria-pressed')], ['true', 'true']); eq(Object.keys(stars(A.w)).includes(first.dataset.id), true);
    click(A.w, A.d.getElementById('bigStar')); eq(first.querySelector('.star').getAttribute('aria-pressed'), 'false');
  });
  await T('Esc · 닫기 — 닫히고 큰 그림을 놓음', () => {
    key(A.w, 'Escape'); yes(!dlg.open, 'Esc'); eq(A.d.getElementById('bigImg').getAttribute('src'), null);
    click(A.w, first.querySelector('.thumb')); yes(dlg.open); click(A.w, A.d.getElementById('bigClose')); yes(!dlg.open, '닫기 단추');
    click(A.w, first.querySelector('.thumb')); click(A.w, dlg); yes(!dlg.open, '배경 누름');
  });
  await T('별표 거르기를 켜면 앞뒤 그림이 지금 보이는 줄만 따라감', () => {
    click(A.w, A.d.getElementById('fStar'));   // 별표: second · third
    click(A.w, second.querySelector('.thumb')); eq(A.d.getElementById('bigPrev').disabled, true);
    click(A.w, A.d.getElementById('bigNext')); eq(bigTitle().split(' ')[0], third.dataset.id); eq(A.d.getElementById('bigNext').disabled, true, '거른 목록의 끝');
    click(A.w, A.d.getElementById('bigClose')); click(A.w, A.d.getElementById('fStar'));
  });
  await T('큰 보기에서 별표를 지워도 그 그림은 닫기 전까지 남음(거르기를 켠 채)', () => {
    click(A.w, A.d.getElementById('fStar'));   // 거르기 켬 — second · third 만
    click(A.w, second.querySelector('.thumb')); click(A.w, A.d.getElementById('bigStar'));   // second 별표 지움
    yes(!second.hidden, '열려 있는 그림은 안 사라짐'); click(A.w, A.d.getElementById('bigClose')); yes(second.hidden, '닫으면 거름');
    click(A.w, A.d.getElementById('fStar'));
  });
  await T('다른 탭에서 바뀌면 storage 이벤트로 따라감(별표 · 거르기)', () => {
    const id = rows[9].dataset.id; A.w.localStorage.setItem('lesson_stars', JSON.stringify({ [id]: 1 }));
    A.w.dispatchEvent(new A.w.StorageEvent('storage', { key: 'lesson_stars' }));
    eq(rows[9].querySelector('.star').getAttribute('aria-pressed'), 'true'); eq(A.d.getElementById('fStar').textContent, '★ 표시한 것만 (1)');
  });
  await T('저장이 막힌 브라우저에서도 오류 없이 그 쪽에서는 기억함', () => {
    const B = boot('index.html', { brokenStorage: true }); const r = B.d.querySelector('.row');
    click(B.w, r.querySelector('.star')); eq(r.querySelector('.star').getAttribute('aria-pressed'), 'true');
    click(B.w, B.d.getElementById('fStar')); eq([...B.d.querySelectorAll('.row')].filter(x => !x.hidden).length, 1);
    eq(B.errs, []);
  });
  await T('옛 저장 열쇠에 손대지 않음(lesson_<ID> · lesson_shuffle · lesson_srs_inbox · lesson_auto_start)', () => {
    const old = { lesson_L17e: '{"v":2,"items":{},"sessions":[]}', lesson_shuffle: '1', lesson_srs_inbox: '[]', lesson_auto_start: '0' };
    const B = boot('index.html', { store: old }); const r = B.d.querySelector('.row');
    click(B.w, r.querySelector('.star')); click(B.w, B.d.getElementById('fStar')); click(B.w, r.querySelector('.thumb')); key(B.w, 'ArrowRight');
    for (const k in old) eq(B.w.localStorage.getItem(k), old[k], k);
    eq(Object.keys(B.w.localStorage).filter(k => !(k in old)).sort(), ['lesson_prefs', 'lesson_stars']);
  });

  console.log('\n── ① 별표 — 과 화면 ──');
  await T('과 화면 제목 곁 ☆ — 같은 열쇠 · 목록과 한 몸', () => {
    const P = bootLesson('L17e'); eq(P.errs, []); const b = P.d.getElementById('bStar'), w = P.w;
    eq([b.getAttribute('aria-pressed'), b.textContent], ['false', '☆']);
    click(w, b); eq([b.getAttribute('aria-pressed'), b.textContent], ['true', '★']); eq(Object.keys(stars(w)), ['L17e']);
    const Q = bootLesson('L17e', { store: { lesson_stars: JSON.stringify({ L17e: 5 }) } }); eq(Q.d.getElementById('bStar').getAttribute('aria-pressed'), 'true', '저장된 별표');
    Q.w.localStorage.removeItem('lesson_stars'); Q.w.dispatchEvent(new Q.w.StorageEvent('storage', { key: 'lesson_stars' })); eq(Q.d.getElementById('bStar').textContent, '☆', '다른 탭에서 지움');
    const R = bootLesson('L17e', { brokenStorage: true }); click(R.w, R.d.getElementById('bStar')); eq(R.d.getElementById('bStar').textContent, '★', '저장이 막혀도'); eq(R.errs, []);
  });
  await T('과 화면이 빌드의 모든 142과에서 같은 틀(별표 단추 · 저장 도우미)로 지어짐', () => {
    const bad = lessons.filter(L => { const t = fs.readFileSync(path.join(LES, L.id + '.html'), 'utf8'); return !t.includes('id="bStar"') || !t.includes('const LStore'); }).map(L => L.id);
    eq(bad, []);
  });


  // ═══════════════════════ ③ 반복 재생 ═══════════════════════
  console.log('\n── ③ 반복 재생 ──');
  const idxOf = P => P.w.eval('i'), at = P => P.w.eval('i');
  const N = 13;
  const play = (P) => click(P.w, P.d.getElementById('bPlay'));
  const clickId = (P, id) => click(P.w, P.d.getElementById(id));
  const goTo = (P, k) => { P.w.eval('go(' + k + ')'); };
  const abKey = id => 'lesson_ab_' + id;
  const trace = async (P, ms, step = 100) => { const seen = []; for (let t = 0; t < ms; t += step) { await P.tick(step); const v = at(P); if (seen[seen.length - 1] !== v) seen.push(v); } return seen; };

  await T('🔁 단추 — 꺼짐 → 구간 → 이 그림 → 목록 → 꺼짐 · 눌림 표시 · 설정이 lesson_prefs 에 · 구간 줄은 구간일 때만', async () => {
    const P = bootLesson('L17e'); eq(P.errs, []); const b = P.d.getElementById('bRep'), bar = P.d.getElementById('abBar');
    eq([b.textContent, b.getAttribute('aria-pressed'), bar.hidden], ['🔁 반복 꺼짐', 'false', true]);
    clickId(P, 'bRep'); eq([b.textContent, b.getAttribute('aria-pressed'), bar.hidden, prefs(P.w).rep], ['🔁 구간 반복', 'true', false, 'ab']);
    clickId(P, 'bRep'); eq([b.textContent, bar.hidden, prefs(P.w).rep], ['🔁 이 그림 반복', true, 'one']);
    clickId(P, 'bRep'); eq([b.textContent, bar.hidden, prefs(P.w).rep], ['🔁 목록 반복', true, 'list']);
    clickId(P, 'bRep'); eq([b.textContent, bar.hidden, prefs(P.w).rep], ['🔁 반복 꺼짐', true, 'off']);
    const Q = bootLesson('L17e', { store: { lesson_prefs: JSON.stringify({ rep: 'one' }) } }); eq(Q.d.getElementById('bRep').textContent, '🔁 이 그림 반복', '새로 열어도 기억');
  });

  await T('이 그림 반복 — 끝 정거장 다음에 되짚기가 아니라 처음(1번)으로 돌아가 계속 돎 · 되짚기를 읽지 않음', async () => {
    const P = bootLesson('L17e'); clickId(P, 'bRep'); clickId(P, 'bRep');   // 이 그림
    play(P); const seen = await trace(P, 13 * 800 * 2 + 400);
    yes(seen.filter(v => v === 0).length >= 2, '처음으로 두 번 이상 돌아옴 ' + JSON.stringify(seen));
    yes(seen.includes(N - 1), '끝까지 감'); eq(P.d.getElementById('recap').style.display === 'block', false, '되짚기 칸이 안 열림');
    yes(!P.spoken.some(t => /되짚기/.test(t)), '되짚기 안내를 읽지 않음');
    eq(P.errs, []);
  });

  await T('구간 반복 — 여기부터 · 여기까지가 sid 로 저장되고(lesson_ab_<ID>) 그 안에서만 돎 · 단계 글에 구간이 보임', async () => {
    const P = bootLesson('L17e'); clickId(P, 'bRep');   // 구간
    goTo(P, 2); clickId(P, 'bA'); goTo(P, 4); clickId(P, 'bB');
    eq(JSON.parse(P.w.localStorage.getItem(abKey('L17e'))), { a: 's3', b: 's5' });
    yes(/구간 3 – 5/.test(P.d.getElementById('step').textContent), '단계 글 ' + P.d.getElementById('step').textContent);
    P.w.eval('playing=false'); goTo(P, 2); play(P); const seen = await trace(P, 4200);
    yes(seen.every(v => v >= 2 && v <= 4), '구간 밖으로 안 나감 ' + JSON.stringify(seen));
    yes(seen.filter(v => v === 2).length >= 2 && seen.includes(4), '4 다음에 2 로 돌아옴 ' + JSON.stringify(seen));
    eq(P.d.getElementById('recap').style.display === 'block', false);
  });

  await T('구간 반복 — 구간을 안 정했으면 과 전체를 돌고, 뒤집힌 구간은 서로 비움', async () => {
    const P = bootLesson('L17e'); clickId(P, 'bRep'); play(P); const seen = await trace(P, 13 * 800 + 3 * 800);
    yes(seen.includes(N - 1) && seen.filter(v => v === 0).length >= 2, '전체를 돌고 처음으로 ' + JSON.stringify(seen));
    const Q = bootLesson('L17e'); clickId(Q, 'bRep'); goTo(Q, 6); clickId(Q, 'bA'); goTo(Q, 3); clickId(Q, 'bB');
    eq(JSON.parse(Q.w.localStorage.getItem(abKey('L17e'))), { a: null, b: 's4' }, '끝을 앞에 두면 시작을 비움');
    clickId(Q, 'bAbClr'); eq(Q.w.localStorage.getItem(abKey('L17e')), null, '구간 지움');
  });

  await T('◀ ▶ 로 손으로 넘길 때는 반복하지 않음(구간 끝에서도 그냥 한 칸 더)', async () => {
    const P = bootLesson('L17e'); clickId(P, 'bRep'); goTo(P, 1); clickId(P, 'bA'); goTo(P, 3); clickId(P, 'bB');
    P.w.eval('playing=false'); clickId(P, 'bNext'); eq(at(P), 4, '구간 끝 다음 칸으로 감');
    goTo(P, 1); clickId(P, 'bPrev'); eq(at(P), 0, '구간 앞으로도 감'); clickId(P, 'bRep'); goTo(P, N - 1); clickId(P, 'bNext');
    eq(P.d.getElementById('recap').style.display, 'block', '반복이 꺼지면 맨 끝에서 되짚기');
  });

  await T('▶ 를 누르면 구간 밖에서는 구간의 처음부터, 구간 안이면 그 자리부터', async () => {
    const P = bootLesson('L17e', { speech: 'manual' }); clickId(P, 'bRep'); goTo(P, 4); clickId(P, 'bA'); goTo(P, 6); clickId(P, 'bB');
    goTo(P, 1); play(P); eq(at(P), 4, '구간 앞에서 시작');
    clickId(P, 'bPlay'); goTo(P, 5); play(P); eq(at(P), 5, '구간 안에서는 그 자리');
    clickId(P, 'bPlay'); goTo(P, 9); play(P); eq(at(P), 4, '구간 뒤에서 시작');
    clickId(P, 'bPlay'); P.w.eval('i=-1'); play(P); eq(at(P), 4, '시작 전에는 구간 처음');
  });

  await T('반복을 켠 채 되짚기를 눌러도 소리 내어 읽지 않음(화면에만), 껐을 때는 읽고 읽는 정거장 상자가 밝아짐', async () => {
    const P = bootLesson('L17e', { speech: 'manual' }); clickId(P, 'bRep'); const n0 = P.spoken.length; clickId(P, 'bRecap');
    eq(P.d.getElementById('recap').style.display, 'block'); eq(P.spoken.length, n0, '반복 중 되짚기는 조용함');
    const Q = bootLesson('L17e', { speech: 'manual' }); clickId(Q, 'bRecap'); await Q.tick(0); yes(Q.spoken.length >= 1, '반복이 꺼지면 읽음');
    const bx = k => Q.w.eval('(()=>{const b=stops[' + k + '].box; return b ? (Array.isArray(b[0]) ? b[0][0] : b[0]) : null})()');
    const cur = () => (Q.d.getElementById('ov').innerHTML.match(/class="cur" x="(\d+)"/) || [])[1];
    const k0 = Q.w.eval('stops.findIndex(s => s.box)'); const kn = Q.w.eval('stops.findIndex((s, j) => j > ' + k0 + ' && s.box)');
    for (let k = 0; k < k0; k++) { Q.finishSpeech(); await Q.tick(800); }
    eq(+cur(), bx(k0), '되짚기에서 읽는 칸의 상자가 밝아짐');
    for (let k = k0; k < kn; k++) { Q.finishSpeech(); await Q.tick(800); }
    eq(+cur(), bx(kn), '다음 상자로 옮겨 감');
  });

  await T('복습 · 시험 모드로 바꾸면 반복이 멎고 저절로 넘어가지 않음 / 투어로 돌아와도 멈춘 채', async () => {
    const P = bootLesson('L17e'); clickId(P, 'bRep'); clickId(P, 'bRep'); play(P); await P.tick(1500);
    clickId(P, 'bReview'); eq(P.w.eval('playing'), false); const n = P.spoken.length; await P.tick(5000); eq(P.spoken.length, n, '복습 중에는 읽지 않음');
    clickId(P, 'bQuiz'); await P.tick(5000); eq(P.w.eval('playing'), false);
    clickId(P, 'bTour'); await P.tick(5000); eq(P.w.eval('playing'), false, '투어로 돌아와도 스스로 켜지지 않음'); eq(P.errs, []);
  });

  await T('음성을 끈 채 반복 — 3.5초마다 넘어가며 이 그림 끝에서 처음으로', async () => {
    const P = bootLesson('L17e'); clickId(P, 'bVoice'); clickId(P, 'bRep'); clickId(P, 'bRep');
    goTo(P, N - 2); play(P); P.w.eval('go(' + (N - 2) + ')'); const seen = await trace(P, 3600 * 3, 200);
    yes(seen.includes(N - 1) && seen.includes(0), '끝에서 처음으로 ' + JSON.stringify(seen)); eq(P.spoken.length, 0, '음성이 꺼져 있음');
  });

  await T('연타 — ▶ ◀ ▶ 🔁 를 빠르게 40번 눌러도 동시에 하나만 읽고 번호가 범위를 벗어나지 않음(seq)', async () => {
    const P = bootLesson('L17e'); const ids = ['bPlay', 'bNext', 'bPrev', 'bRep', 'bNext', 'bPlay', 'bPrev', 'bNext'];
    for (let r = 0; r < 40; r++) { clickId(P, ids[(r * 5) % ids.length]); if (r % 7 === 0) await P.tick(30); }
    await P.tick(5000); yes(at(P) >= -1 && at(P) < N, '번호 ' + at(P)); yes(P.pending.length <= 1, '동시에 살아 있는 낭독 ' + P.pending.length); eq(P.errs, []);
    const live = P.audios.filter(a => !a.paused).length; yes(live <= 1, '동시에 재생 중인 녹음 ' + live);
  });

  await T('늦은 완료 — 멈추거나 넘긴 뒤에 옛 낭독이 뒤늦게 끝나도 건너뛰지 않음(alive · settled)', async () => {
    const P = bootLesson('L17e', { speech: 'manual' }); clickId(P, 'bRep'); clickId(P, 'bRep'); play(P); await P.tick(0);
    const old = P.pending[0]; yes(old, '첫 낭독'); eq(at(P), 0);
    clickId(P, 'bNext'); eq(at(P), 1);   // 사람이 넘김 → 옛 낭독은 취소됨
    old.onend && old.onend(); await P.tick(2000); eq(at(P), 1, '옛 낭독의 늦은 완료가 넘기지 못함');
    P.finishSpeech(); await P.tick(800); eq(at(P), 2, '지금 낭독이 끝나면 한 칸');
    clickId(P, 'bPlay'); const cur = P.pending[0]; P.finishSpeech(); await P.tick(3000); eq(at(P), 2, '멈춘 뒤의 완료는 넘기지 못함'); void cur;
    eq(P.errs, []);
  });

  await T('늦은 완료 — 반복 한 바퀴 돌아 처음으로 간 뒤에도 옛(끝 정거장) 낭독의 완료가 처음 칸을 넘기지 않음', async () => {
    const P = bootLesson('L17e', { speech: 'manual' }); clickId(P, 'bRep'); clickId(P, 'bRep'); goTo(P, N - 1); play(P); await P.tick(0);
    const last = P.pending[0]; yes(last, '끝 정거장 낭독'); P.finishSpeech(); await P.tick(800); eq(at(P), 0, '이 그림 반복으로 처음 칸');
    last.onend && last.onend(); last.onend && last.onend(); await P.tick(2500); eq(at(P), 0, '옛 완료를 여러 번 받아도 그대로'); eq(P.errs, []);
  });

  await T('한 시간 지킴이 — 만지지 않고 60분 넘게 반복하면 멈추고 「계속할까요」, ▶ 로 이어 감', async () => {
    const P = bootLesson('L17e'); clickId(P, 'bRep'); clickId(P, 'bRep'); play(P);
    await P.tick(59 * 60 * 1000); eq(P.w.eval('playing'), true, '59분에는 계속');
    await P.tick(3 * 60 * 1000); eq(P.w.eval('playing'), false, '61분에 멈춤'); yes(/계속할까요/.test(P.d.getElementById('audioStatus').textContent), '안내 글');
    const k = at(P); play(P); await P.tick(2500); eq(P.w.eval('playing'), true, '▶ 로 이어 감'); yes(at(P) !== k || true);
  });

  await T('손을 대면 한 시간 지킴이가 새로 잼(키 · 누름)', async () => {
    const P = bootLesson('L17e'); clickId(P, 'bRep'); clickId(P, 'bRep'); play(P);
    for (let m = 0; m < 3; m++) { await P.tick(30 * 60 * 1000); key(P.w, 'Shift'); }
    eq(P.w.eval('playing'), true, '90분이 지나도 만지고 있으니 계속');
  });

  await T('③이 옛 열쇠를 건드리지 않음 · 구간 열쇠는 과마다 따로', async () => {
    const old = { lesson_L17e: '{"v":2,"items":{},"sessions":[]}', lesson_shuffle: '1', lesson_srs_inbox: '[]', lesson_auto_start: '0' };
    const P = bootLesson('L17e', { store: old }); clickId(P, 'bRep'); goTo(P, 3); clickId(P, 'bA'); clickId(P, 'bRep'); clickId(P, 'bRep');
    for (const k in old) eq(P.w.localStorage.getItem(k), old[k], k);
    eq(Object.keys(P.w.localStorage).filter(k => !(k in old)).sort(), ['lesson_ab_L17e', 'lesson_prefs']);
    const Q = bootLesson('L16a', { store: { lesson_prefs: JSON.stringify({ rep: 'ab' }) } }); eq(Q.w.localStorage.getItem(abKey('L16a')), null);
  });

  await T('저장이 막혀도 반복 · 구간이 오류 없이 그 쪽에서 동작', async () => {
    const P = bootLesson('L17e', { brokenStorage: true }); clickId(P, 'bRep'); goTo(P, 2); clickId(P, 'bA'); goTo(P, 4); clickId(P, 'bB'); P.w.eval('playing=false'); goTo(P, 2); play(P);
    const seen = await trace(P, 3200); yes(seen.every(v => v >= 2 && v <= 4), JSON.stringify(seen)); eq(P.errs, []);
  });


  // ═══════════════════ ④ 다음 그림 자동 넘김 ═══════════════════
  console.log('\n── ④ 다음 그림 자동 넘김 ──');
  const ORD = JSON.parse(fs.readFileSync(path.join(LES, 'order.js'), 'utf8').replace(/^\/\*[\s\S]*?\*\/\s*/, '').replace(/^window\.LESSON_ORDER=/, '').replace(/;\s*$/, ''));
  const nextOf = (id, d = 1) => { const k = ORD.findIndex(o => o.id === id); return ORD[k + d] ? ORD[k + d].id : null; };
  const cur = P => P.w.eval('L.id');
  const nStops = id => JSON.parse(fs.readFileSync(path.join(ROOT, 'lessons', id + '.json'), 'utf8')).stops.length;
  const pathId = P => (/\/(L\d{2}[a-z]?)\.html$/.exec(P.w.location.pathname) || [])[1];
  const noteTxt = P => P.d.getElementById('nextNote').hidden ? '' : P.d.getElementById('nextNote').textContent;
  // 끝에서 둘째 정거장부터 자동으로 읽게 해서 끝까지 흘린다
  const toEnd = async (P, ms = 1500) => { const n = P.w.eval('stops.length'); P.w.eval('playing=true'); goTo(P, n - 2); await P.tick(ms); };
  const F = ORD[10].id, F2 = nextOf(F);   // 시험에 쓰는 과와 그 다음 과

  await T('「다음 그림 자동」 단추 — 눌림 · prefs.autoNext · 범위 단추(전체 ↔ ★만) · 앞뒤 그림 링크가 목록 차례대로', () => {
    const P = bootLesson(F); const b = P.d.getElementById('bNextAuto');
    eq([b.hidden, b.textContent, b.getAttribute('aria-pressed')], [false, '다음 그림 자동 꺼짐', 'false']);
    clickId(P, 'bNextAuto'); eq([b.textContent, b.getAttribute('aria-pressed'), prefs(P.w).autoNext], ['다음 그림 자동 켜짐', 'true', true]);
    clickId(P, 'bScope'); eq([P.d.getElementById('bScope').textContent, prefs(P.w).scope], ['범위 ★만', 'star']); clickId(P, 'bScope'); eq(prefs(P.w).scope, 'all');
    eq([P.d.getElementById('navNext').getAttribute('href'), P.d.getElementById('navPrev').getAttribute('href')], [F2 + '.html', nextOf(F, -1) + '.html']);
    const Q = bootLesson(F, { store: { lesson_prefs: JSON.stringify({ autoNext: true, scope: 'star' }) } }); eq([Q.d.getElementById('bNextAuto').textContent, Q.d.getElementById('bScope').textContent], ['다음 그림 자동 켜짐', '범위 ★만'], '새로 열어도 기억');
  });
  await T('목록 맨 앞 과에는 앞 그림 링크가 없고, 맨 뒤 과에는 다음 그림 링크가 없음 · 한 파일(standalone)에는 이어 듣기 단추가 없음', () => {
    const a = bootLesson(ORD[0].id), z = bootLesson(ORD[ORD.length - 1].id);
    eq([a.d.getElementById('navPrev').hidden, a.d.getElementById('navNext').hidden, z.d.getElementById('navNext').hidden, z.d.getElementById('navPrev').hidden], [true, false, true, false]);
    const S = bootLesson(F, { mutate: h => h.replace('/*L' + '0*/{', '/*L' + '0*/{"home":"https://x.example/index.html",') }); eq(S.errs, []);
    eq([S.d.getElementById('bNextAuto').hidden, S.d.getElementById('bScope').hidden, S.d.getElementById('navNext').hidden], [true, true, true]);
    clickId(S, 'bRep'); clickId(S, 'bRep'); clickId(S, 'bRep'); eq(S.d.getElementById('bRep').textContent, '🔁 반복 꺼짐', '목록 반복이 없음(구간 → 이 그림 → 꺼짐)');
  });

  await T('켜 두고 끝까지 읽으면 — 되짚기는 조용히 보이고 5초 알림이 뜸(다음 과 이름 · 지금 넘김 · 취소)', async () => {
    const P = bootLesson(F, { store: { lesson_prefs: JSON.stringify({ autoNext: true }) } }); const n0 = P.spoken.length;
    await toEnd(P); eq(cur(P), F, '아직 같은 과'); eq(P.d.getElementById('recap').style.display, 'block');
    yes(!P.spoken.slice(n0).some(t => /되짚기/.test(t)) && P.spoken.length - n0 <= 3, '되짚기를 읽지 않음 ' + (P.spoken.length - n0));
    const t = noteTxt(P); yes(/5초 뒤 다음 그림/.test(t) && t.includes(F2) && /지금 넘김/.test(t) && /취소/.test(t), '알림 글: ' + t); eq(P.errs, []);
  });
  await T('알림의 초가 줄어들고 5초가 되면 그 자리에서 다음 과로 바뀜(제목 · 그림 · 주소 · 점수 열쇠 · 별표 · 읽기 시작)', async () => {
    const rec = JSON.stringify({ v: 2, items: { s1: [{ t: 1, ok: true, s: 0 }] }, sessions: [] });
    const P = bootLesson(F, { store: { lesson_prefs: JSON.stringify({ autoNext: true }), ['lesson_' + F2]: rec, lesson_stars: JSON.stringify({ [F2]: 9 }) } });
    await toEnd(P); yes(/<b>5<\/b>|5초/.test(noteTxt(P)), '5초에서 시작'); await P.tick(2100); yes(/3초 뒤/.test(noteTxt(P)), '3초: ' + noteTxt(P)); eq(cur(P), F);
    await P.tick(3200);
    eq(cur(P), F2, '과가 바뀜'); eq(P.d.getElementById('title').textContent, P.w.eval('L.title')); eq(P.d.title, P.w.eval('L.title'));
    eq(pathId(P), F2, '주소창'); eq(P.w.eval('scoreKey'), 'lesson_' + F2); eq(P.w.eval('Object.keys(store.items)'), ['s1'], '그 과의 옛 기록을 읽음');
    eq(P.d.getElementById('bStar').textContent, '★', '새 과의 별표'); yes(P.d.getElementById('img').getAttribute('src').includes(F2), '그림이 바뀜');
    eq(at(P), 0, '새 과의 첫 정거장부터 읽기 시작'); eq(P.w.eval('playing'), true); eq(noteTxt(P), '', '알림이 사라짐');
    yes(P.d.getElementById('step').textContent.startsWith('1 / ' + nStops(F2)), '단계 ' + P.d.getElementById('step').textContent);
    eq(P.d.getElementById('bNextAuto').textContent, '다음 그림 자동 켜짐', '켜 둔 채 이어짐'); eq(P.errs, []);
  });
  await T('「지금 넘김」 — 기다리지 않고 바로 바꿈', async () => {
    const P = bootLesson(F, { store: { lesson_prefs: JSON.stringify({ autoNext: true }) } }); await toEnd(P);
    click(P.w, P.d.querySelector('#nextNote [data-cd="now"]')); await P.tick(50); eq(cur(P), F2); eq(at(P), 0);
  });
  await T('「취소」 — 이번 한 번만: 그 과에 머물고 단추는 켜진 채, 안내 글이 남음', async () => {
    const P = bootLesson(F, { store: { lesson_prefs: JSON.stringify({ autoNext: true }) } }); await toEnd(P);
    click(P.w, P.d.querySelector('#nextNote [data-cd="cancel"]')); await P.tick(20000);
    eq(cur(P), F); eq(P.d.getElementById('bNextAuto').getAttribute('aria-pressed'), 'true'); eq(prefs(P.w).autoNext, true); yes(/취소했다/.test(noteTxt(P)), noteTxt(P));
    eq(P.w.eval('playing'), false);
  });
  await T('알림 중에 ◀ · ▶ · ❚❚(시작) · 모드 바꾸기 · 단추 끄기를 하면 알림이 거두어지고 넘어가지 않음', async () => {
    const acts = { '◀': P => clickId(P, 'bPrev'), '▶ 다음': P => clickId(P, 'bNext'), '시작/멈춤': P => clickId(P, 'bPlay'), '복습': P => clickId(P, 'bReview'), '시험': P => clickId(P, 'bQuiz'), '자동 끄기': P => clickId(P, 'bNextAuto'), '앞 그림 링크': P => clickId(P, 'navPrev') };
    for (const [name, act] of Object.entries(acts)) {
      const P = bootLesson(F, { store: { lesson_prefs: JSON.stringify({ autoNext: true }) } }); await toEnd(P); yes(noteTxt(P), name + ' 알림이 떠 있어야'); const before = cur(P);
      act(P); await P.tick(100); if (name === '앞 그림 링크') { await P.tick(50); eq(cur(P), nextOf(F, -1), name + ' — 앞 과로 감'); continue; }
      yes(!/뒤 다음 그림/.test(noteTxt(P)), name + ' 알림이 남음: ' + noteTxt(P)); await P.tick(8000); yes(cur(P) === before || name === '시작/멈춤', name + ' 과가 넘어감 ' + cur(P));
    }
  });
  await T('자동이 꺼져 있으면 끝에서 되짚기를 읽고 알림 없이 멈춤(옛 동작 그대로)', async () => {
    const P = bootLesson(F); const n0 = P.spoken.length; await toEnd(P, 2500); eq(noteTxt(P), ''); await P.tick(10000); eq(cur(P), F);
    yes(P.spoken.length - n0 > 3, '되짚기를 읽음 ' + (P.spoken.length - n0));
  });
  await T('목록 반복 — 자동 단추가 꺼져 있어도 이어 가고, 목록 맨 끝에서는 맨 앞 과로 한 바퀴', async () => {
    const LAST = ORD[ORD.length - 1].id, P = bootLesson(LAST, { store: { lesson_prefs: JSON.stringify({ rep: 'list' }) } }); await toEnd(P);
    yes(noteTxt(P).includes(ORD[0].id), '맨 앞 과로: ' + noteTxt(P)); await P.tick(5200); eq(cur(P), ORD[0].id);
    const Q = bootLesson(F, { store: { lesson_prefs: JSON.stringify({ rep: 'list' }) } }); await toEnd(Q); await P.tick(0); yes(Q.d.getElementById('nextNote').textContent.includes(F2));
  });
  await T('목록 끝에서 목록 반복이 아니면 「목록의 끝」 — 알림 없이 조용히 멈춤', async () => {
    const LAST = ORD[ORD.length - 1].id, P = bootLesson(LAST, { store: { lesson_prefs: JSON.stringify({ autoNext: true }) } }); await toEnd(P);
    yes(/목록의 끝/.test(noteTxt(P)), noteTxt(P)); yes(!P.d.querySelector('#nextNote [data-cd]'), '단추 없음'); await P.tick(9000); eq(cur(P), LAST);
  });
  await T('★만 이어 듣기 — ★ 없는 과는 건너뜀 · 앞뒤 그림 링크도 같은 범위 · 마지막 ★ 다음은 「끝」', async () => {
    const id = [ORD[10].id, ORD[13].id, ORD[15].id], st = { lesson_stars: JSON.stringify({ [id[0]]: 1, [id[1]]: 2, [id[2]]: 3 }), lesson_prefs: JSON.stringify({ autoNext: true, scope: 'star' }) };
    const P = bootLesson(id[0], { store: st }); eq(P.d.getElementById('navNext').getAttribute('href'), id[1] + '.html'); eq(P.d.getElementById('navPrev').hidden, true, '앞쪽에 ★ 없음');
    await toEnd(P); yes(noteTxt(P).includes(id[1]), noteTxt(P)); await P.tick(5200); eq(cur(P), id[1]);
    const Z = bootLesson(id[2], { store: st }); await toEnd(Z); yes(/★ 표시한 그림의 끝/.test(noteTxt(Z)), noteTxt(Z));
  });
  await T('음성을 끈 채로도 이어 감(3.5초 간격) — 알림 뒤 새 과도 음성 없이 읽는 척 넘어감', async () => {
    const P = bootLesson(F, { store: { lesson_prefs: JSON.stringify({ autoNext: true }) } }); clickId(P, 'bVoice'); P.w.eval('playing=true'); goTo(P, P.w.eval('stops.length') - 2);
    await P.tick(3600 * 2 + 200); yes(noteTxt(P), '알림이 뜸'); await P.tick(5200); eq(cur(P), F2); eq(P.spoken.length, 0);
  });
  await T('빠른 연타 — 다음 그림 ▶ 직후 앞 그림 ◀ 를 눌러도 나중에 누른 쪽만 남음(swapSeq)', async () => {
    const P = bootLesson(F); clickId(P, 'navNext'); clickId(P, 'navPrev'); await P.tick(100); eq(cur(P), nextOf(F, -1)); eq(pathId(P) || 'x', nextOf(F, -1)); eq(P.errs, []);
    const Q = bootLesson(F); for (let r = 0; r < 12; r++) clickId(Q, r % 2 ? 'navPrev' : 'navNext'); await Q.tick(200); yes([F2, nextOf(F, -1)].includes(cur(Q)), '마지막 눌림 쪽'); eq(cur(Q), nextOf(F, -1)); eq(Q.errs, []);
  });
  await T('늦은 완료 — 과가 바뀐 뒤 옛 과의 낭독이 뒤늦게 끝나도 새 과가 넘어가지 않음', async () => {
    const P = bootLesson(F, { speech: 'manual' }); clickId(P, 'bPlay'); await P.tick(0); const old = P.pending[0]; yes(old, '옛 과 낭독');
    clickId(P, 'navNext'); await P.tick(50); eq(cur(P), F2); const n1 = P.spoken.length; old.onend && old.onend(); old.onend && old.onend(); await P.tick(1500);   // (기기 음성이 3초 안에 시작하지 않으면 막힌 것으로 본다 — 그 전에 확인)
    eq(at(P), 0, '옛 완료가 새 과를 건드리지 않음(재생 중이었으니 새 과의 첫 정거장에서 기다림)'); eq(P.spoken.length, n1, '새로 읽기 시작한 것이 없음'); eq(P.errs, []);
    P.finishSpeech(); await P.tick(800); eq(at(P), 1, '새 과의 낭독이 끝나야 넘어감');
  });
  await T('늦은 완료 — 받아 오는 중에 바뀐 과의 답이 늦게 와도 버림', async () => {
    const P = bootLesson(F); let release; const gate = new Promise(r => { release = r; }); const orig = P.w.fetch;
    P.w.fetch = async u => { if (String(u).includes(F2 + '.html')) await gate; return orig(u); };
    clickId(P, 'navNext'); await P.tick(10); clickId(P, 'navPrev'); await P.tick(50); eq(cur(P), nextOf(F, -1)); release(); await P.tick(100); eq(cur(P), nextOf(F, -1), '늦게 온 다음 과를 버림'); eq(pathId(P), nextOf(F, -1));
  });
  await T('받아 오기에 실패하면 예전처럼 쪽을 옮김(#auto) — 오류 없이', async () => {
    const P = bootLesson(F, { noFetchLessons: true, store: { lesson_prefs: JSON.stringify({ autoNext: true }) } }); await toEnd(P); await P.tick(5200);
    eq(P.nav, [F2 + '.html#auto']); eq(cur(P), F); eq(P.errs, []);
    clickId(P, 'navNext'); await P.tick(50); eq(P.nav[1], F2 + '.html', '손으로 누르면 #auto 없이');
  });
  await T('뒤로 가기(popstate) — 바꿔 끼운 쪽 사이를 오감', async () => {
    const P = bootLesson(F); clickId(P, 'navNext'); await P.tick(50); eq(cur(P), F2);
    P.w.history.pushState({}, '', F + '.html'); P.w.dispatchEvent(new P.w.PopStateEvent('popstate')); await P.tick(50); eq(cur(P), F, '뒤로'); eq(P.w.eval('playing'), false);
  });
  await T('#auto 로 열리면 자동 시작이 꺼져 있어도 읽기 시작 / 없으면 옛 동작', async () => {
    const A1 = bootLesson(F, { url: 'https://baeggman.github.io/biology2/lesson/' + F + '.html#auto', store: { lesson_auto_start: '0' } }); A1.imgLoad(); await A1.tick(50); eq(A1.w.eval('playing'), true); eq(at(A1), 0);
    const A2 = bootLesson(F, { store: { lesson_auto_start: '0' } }); A2.imgLoad(); await A2.tick(50); eq(A2.w.eval('playing'), false);
    const A3 = bootLesson(F); A3.imgLoad(); await A3.tick(50); eq(A3.w.eval('playing'), true, '자동 시작 켜짐이 기본');
  });
  await T('한 시간 지킴이가 이어 듣기에도 걸림 — 만지지 않은 지 한 시간이 넘으면 다음 그림으로 안 넘어감', async () => {
    const P = bootLesson(F, { store: { lesson_prefs: JSON.stringify({ autoNext: true }) } }); P.w.eval('lastTouch = Date.now() - 3700000'); P.w.eval('playing=true'); goTo(P, 0); await P.tick(2000);
    eq(P.w.eval('playing'), false); yes(/계속할까요/.test(P.d.getElementById('audioStatus').textContent));
  });
  await T('목록의 「처음부터 / ★만 이어 듣기」 — 설정을 켜고 첫 과(#auto)로 감 · ★ 없으면 ★만은 눌리지 않음', () => {
    const B = boot('index.html'); let got = []; B.w.__navigate = u => got.push(u);
    eq(B.d.getElementById('chainStar').disabled, true);
    click(B.w, B.d.getElementById('chainAll')); eq(got, [ORD[0].id + '.html#auto']); eq([prefs(B.w).autoNext, prefs(B.w).scope], [true, 'all']);
    click(B.w, B.d.querySelectorAll('.row')[7].querySelector('.star')); eq(B.d.getElementById('chainStar').disabled, false);
    click(B.w, B.d.getElementById('chainStar')); eq(got[1], ORD[7].id + '.html#auto'); eq([prefs(B.w).autoNext, prefs(B.w).scope], [true, 'star']);
  });
  await T('이어 듣기가 옛 저장 열쇠를 건드리지 않음 · 새 열쇠는 lesson_prefs · lesson_stars · lesson_ab_<ID> · 점수 열쇠만', async () => {
    const old = { lesson_shuffle: '1', lesson_srs_inbox: '[]', lesson_auto_start: '1' };
    const P = bootLesson(F, { store: { ...old, lesson_prefs: JSON.stringify({ autoNext: true }) } }); await toEnd(P); await P.tick(5200);
    for (const k in old) eq(P.w.localStorage.getItem(k), old[k], k);
    eq(Object.keys(P.w.localStorage).filter(k => !(k in old)).sort(), ['lesson_prefs']);
  });
  await T('142과 모두 새 틀 — 이어 듣기 단추 · 알림 칸 · 앞뒤 링크 · 표지가 한 번씩 있음', () => {
    const bad = lessons.filter(L => { const t = fs.readFileSync(path.join(LES, L.id + '.html'), 'utf8'); return !(['id="bNextAuto"', 'id="nextNote"', 'id="navNext"', '<script src="order.js"></script>'].every(x => t.includes(x)) && t.split('/*L' + '0*/').length === 2 && t.split('/*L' + '1*/').length === 2); }).map(L => L.id);
    eq(bad, []);
  });

  console.log('\n' + (fail ? '❌' : '✅') + ' 보기 화면 통과 ' + pass + ' / 실패 ' + fail);
  process.exit(fail ? 1 : 0);
})();
