#!/usr/bin/env node
/* 답 열쇠 · 이름 장부 — tools/cue/answerkey.py · tools/cue/names (2026-11-22 · 지시서_Opus_이름고리 §2 · §8)
   ① 답 열쇠 연장이 군더더기(장부의 ㉮)를 더는 내지 않는다 — 괄호 조각 · 화살표 · 수 · 일상어 · 표기 겹침
   ② 바이러스 이름처럼 꼭 필요한 낱말은 빼지 않는다(「—」 없는 fact 의 짧은 낱말도 남김)
   ③ 면제 목록(hooks.json 「_이름장부면제」)은 낱말마다 까닭이 있다
   ④ 장부의 「못 꺼냄」 줄은 모두 갈래 · 상태를 가진다 · mkreaders 와 relock 이 같은 연장을 쓴다 */
const {execFileSync}=require('child_process'), path=require('path'), fs=require('fs');
const R=path.join(__dirname,'..');
let bad=0; const ok=(c,m)=>{console.log((c?'  ✓ ':'  ✗ ')+m); if(!c) bad++;};
const G=JSON.parse(fs.readFileSync(path.join(R,'tools/cue/names/가름.json'),'utf8'));
const LED=JSON.parse(fs.readFileSync(path.join(R,'tools/cue/names/장부.json'),'utf8'));
const junk=Object.entries(G).filter(([k,v])=>v.갈래==='㉮').map(([k])=>k.split('|'));
const Ls=[...new Set([...junk.map(x=>x[0]),'L01a'])];
const K=JSON.parse(execFileSync('python3',[path.join(R,'tools/cue/answerkey.py'),...Ls]).toString());
const left=junk.filter(([L,w])=>K[L]&&w in K[L]);
ok(left.length===0,`장부 ㉮ ${junk.length} 줄이 답 열쇠에 없다${left.length?' — 남은 것: '+left.map(x=>x.join(' ')).join(' · '):''}`);
const all=Object.entries(K).flatMap(([L,r])=>Object.keys(r).map(t=>[L,t]));
ok(all.every(([L,t])=>(t.match(/\(/g)||[]).length===(t.match(/\)/g)||[]).length&&!/[↑↓→←/]/.test(t)),'괄호 짝 · 화살표 조각 없음');
ok(all.every(([L,t])=>!/^[\d.,]+\s*(만|억|ATP|년)?$/.test(t)),'수만인 낱말 없음');
ok(['HSV','HPV','아데노바이러스','EBV'].every(t=>t in (K.L01a||{})),'꼭 필요한 이름(L01a 바이러스 이름)은 남는다');
const H=JSON.parse(fs.readFileSync(path.join(R,'tools/hooks.json'),'utf8'));
const EX=(H._이름장부면제||{}).목록||{};
ok(Object.keys(EX).length>0&&Object.values(EX).every(v=>typeof v==='string'&&v.length>4),'면제 목록의 낱말마다 까닭');
const rows=Object.values(LED).filter(e=>e.출처==='못 꺼냄');
ok(rows.length>0&&rows.every(e=>e.갈래&&e.상태),`장부의 「못 꺼냄」 ${rows.length} 줄이 모두 갈래 · 상태를 가진다`);
for(const f of ['tools/cue/mkreaders.py','tools/cue/names/relock.py']){
  const src=fs.existsSync(path.join(R,f))?fs.readFileSync(path.join(R,f),'utf8'):'';
  ok(/from answerkey import/.test(src),f+' 가 answerkey 를 쓴다');
}
console.log(bad?'\n❌ 답 열쇠 · 장부 '+bad+'곳 실패':'\n✅ 답 열쇠 · 이름 장부 통과');
process.exit(bad?1:0);
