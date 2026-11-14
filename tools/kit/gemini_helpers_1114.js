// gemini_helpers_1114.js — Gemini 웹(gemini.google.com) 탭에 넣어 쓰는 도우미(2026-11-14 · L13c ~ L13b 다시 짓기에서 쓴 것 그대로).
//   넣는 법: Claude in Chrome 의 javascript_tool 로 이 파일 내용을 한 번 실행한다(페이지가 새로 뜨면 사라진다 — 「__prep is not defined」가 나면 다시 넣는다).
//   쓰는 법은 tools/kit/README.md 「2. Gemini 몰기」.
//   ⚠ 로그인 · 약관 · CAPTCHA 는 건드리지 않는다(사용자 몫). document.visibilityState 를 속이지 않는다.
window.__sleep = ms => new Promise(r => setTimeout(r, ms));
// 모드 알약의 지금 이름 — 그림을 시키기 전에 반드시 「카본 높음」인지 본다.
window.__pill = () => { const b=[...document.querySelectorAll('button')].find(b=>(b.getAttribute('aria-label')||'').startsWith('모드 선택 도구 열기')); const m=b&&(b.getAttribute('aria-label')||'').match(/현재 (.+?) 모드/); return m?m[1]:null; };
window.__turns = () => document.querySelectorAll('model-response').length;
// 파일 올리기 채비: 숨은 file input 을 화면 귀퉁이에 꺼내고 aria-label 을 붙인다 → find("file input labeled <LABEL>") → file_upload(ref).
window.__prep = async (label) => { document.querySelectorAll('input[type=file][aria-label]').forEach(i => { if (i.parentElement === document.body) i.remove(); else i.removeAttribute('aria-label'); });
  const btn = [...document.querySelectorAll('button')].find(b => (b.getAttribute('aria-label')||'') === '업로드 및 도구'); if (!btn) return {err:'no plus'};
  btn.click(); await __sleep(1000); const inputs=[...document.querySelectorAll('input[type=file]')]; const ex={n:inputs.length,moved:false};
  if (inputs[0]) { const i=inputs[0]; i.setAttribute('aria-label', label); document.body.appendChild(i); i.style.cssText='position:fixed;left:2px;top:2px;width:40px;height:20px;opacity:0.01;z-index:2147483647;display:block'; i.removeAttribute('hidden'); ex.moved=true; }
  document.dispatchEvent(new KeyboardEvent('keydown',{key:'Escape',code:'Escape',keyCode:27,bubbles:true})); await __sleep(400); return {ex, path:location.pathname, pill:__pill(), turns:__turns()}; };
// 프롬프트를 넣고 보낸다(붙은 그림의 폭을 thumbs 로 돌려준다 — 비어 있으면 그림이 안 붙은 것).
window.__go = async (prompt) => { const thumbs=[...document.querySelectorAll('uploader-file-preview img, .file-preview img, img[data-test-id*=preview], .attachment-preview img')].map(i=>i.naturalWidth);
  const ed=document.querySelector('rich-textarea .ql-editor')||document.querySelector('div[contenteditable=true]'); if(!ed) return {err:'no editor'};
  ed.focus(); document.execCommand('selectAll',false,null); document.execCommand('insertText',false,prompt); await __sleep(600); const t0=__turns();
  const sb=[...document.querySelectorAll('button')].find(b=>/보내기|메시지 보내기|Send/i.test(b.getAttribute('aria-label')||'')&&!b.disabled); if(!sb) return {err:'no send button',thumbs};
  sb.click(); await __sleep(1500); return {attach:{thumbs}, send:{sent:true, turns:__turns(), before:t0, len:prompt.length}}; };
// 답 그림이 다 나왔으면 PNG 로 내려받는다(파일 이름 = <label>_<ms>.png → 사용자의 Downloads). 아직이면 {pending:true}.
window.__wait2 = async (label) => { const rs=[...document.querySelectorAll('model-response')]; const last=rs[rs.length-1];
  const stop=!![...document.querySelectorAll('button')].find(b=>/중지|Stop/i.test(b.getAttribute('aria-label')||''));
  const imgs=last?[...last.querySelectorAll('img')].filter(i=>i.naturalWidth>=256&&i.complete):[];
  if (stop||!imgs.length) return {pending:true, st:{imgs:imgs.length, resp:rs.length, stop:stop?1:0, txt:last?(last.innerText||'').slice(0,120):''}};
  const img=imgs[imgs.length-1]; let blob=null, how='fetch'; try { blob=await (await fetch(img.src)).blob(); } catch(e){ how='canvas'; }
  if(!blob){ const c=document.createElement('canvas'); c.width=img.naturalWidth; c.height=img.naturalHeight; c.getContext('2d').drawImage(img,0,0); blob=await new Promise(r=>c.toBlob(r,'image/png')); }
  const name=`${label}_${Date.now()}.png`; const a=document.createElement('a'); a.href=URL.createObjectURL(blob); a.download=name; document.body.appendChild(a); a.click(); a.remove();
  return {n:imgs.length, name, w:img.naturalWidth, stop:0, type:blob.type, bytes:blob.size, how}; };
// 프롬프트는 길어서 javascript_tool 한 번에 window.__T = {S1:"…", Z1:"…"} 처럼 넣어 두고 __go(window.__T.S1) 로 보낸다.
['__sleep','__pill','__turns','__prep','__go','__wait2'].map(k=>k+':'+typeof window[k]).join(' ')
