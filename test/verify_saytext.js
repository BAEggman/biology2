#!/usr/bin/env node
/* verify_saytext.js — 낭독 대본(say)과 화면 글이 반말 변환 · 언어 복구 뒤 다시 망가지지 않았는지 (2026-11-20 · 인계문 §6 · §13)
   1. 과 142 · 정거장 1,598 고정 — tools/audit/2026-11-20/sids.json 과 같아야 한다(뜻이 있어 늘리거나 줄일 때는 그 파일을 고치고 까닭을 커밋에)
   2. 제어문자(U+0000 ~ U+001F · U+007F) 없음 — obj · fact · hook · say · ask
   3. 받침 ㅆ + 「는다」(세웠는다 · 일어났는다 …) 없음 — 「있는다」만 허용
   4. 「 않다 · 않는다 · 않았다 …」 앞 낱말이 「-지(는 · 도 · 만 …)」로 끝남(낱말이 빠진 「[U+0001] 않다」 꼴을 막음)
   5. 존댓말 어미 없음 — 받침 ㅂ + 니다 · 니까 · 시다(합니다 · 봅시다) · 요/죠 + 문장부호 · 세요 · 십시오
   6. 반말 변환 때 생긴 사전형 종결(펄럭이다. · 죽이다. · 눈이 뜨다 · 약한다 …) 없음
   7. 언어 복구 44 구간(tools/audit/2026-11-20/repaired44.json)의 「복구 뒤」 글귀가 그대로 있음
      — 과학 고침으로 그 문장 자체가 바뀌면 repaired44.json 의 그 줄을 새 글귀로 고치고 까닭을 커밋에 적는다
   8. say ≤ 560자(낭독 한 파일이 70초 안쪽) */
const fs=require('fs'), path=require('path');
const ROOT=path.resolve(__dirname,'..');
const LDIR=process.env.SAYTEXT_LESSONS||path.join(ROOT,'lessons');   /* 시험용: 옛 글을 풀어 둔 폴더로 바꿔 문이 실제로 막는지 본다 */
const A=path.join(ROOT,'tools/audit/2026-11-20');
const ids=fs.readdirSync(LDIR).filter(f=>/^L\w+\.json$/.test(f)).sort();
const L={}; for(const f of ids){ const j=JSON.parse(fs.readFileSync(path.join(LDIR,f),'utf8')); L[j.id]=j; }
let bad=0, n=0;
const fail=(m)=>{ bad++; if(bad<=40) console.log('  ✕ '+m); };
const ok=(m)=>console.log('  ✓ '+m);

/* 1 */
const want=JSON.parse(fs.readFileSync(path.join(A,'sids.json'),'utf8'));
const got={}; for(const [k,j] of Object.entries(L)) got[k]=j.stops.map(s=>s.sid);
const wk=Object.keys(want), gk=Object.keys(got);
for(const k of wk) if(!got[k]) fail('과가 없다: '+k);
for(const k of gk) if(!want[k]) fail('새 과(sids.json 에 없음): '+k);
for(const k of wk) if(got[k] && JSON.stringify(got[k])!==JSON.stringify(want[k])) fail('정거장 목록이 다르다: '+k+' '+JSON.stringify(got[k]));
const nS=gk.reduce((a,k)=>a+got[k].length,0);
if(bad===0) ok('과 '+gk.length+' · 정거장 '+nS+' — sids.json 과 같음');

const jong=c=>{ const o=c.charCodeAt(0)-0xAC00; return (o>=0&&o<11172)?o%28:-1; };
const CTL=/[\u0000-\u001f\u007f]/;
const DICT=/(^|[\s,])(펄럭|반짝|번쩍|헐떡|깜빡|끄덕|출렁|기울|밀어붙|먹|죽|움직)이다[.!?]|눈이 뜨다|(^|\s)(약|강)한다/;
const HON=/(세요|십시오|[가-힣]요[.?!]|죠[.?!])/;
const c={ctl:0,ss:0,anh:0,hon:0,dict:0,len:0};
for(const [id,j] of Object.entries(L)) for(const s of j.stops){
  n++;
  for(const k of ['obj','fact','hook','say','ask']){ const t=s[k]; if(typeof t==='string' && CTL.test(t)){ c.ctl++; fail(`제어문자 ${id} ${s.sid} ${k}`); } }
  const t=s.say||'';
  /* 3 */
  for(const m of t.matchAll(/(\S*?)([가-힣])는다/g)){ if(jong(m[2])===20 && m[2]!=='있'){ c.ss++; fail(`받침ㅆ+는다 ${id} ${s.sid} 「${m[0]}」`); } }
  /* 4 */
  for(const m of t.matchAll(/(\S*)\s(않(?:다|는다|았다|을|고|으며|으면|아|았|는|게)?)/g)){
    if(!/지(?:는|도|만|조차|가|요)?$/.test(m[1])){ c.anh++; fail(`「 않-」 앞이 「-지」가 아님 ${id} ${s.sid} 「${m[0]}」`); } }
  /* 5 */
  for(const m of t.matchAll(/([가-힣])(니다|니까|시다)/g)){ if(jong(m[1])===17){ c.hon++; fail(`존댓말 ${id} ${s.sid} 「${m[0]}」`); } }
  const h=t.match(HON); if(h){ c.hon++; fail(`존댓말 ${id} ${s.sid} 「${h[0]}」`); }
  /* 6 */
  const d=t.match(DICT); if(d){ c.dict++; fail(`사전형 종결 ${id} ${s.sid} 「${d[0].trim()}」`); }
  /* 8 */
  if(t.length>560){ c.len++; fail(`say 가 560자를 넘음 ${id} ${s.sid} ${t.length}`); }
}
for(const [k,v] of Object.entries({ctl:'제어문자',ss:'받침ㅆ+는다',anh:'빠진 「-지」',hon:'존댓말',dict:'사전형 종결',len:'560자 넘음'})) if(!c[k]) ok(v+' 0');

/* 7 */
const R=JSON.parse(fs.readFileSync(path.join(A,'repaired44.json'),'utf8')); let r=0;
for(const x of R){ const s=(L[x.lesson]||{stops:[]}).stops.find(s=>s.sid===x.sid);
  if(!s){ fail(`복구 목록의 정거장이 없다 ${x.lesson} ${x.sid}`); continue; }
  if(!s.say.includes(x.must_contain.trim())){ fail(`언어 복구가 되돌아감 ${x.lesson} ${x.sid} 「${x.must_contain.trim().slice(0,30)}…」`); continue; }
  r++; }
if(r===R.length) ok(`언어 복구 ${r}/${R.length} 구간 그대로`);

console.log(bad?`\n❌ 대본 문 실패 ${bad}`:`\n✅ 대본 문 통과 (정거장 ${n})`);
process.exit(bad?1:0);
