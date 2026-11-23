/* lesson_index_ui.js — 과 목록(lesson/index.html)의 별표 · 썸네일 큰 보기 · 거르기(보기 화면 명세 §1.2 · §1.3).
   빌드(build_lesson.js)가 목록 쪽에 끼워 넣는다(LStore 는 lesson_store.js). 바깥 라이브러리 없음. */
(() => {
  const $ = (s, r = document) => r.querySelector(s), $$ = (s, r = document) => Array.from(r.querySelectorAll(s));
  const rows = () => $$('.row');
  const rowOf = id => rows().find(r => r.dataset.id === id) || null;

  // ── 별표 ───────────────────────────────────────────
  function paintStarBtn(btn, on) {
    btn.setAttribute('aria-pressed', String(on)); btn.textContent = on ? '★' : '☆';
    btn.setAttribute('aria-label', on ? '중요 표시 지우기' : '중요 표시');
  }
  function paintRow(row) { const on = LStore.isStar(row.dataset.id); row.classList.toggle('starred', on); paintStarBtn($('.star', row), on); }

  // 거르기 — 켜면 별표 없는 줄을 감추고, 줄이 하나도 안 남은 단원은 통째로 감춘다(목차의 그 항목도)
  function applyFilter() {
    const only = LStore.prefs().onlyStar, keep = row => !only || LStore.isStar(row.dataset.id) || (bigRow === row && dlg.open);
    rows().forEach(r => { r.hidden = !keep(r); });
    $$('.chapter').forEach(ch => { ch.hidden = !$$('.row', ch).some(r => !r.hidden); });
    $$('.unit').forEach(u => { u.hidden = !$$('.chapter', u).some(c => !c.hidden); });
    $$('.toc-group a').forEach(a => { const ch = document.getElementById(a.getAttribute('href').slice(1)); const sec = ch && ch.closest('.chapter'); a.parentNode.hidden = !!(sec && sec.hidden); });
    $$('.toc-group').forEach(g => { g.hidden = !$$('li', g).some(li => !li.hidden); });
    const n = rows().filter(r => LStore.isStar(r.dataset.id)).length, f = $('#fStar');
    f.textContent = '★ 표시한 것만 (' + n + ')'; f.setAttribute('aria-pressed', String(only)); f.classList.toggle('on', only);
    $('#chainStar').disabled = n === 0;
  }
  function setStar(id, on) { LStore.setStar(id, on); const r = rowOf(id); if (r) paintRow(r); if (bigRow && bigRow.dataset.id === id) paintStarBtn($('#bigStar'), on); applyFilter(); if (bigRow) bigButtons(); }
  document.addEventListener('click', e => {
    const b = e.target.closest && e.target.closest('.row .star'); if (!b) return;
    e.preventDefault(); const id = b.closest('.row').dataset.id; setStar(id, !LStore.isStar(id));
  });
  $('#fStar').addEventListener('click', () => { LStore.setPrefs({ onlyStar: !LStore.prefs().onlyStar }); applyFilter(); });

  // ── 큰 보기(그 자리에서) ───────────────────────────
  const dlg = $('#big'), canModal = typeof dlg.showModal === 'function';
  let bigRow = null, subOpen = false;
  const shown = () => rows().filter(r => !r.hidden || r === bigRow);
  function bigButtons() {
    const list = shown(), at = list.indexOf(bigRow);
    $('#bigPrev').disabled = at <= 0; $('#bigNext').disabled = at < 0 || at >= list.length - 1;
  }
  function showBig(row) {
    bigRow = row; const id = row.dataset.id;
    $('#bigTitle').textContent = id + ' ' + row.dataset.title;
    const img = $('#bigImg'); img.alt = id + ' ' + row.dataset.title; img.src = row.dataset.img || '';   // 큰 그림은 열 때 부른다
    $('#bigGo').href = id + '.html';
    paintStarBtn($('#bigStar'), LStore.isStar(id));
    subOpen = false; $('#bigSub').hidden = true; $('#bigSub').textContent = ''; $('#bigSubBtn').textContent = '요약 보기'; $('#bigSubBtn').setAttribute('aria-expanded', 'false');
    bigButtons();
  }
  function openBig(row) {
    showBig(row);
    if (!dlg.open) { if (canModal) dlg.showModal(); else { dlg.classList.add('fb'); dlg.setAttribute('open', ''); } }
    $('#bigClose').focus();
  }
  function closeBig() {
    if (!dlg.open) return;
    const row = bigRow;
    if (canModal && typeof dlg.close === 'function') dlg.close(); else dlg.removeAttribute('open');
    bigRow = null; $('#bigImg').removeAttribute('src');   // 닫으면 큰 그림을 놓는다
    applyFilter();
    const t = row && $('.thumb', row); if (t) t.focus();
  }
  function step(d) {
    if (!bigRow) return; const list = shown(), at = list.indexOf(bigRow), nx = list[at + d]; if (nx) showBig(nx);
  }
  document.addEventListener('click', e => {
    const t = e.target.closest && e.target.closest('.row .thumb'); if (!t) return; e.preventDefault(); openBig(t.closest('.row'));
  });
  $('#bigClose').addEventListener('click', closeBig);
  $('#bigPrev').addEventListener('click', () => step(-1));
  $('#bigNext').addEventListener('click', () => step(1));
  $('#bigStar').addEventListener('click', () => { if (bigRow) setStar(bigRow.dataset.id, !LStore.isStar(bigRow.dataset.id)); });
  $('#bigSubBtn').addEventListener('click', () => {
    if (!bigRow) return; subOpen = !subOpen;
    const sub = $('.card .sub', bigRow); $('#bigSub').textContent = subOpen && sub ? sub.textContent : '';
    $('#bigSub').hidden = !subOpen; $('#bigSubBtn').textContent = subOpen ? '요약 접기' : '요약 보기'; $('#bigSubBtn').setAttribute('aria-expanded', String(subOpen));
  });
  dlg.addEventListener('click', e => { if (e.target === dlg) closeBig(); });                 // 바깥(배경)을 누르면 닫힘
  dlg.addEventListener('close', () => { if (bigRow) { bigRow = null; applyFilter(); } });     // 기본 Esc 로 닫혔을 때
  document.addEventListener('keydown', e => {
    if (!dlg.open) return;
    if (e.key === 'ArrowLeft') { e.preventDefault(); step(-1); }
    else if (e.key === 'ArrowRight') { e.preventDefault(); step(1); }
    else if (e.key === 'Escape') { e.preventDefault(); closeBig(); }
  });

  // 다른 탭에서 바뀌면 따라간다
  window.addEventListener('storage', e => { if (e.key === null || e.key === 'lesson_stars' || e.key === 'lesson_prefs') { rows().forEach(paintRow); if (bigRow) paintStarBtn($('#bigStar'), LStore.isStar(bigRow.dataset.id)); applyFilter(); } });

  // 이어 듣기 — 첫 그림으로 가서 「다음 그림 자동」을 켠다(범위만 다르게). 과 화면이 #auto 로 열리면 곧장 읽기 시작한다.
  function chain(scope) {
    const first = (window.LESSON_ORDER || []).find(o => scope !== 'star' || LStore.isStar(o.id)); if (!first) return;
    LStore.setPrefs({ autoNext: true, scope });
    const url = first.id + '.html#auto'; if (window.__navigate) window.__navigate(url); else location.href = url;
  }
  $('#chainAll').addEventListener('click', () => chain('all'));
  $('#chainStar').addEventListener('click', () => chain('star'));

  rows().forEach(paintRow); applyFilter();
})();
