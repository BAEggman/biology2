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
function bootLesson(id, { store = {}, brokenStorage = false, manifest = { lessons: {} }, hold = {}, heard = {}, speech = 'auto', speakMs = 10, url, now = 1.8e12, noFetchLessons = false, noImgLoad = false } = {}) {
  let html = fs.readFileSync(path.join(LES, id + '.html'), 'utf8');
  html = html.replace(/<script src="narration-player\.js[^"]*"><\/script>/, () => '<script>' + fs.readFileSync(path.join(LES, 'narration-player.js'), 'utf8') + '</script>')
             .replace(/<script src="order\.js"><\/script>/, () => '<script>' + fs.readFileSync(path.join(LES, 'order.js'), 'utf8') + '</script>');
  const errs = [], vc = new VirtualConsole(); vc.on('jsdomError', e => errs.push(e.message.split('\n')[0]));
  const env = { errs, fetched: [], audios: [], spoken: [], pending: [], q: [], nowMs: 0, seq: 0 };
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

  console.log('\n' + (fail ? '❌' : '✅') + ' 보기 화면 통과 ' + pass + ' / 실패 ' + fail);
  process.exit(fail ? 1 : 0);
})();
