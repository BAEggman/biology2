const L=require('./_lib');
/* 승인 큐 주입기 검증 (tools/apply.js)
   왜 필요한가: 13.7MB 텍스트를 괄호 스캐너로 잘라 고친다. 이 저장소에서 가장
   위험한 종류의 조작이고, 한 글자만 어긋나도 DATA 전체가 죽는다.
   원본은 절대 안 건드린다 — 사본에 대고 돌린다. */
const fs=require('fs'), path=require('path'), {execSync}=require('child_process');
const R=L.ROOT, TMP=path.join(R,'test/.tmp');
let pass=0,fail=0;
const T=(n,f)=>{ try{ const m=f(); console.log('  ✓',n,m===undefined?'':'— '+m); pass++; }
                 catch(e){ console.log('  ✗',n,'—',String(e.message).split('\n')[0]); fail++; } };
const eq=(a,b,m)=>{ if(String(a)!==String(b)) throw new Error((m||'')+' got '+a+' want '+b); return a; };

fs.mkdirSync(TMP,{recursive:true});
const ORIG=fs.readFileSync(path.join(R,'sketchy.html'),'utf8');
const COPY=path.join(TMP,'sk_apply.html'), PICK=path.join(TMP,'pick.txt');
/* 실제 산출물(outputs/need_picture.md)을 절대 안 건드린다 — 테스트가 사용자의 작업을 지우면 안 된다 */
const NP=path.join(TMP,'need_picture.md');
const CARDS=JSON.parse(fs.readFileSync(path.join(R,'index.html'),'utf8')
  .match(/id=["']CARDS["'][^>]*>([\s\S]*?)<\/script>/)[1]);
const CID=CARDS.map(c=>c.id);

const run=(txt,flags='')=>{
  fs.writeFileSync(COPY,ORIG); fs.writeFileSync(PICK,txt);
  return execSync(`node tools/apply.js ${PICK} ${flags}`,
    {cwd:R,encoding:'utf8',maxBuffer:1e9,env:{...process.env,SKETCHY:COPY,NEEDPIC:NP}});
};
const runFail=(txt)=>{ try{ run(txt); return null; }catch(e){ return (e.stdout||'')+(e.stderr||''); } };
const out=()=>fs.readFileSync(COPY,'utf8');
const span=(s,pid)=>{ /* 패널 객체 전체 — bx가 길어 고정 길이로 자르면 f:[에 못 닿는다 */
  const i=s.indexOf("{id:'"+pid+"'"); let d=0,q=null,e=false;
  for(let k=i;k<s.length;k++){ const c=s[k];
    if(q){ if(e){e=false;continue} if(c==='\\'){e=true;continue} if(c===q)q=null; continue }
    if(c==='"'||c==="'"||c==='`'){q=c;continue}
    if(c==='{')d++; else if(c==='}'){ d--; if(!d) return s.slice(i,k+1); } }
  throw new Error(pid+' 범위를 못 찾았다'); };
/* 사실표가 있고 아직 셋째 자리가 없는 패널을 하나 고른다 */
const PID='s31p01', PID2='s33p01';
const C1=CID.find(x=>x==='B1-51')||CID[0], C2=CID.find(x=>x==='B1-209')||CID[1];
/* [정정 2026-08-22] pc 훑기가 끝나 덱에 pc 가 한 곳도 남지 않았다(패널단위 0).
   아래 세 검사는 ORIG 에서 pc 패널을 **찾아** 썼기 때문에 null 을 읽고 죽었다.
   그런데 지켜야 할 불변식은 「덱에 pc 가 있다」가 아니라 「주입기가 pc 를 다룰 줄 안다」이다.
   pc 는 앞으로도 새 그림을 넣을 때 임시로 생겼다가 행으로 내려가며 사라진다 —
   그 왕복을 검사하려면 덱 상태에 기대지 말고 씨앗을 심어서 검사해야 한다. */
const SEED=(()=>{ const h="{id:'"+PID2+"'"; const i=ORIG.indexOf(h);
  if(i<0) throw new Error(PID2+' 를 못 찾았다');
  return ORIG.slice(0,i+h.length)+',pc:["'+C2+'"]'+ORIG.slice(i+h.length); })();
const runS=(txt,flags='')=>{
  fs.writeFileSync(COPY,SEED); fs.writeFileSync(PICK,txt);
  return execSync(`node tools/apply.js ${PICK} ${flags}`,
    {cwd:R,encoding:'utf8',maxBuffer:1e9,env:{...process.env,SKETCHY:COPY,NEEDPIC:NP}});
};

console.log('\n── A. 행 단위 주입 (PROW) ──');
T('행 지정이 셋째 자리에 들어간다', ()=>{
  run(`${C1}=${PID}#0`);
  const s=span(out(),PID);
  const f=s.slice(s.indexOf(',f:['));
  if(!f.includes('"'+C1+'"')) throw new Error('카드가 안 들어갔다 (큰따옴표 형식이어야 한다)');
  return C1+' → '+PID+'#0';
});
/* 장면·패널 수를 고정값(37)으로 검사했더니 장면을 하나 그릴 때마다 이 테스트가 깨졌다.
   주입기가 지켜야 할 불변식은 「37장면」이 아니라 「주입이 장면·패널을 늘리거나 줄이지
   않는다」이다. 그래서 원본과 대조한다. 사실 개수는 늘어도 되지만(셋째 자리가 붙으므로)
   장면·패널 수는 절대 안 바뀐다. */
const shape=s=>{
  const st=s.indexOf('[',s.indexOf('const DATA'));
  let d=0,q=null,e=false,end=-1;
  for(let k=st;k<s.length;k++){const c=s[k];
    if(q){if(e){e=false;continue}if(c==='\\'){e=true;continue}if(c===q)q=null;continue}
    if(c==='"'||c==="'"||c==='`'){q=c;continue}
    if(c==='[')d++; else if(c===']'){d--; if(!d){end=k;break}}}
  const D=eval('('+s.slice(st,end+1)+')');
  return {n:D.length, p:D.reduce((a,x)=>a+x.panels.length,0),
          ids:D.flatMap(x=>x.panels.map(p=>p.id)).sort().join(',')};
};
const BASE=shape(ORIG);
T('주입 후에도 DATA가 파싱되고 장면·패널이 그대로다', ()=>{
  const A=shape(out());
  eq(A.n,BASE.n,'장면 수가 바뀌었다:');
  eq(A.p,BASE.p,'패널 수가 바뀌었다:');
  eq(A.ids,BASE.ids,'패널 ID 집합이 바뀌었다:');
  return BASE.n+'장면 · '+BASE.p+'패널 (원본과 동일)';
});
T('build.js가 PROW를 실제로 만든다', ()=>{
  const sk=path.join(R,'sketchy.html'), bak=path.join(TMP,'sk_bak.html');
  fs.copyFileSync(sk,bak);
  try{
    fs.copyFileSync(COPY,sk);
    const o=execSync('node build.js --check',{cwd:R,encoding:'utf8',maxBuffer:1e9});
    const m=o.match(/행단위 (\d+)/);
    if(!m||+m[1]<1) throw new Error('행단위가 0이다: '+o.split('\n')[1]);
    return '행단위 '+m[1];
  } finally { fs.copyFileSync(bak,sk); fs.unlinkSync(bak); }
});

console.log('\n── B. 패널 단위 주입 (pc) ──');
T('pc가 없는 패널에 pc를 새로 만든다', ()=>{
  run(`${C2}=${PID2}`);
  const s=span(out(),PID2);
  if(!/^\{id:'s33p01',pc:\[/.test(s)) throw new Error('pc 신설 실패: '+s.slice(0,60));
  return 'pc 신설';
});
T('pc가 있는 패널에는 덧붙인다', ()=>{
  runS(`${C1}=${PID2}`);
  const s=span(out(),PID2);
  const pc=s.slice(s.indexOf('pc:['), s.indexOf(']',s.indexOf('pc:['))+1);
  if(!pc.includes('"'+C1+'"')) throw new Error('덧붙이기 실패: '+pc.slice(0,80));
  if(!pc.includes('"'+C2+'"')) throw new Error('원래 있던 것을 덮어썼다: '+pc.slice(0,80));
  return PID2+' → '+pc.split(',').length+'개';
});

T('주입된 pc가 JSON.parse 된다 (verify_build 호환)', ()=>{
  const bad=[...out().matchAll(/pc:\[([^\]]*)\]/g)].filter(m=>{
    try{ JSON.parse('['+m[1]+']'); return false; }catch(e){ return true; } });
  if(bad.length) throw new Error(bad.length+'개가 JSON이 아니다: '+bad[0][0].slice(0,70));
  return '전부 JSON';
});

console.log('\n── B2. 같은 자리에 여럿 (회귀) ──');
/* 배열 리터럴의 최상위 원소를 센다 — 문자열 안의 괄호에 속으면 안 된다 */
function cells(src, lb){
  let d=0,q=null,e=false,st=null,out=[];
  const rb=(()=>{ let dd=0,qq=null,ee=false;
    for(let k=lb;k<src.length;k++){ const c=src[k];
      if(qq){ if(ee){ee=false;continue} if(c==='\\'){ee=true;continue} if(c===qq)qq=null; continue }
      if(c==='"'||c==="'"||c==='`'){qq=c;continue}
      if(c==='[')dd++; else if(c===']'){ dd--; if(!dd) return k; } } })();
  for(let k=lb+1;k<rb;k++){ const c=src[k];
    if(q){ if(e){e=false;continue} if(c==='\\'){e=true;continue} if(c===q)q=null; continue }
    if(c==='"'||c==="'"||c==='`'){ if(st===null)st=k; q=c; continue }
    if(c==='['||c==='{'){ if(!d&&st===null)st=k; d++; continue }
    if(c===']'||c==='}'){ d--; continue }
    if(c===','&&!d){ if(st!==null){out.push(src.slice(st,k)); st=null;} continue }
    if(!d&&st===null&&!/\s/.test(c)) st=k; }
  if(st!==null) out.push(src.slice(st,rb));
  return out;
}
T('한 행에 카드 둘 → 셋째 자리는 하나', ()=>{
  run(`${C1}=${PID}#0\n${C2}=${PID}#0`);
  const s=span(out(),PID);
  const fb=s.indexOf('[', s.indexOf(',f:['));
  const row0=cells(s, fb)[0];
  const cs=cells(s, s.indexOf(row0)===-1?fb:s.indexOf('[', s.indexOf(row0)-1));
  const n=cells(row0, 0).length;
  if(n!==3) throw new Error('행 원소가 '+n+'개다 (3 기대) — 셋째 자리 중복: '+row0.slice(0,110));
  if(!row0.includes(C1)||!row0.includes(C2)) throw new Error('둘 다 안 들어갔다: '+row0.slice(0,110));
  return '원소 3 · ["'+C1+'","'+C2+'"]';
});
T('한 행에 카드 둘 → build.js가 받아준다', ()=>{
  const sk=path.join(R,'sketchy.html'), bak=path.join(TMP,'sk_bak2.html');
  fs.copyFileSync(sk,bak);
  try{
    fs.copyFileSync(COPY,sk);
    const o=execSync('node build.js --check',{cwd:R,encoding:'utf8',maxBuffer:1e9});
    if(!/통과/.test(o)) throw new Error('빌드가 안 통과: '+o.slice(-160));
    return (o.match(/행단위 (\d+)/)||[])[0]||'ok';
  } finally { fs.copyFileSync(bak,sk); fs.unlinkSync(bak); }
});
T('한 패널에 카드 둘 → pc 하나에 둘', ()=>{
  run(`${C1}=${PID2}\n${C2}=${PID2}`);
  const s=span(out(),PID2);
  const pc=s.slice(s.indexOf('pc:['), s.indexOf(']',s.indexOf('pc:['))+1);
  if((s.match(/pc:\[/g)||[]).length!==1) throw new Error('pc가 여러 번 생겼다');
  if(!pc.includes(C1)||!pc.includes(C2)) throw new Error('둘 다 안 들어갔다: '+pc);
  return pc.slice(0,50);
});

console.log('\n── C. 멱등·충돌 ──');
T('이미 있는 링크는 건너뛴다', ()=>{
  const o=runS(`${C2}=${PID2}`);
  if(!/이미 있다/.test(o)) throw new Error('건너뛰지 않았다');
  return eq(out().length, SEED.length, '길이 불변')&&'무변경';
});
T('행이 이기고 pc에서 빠진다', ()=>{
  const o=runS(`${C2}=${PID2}#0`);
  if(!/pc 에서 제거/.test(o)) throw new Error('pc에서 안 뺐다');
  const s=span(out(),PID2);
  const j=s.indexOf('pc:[');
  const pc=j<0?'':s.slice(j, s.indexOf(']',j)+1);
  if(pc.includes('"'+C2+'"')) throw new Error('pc에 아직 있다');
  const f=s.slice(s.indexOf(',f:['));
  if(!f.includes('"'+C2+'"')) throw new Error('행으로 안 내려갔다');
  return '중복 0 · 행으로 내려감';
});

console.log('\n── D. 잘못된 입력은 아무것도 안 쓴다 ──');
T('없는 카드 ID면 죽는다', ()=>{
  const e=runFail(`NOPE-999=${PID}`);
  if(!/없는 카드 ID/.test(e||'')) throw new Error('안 죽었다');
  return '중단';
});
T('없는 패널 표기면 죽는다', ()=>{
  const e=runFail(`${C1}=s99p99`);
  if(!/중단/.test(e||'')) throw new Error('안 죽었다');
  return '중단';
});
T('행 번호가 범위를 넘으면 죽는다', ()=>{
  const e=runFail(`${C1}=${PID}#999`);
  if(!/행이 \d+개뿐/.test(e||'')) throw new Error('안 죽었다');
  return '중단';
});
T('--check는 파일을 안 쓴다', ()=>{
  run(`${C1}=${PID}#0`,'--check');
  return eq(out().length, ORIG.length, '길이')&&'무변경';
});

console.log('\n── E. 해당 없음 ──');
T('빈 우변은 need_picture.md로 간다', ()=>{
  const np=NP;
  if(fs.existsSync(np)) fs.unlinkSync(np);
  run(`${C1}=`);
  if(!fs.existsSync(np)) throw new Error('파일이 안 생겼다');
  const t=fs.readFileSync(np,'utf8');
  if(!t.includes(C1)) throw new Error('카드가 안 적혔다');
  return eq(out().length, ORIG.length, 'sketchy 불변')&&'기록됨';
});

T('--check는 need_picture.md도 안 쓴다', ()=>{
  const np=NP;
  if(fs.existsSync(np)) fs.unlinkSync(np);
  run(`${C1}=`,'--check');
  if(fs.existsSync(np)) throw new Error('--check인데 파일을 썼다 — 출력은 「안 썼다」고 한다');
  return '무기록';
});

fs.rmSync(COPY,{force:true}); fs.rmSync(PICK,{force:true});
console.log(`\n${fail?'❌':'✅'} 주입기 통과 ${pass} / 실패 ${fail}`);
process.exit(fail?1:0);
