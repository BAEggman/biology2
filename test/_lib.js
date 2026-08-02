/* 검증 스위트 공용 — 경로·기준본·DATA를 저장소 안에서 스스로 만든다.
   세션이 바뀌어도 그대로 돈다. 필요한 것은 jsdom 하나뿐이다.
     npm i jsdom && node test/all.js                                          */
const fs=require('fs'), path=require('path'), {execSync}=require('child_process');

const ROOT=path.resolve(__dirname,'..');
const TMP=path.join(__dirname,'.tmp');
const sh=c=>execSync(c,{cwd:ROOT,maxBuffer:1e9,encoding:'utf8'});

/* 비교 기준이 되는 과거 커밋. 태그가 아니라 내용으로 찾는다 —
   커밋 해시가 리베이스로 바뀌어도 안 깨지게. */
function findCommit(pred, label){
  const list=sh('git log --format=%H -n 60').trim().split('\n');
  for(const h of list){ try{ if(pred(h)) return h; }catch(e){} }
  throw new Error('기준 커밋을 못 찾았다: '+label);
}
const has=(h,f,re)=>re.test(sh(`git show ${h}:${f}`));

let _base, _stage1, _stage2;
function baseline(){   /* v12 — 이 작업 직전 상태 */
  /* v10a도 v9 주석을 그대로 갖고 있다. 구분자는 pidList — v10a에서 처음 들어갔다. */
  if(!_base) _base=findCommit(h=>has(h,'index.html',/\/\* v9: 시각 니모닉 딥링크 \*\//)
                                && !has(h,'index.html',/pidList/), 'v12 기준본');
  return _base;
}
function stage1(){     /* v10a — 죽은 링크만 고친 상태 */
  if(!_stage1) _stage1=findCommit(h=>has(h,'index.html',/pidList/) && !has(h,'index.html',/picFix/), 'v10a');
  return _stage1;
}

function stage2(){     /* v10b — 복구 화면까지, 빌드 도입 전 */
  if(!_stage2) _stage2=findCommit(h=>has(h,'index.html',/picFix/) && !has(h,'index.html',/BUILD:START/), 'v10b');
  return _stage2;
}

function ensure(){
  fs.mkdirSync(TMP,{recursive:true});
  const w=(n,c)=>{ const p=path.join(TMP,n); fs.writeFileSync(p,c); return p; };
  const P={};
  P.BASE   = w('index.v12.html',  sh(`git show ${baseline()}:index.html`));
  P.BASESK = w('sketchy.v12.html',sh(`git show ${baseline()}:sketchy.html`));
  try{ P.STAGE1 = w('index.v10a.html', sh(`git show ${stage1()}:index.html`)); }catch(e){ P.STAGE1=null; }
  try{ P.STAGE2 = w('index.v10b.html', sh(`git show ${stage2()}:index.html`)); }catch(e){ P.STAGE2=null; }
  P.DATAJSON = w('DATA.json', JSON.stringify(parseDATA(fs.readFileSync(path.join(ROOT,'sketchy.html'),'utf8'))));
  return P;
}

function parseDATA(src){
  const st=src.indexOf('[', src.indexOf('const DATA'));
  let d=0,q=null,esc=false;
  for(let k=st;k<src.length;k++){ const c=src[k];
    if(q){ if(esc){esc=false;continue} if(c==='\\'){esc=true;continue} if(c===q)q=null; continue }
    if(c==='"'||c==="'"||c==='`'){ q=c; continue }
    if(c==='[')d++; else if(c===']'){ d--; if(!d) return eval('('+src.slice(st,k+1)+')'); } }
  throw new Error('DATA 파싱 실패');
}

/* 작은 테스트 하네스 */
function harness(){
  let pass=0, fail=0;
  const T=(n,f)=>{ try{ const m=f(); console.log('  ✓',n,m===undefined?'':'— '+m); pass++; }
                   catch(e){ console.log('  ✗',n,'—',String(e.message).split('\n')[0]); fail++; } };
  const eq=(a,b,m)=>{ if(String(a)!==String(b)) throw new Error((m||'')+' got '+a+' want '+b); return a; };
  const done=label=>{ console.log('\n'+(fail?'❌':'✅')+' '+label+' 통과 '+pass+' / 실패 '+fail);
                      process.exit(fail?1:0); };
  return {T,eq,done,stat:()=>({pass,fail})};
}

module.exports={ROOT,TMP,sh,ensure,parseDATA,harness,baseline,stage1,stage2};
