// gem_helpers2.js — Gemini(3.1 Pro) 조각 편집 자동화 도우미 (2026-10-25 재작성 · javascript_tool 로 실행)
// __prep() 새 채팅 + Pro 확인 + 업로드 메뉴 → find 'input type=file' → file_upload → __go(P) → __wait(ms, want) → __poll(name) → device_stage_files ~/Downloads/<name>_<ts>.png
window.__w = ms => new Promise(r => setTimeout(r, ms));
window.__PFX = "This is a cropped piece of a wide picture. Keep the framing, scale, every existing object and the drawing style exactly; do not redraw, only add what is listed. ";
window.__ed = () => document.querySelector('rich-textarea div[contenteditable="true"]') || document.querySelector('rich-textarea .ql-editor') || document.querySelector('div[contenteditable="true"]');
window.__state = () => {
  const mrs = [...document.querySelectorAll('model-response')];
  const imgs = [...document.querySelectorAll('model-response img')].filter(i => i.naturalWidth > 300).map(i => [i.naturalWidth, i.naturalHeight]);
  const stop = [...document.querySelectorAll('button')].some(b => /중지|Stop/.test(b.getAttribute('aria-label') || ''));
  const last = mrs[mrs.length - 1];
  return { turns: mrs.length, imgs, busy: stop ? 1 : 0, lastText: last ? last.innerText.trim().slice(0, 160) : '', vis: document.visibilityState };
};
window.__wait = async (ms, want) => { const t0 = Date.now(); let s = __state(); while (Date.now() - t0 < ms) { s = __state(); if (!s.busy && s.imgs.length >= (want || 1) && s.turns >= (want || 1)) break; await __w(2000); } return { s }; };
window.__setText = async (P) => { const ed = __ed(); ed.focus(); document.execCommand('selectAll', false, null); document.execCommand('insertText', false, P); await __w(600); return ed.innerText.length; };
window.__send = async () => { const b = [...document.querySelectorAll('button')].find(b => /보내기|Send/.test(b.getAttribute('aria-label') || '')); if (!b) return 'no send btn'; b.click(); return 'sent'; };
window.__go = async (P) => { const n = await __setText(P); await __w(400); const r = await __send(); return { n, r }; };
window.__sendP = window.__go;
window.__poll = async (name) => {
  const ims = [...document.querySelectorAll('model-response img')].filter(i => i.naturalWidth > 300); const im = ims[ims.length - 1];
  const c = document.createElement('canvas'); c.width = im.naturalWidth; c.height = im.naturalHeight; c.getContext('2d').drawImage(im, 0, 0);
  const bl = await new Promise(r => c.toBlob(r, 'image/png'));
  const fn = name + '_' + Date.now() + '.png'; const a = document.createElement('a'); a.href = URL.createObjectURL(bl); a.download = fn; document.body.appendChild(a); a.click(); await __w(800); a.remove();
  return { grab: { n: ims.length, name: fn, size: bl.size }, imgs: ims.map(i => [i.naturalWidth, i.naturalHeight]) };
};
window.__prep = async () => {
  const nb = [...document.querySelectorAll('a')].find(a => a.getAttribute('href') === '/app' && /새 채팅|New chat/.test(a.getAttribute('aria-label') || '')); if (nb) nb.click(); await __w(2500);
  let mb = [...document.querySelectorAll('button')].find(b => /모드 선택/.test(b.getAttribute('aria-label') || '')); let pill = mb ? mb.getAttribute('aria-label') : null; let hit = false;
  if (mb && !/Pro/.test(pill)) { mb.click(); await __w(1200); const it = [...document.querySelectorAll('[role="menuitem"], [role="menuitemradio"], [role="option"], button')].find(e => /^\s*Pro\b/.test((e.innerText || '').trim())); if (it) { it.click(); hit = true; await __w(1000); } else { document.body.click(); } }
  else hit = !!mb;
  mb = [...document.querySelectorAll('button')].find(b => /모드 선택/.test(b.getAttribute('aria-label') || '')); pill = mb ? mb.getAttribute('aria-label') : null;
  if (!document.querySelector('input[type=file]')) { const ub = [...document.querySelectorAll('button')].find(b => /업로드 및 도구/.test(b.getAttribute('aria-label') || '')); if (ub) { ub.click(); await __w(800); } }
  return { hit, pill, url: location.href, turns: document.querySelectorAll('model-response').length, fileInput: !!document.querySelector('input[type=file]') };
};
