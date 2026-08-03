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

console.log('\n── A. 행 단위 주입 (PROW) ──');
T('행 지정이 셋째 자리에 들어간다', ()=>{
  run(`${C1}=${PID}#0`);
  const s=span(out(),PID);
  const f=s.slice(s.indexOf(',f:['));
  if(!f.includes('"'+C1+'"')) throw new Error('카드가 안 들어갔다 (큰따옴표 형식이어야 한다)');
  return C1+' → '+PID+'#0';
});
T('주입 후에도 DATA가 파싱된다', ()=>{
  const s=out();
  const st=s.indexOf('[',s.indexOf('const DATA'));
  let d=0,q=null,e=false,end=-1;
  for(let k=st;k<s.length;k++){const c=s[k];
    if(q){if(e){e=false;continue}if(c==='\\'){e=true;continue}if(c===q)q=null;continue}
    if(c==='"'||c==="'"||c==='`'){q=c;continue}
    if(c==='[')d++; else if(c===']'){d--; if(!d){end=k;break}}}
  const D=eval('('+s.slice(st,end+1)+')');
  return eq(D.length,37)+'장면 · '+D.reduce((a,x)=>a+x.panels.length,0)+'패널';
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
  const has=ORIG.match(/\{id:'([sd]\d+p\d+[ab]?)',pc:\[[^\]]+\]/);
  const pid=has[1];
  run(`${C1}=${pid}`);
  const s=span(out(),pid);
  const pc=s.slice(s.indexOf('pc:['), s.indexOf(']',s.indexOf('pc:['))+1);
  if(!pc.includes('"'+C1+'"')) throw new Error('덧붙이기 실패: '+pc.slice(0,80));
  return pid+' → '+pc.split(',').length+'개';
});

T('주입된 pc가 JSON.parse 된다 (verify_build 호환)', ()=>{
  const bad=[...out().matchAll(/pc:\[([^\]]*)\]/g)].filter(m=>{
    try{ JSON.parse('['+m[1]+']'); return false; }catch(e){ return true; } });
  if(bad.length) throw new Error(bad.length+'개가 JSON이 아니다: '+bad[0][0].slice(0,70));
  return '전부 JSON';
});

console.log('\n── C. 멱등·충돌 ──');
T('이미 있는 링크는 건너뛴다', ()=>{
  const has=ORIG.match(/\{id:'([sd]\d+p\d+[ab]?)',pc:\["([^"]+)"/);
  const o=run(`${has[2]}=${has[1]}`);
  if(!/이미 있다/.test(o)) throw new Error('건너뛰지 않았다');
  return eq(out().length, ORIG.length, '길이 불변')&&'무변경';
});
T('행이 이기고 pc에서 빠진다', ()=>{
  const has=ORIG.match(/\{id:'([sd]\d+p\d+[ab]?)',pc:\["([^"]+)"/);
  const pid=has[1], cid=has[2];
  const o=run(`${cid}=${pid}#0`);
  if(!/pc 에서 제거/.test(o)) throw new Error('pc에서 안 뺐다');
  const s=span(out(),pid);
  const pc=s.slice(s.indexOf('pc:['), s.indexOf(']',s.indexOf('pc:['))+1);
  if(pc.includes('"'+cid+'"')) throw new Error('pc에 아직 있다');
  return '중복 0';
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
