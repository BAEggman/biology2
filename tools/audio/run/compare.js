// compare.js — (Gemini 검수 탭에서 실행) 마지막 답의 JSON 받아 적기를 localStorage.b2tts2 대본과 문장 단위로 대조한다.
const t=[...document.querySelectorAll('message-content')].pop()?.innerText||''; const i=t.indexOf('{');
if(i<0) 'notyet'; else { const s=t.slice(i); let d=0,e=0; for(let j=0;j<s.length;j++){if(s[j]=='{')d++; else if(s[j]=='}'){d--; if(!d){e=j+1;break}}}
const J=JSON.parse(s.slice(0,e)); const files=Array.isArray(J)?J:(J.files||Object.values(J).find(v=>Array.isArray(v)));
const T=JSON.parse(localStorage.b2tts2); const nz=s=>s.replace(/[\s.,·!?「」'"‘’“”()\-–—:;…]/g,'');
const sents=s=>s.split(/(?<=[.?!])\s+/).map(x=>x.trim()).filter(Boolean); const out=[];
for(const f of files){const k=(f.filename.match(/(L\w+?_s\d+)_v\d+/)||[])[1]; const a=sents(T[k].t), b=sents(f.verbatim_text||''); const bn=b.map(nz); const diffs=[];
 a.forEach(x=>{const xn=nz(x); if(!bn.includes(xn)){ let best='',bs=0; for(const y of b){let c=0; const yn=nz(y); for(let j=0;j<Math.min(xn.length,yn.length);j++) if(xn[j]===yn[j]) c++; if(c>bs){bs=c;best=y}}
  let i=0; while(i<xn.length&&xn[i]===nz(best)[i]) i++; diffs.push('…'+x.slice(Math.max(0,i-10),i+22)+' ⇒ '+best.slice(Math.max(0,i-10),i+22))}});
 out.push(k+(diffs.length?'\n ✗ '+diffs.join('\n ✗ '):' ✓'));}
out.join('\n')}
