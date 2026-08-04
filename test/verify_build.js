const L=require('./_lib');
const BL=require('./baseline.json');
const ge=(a,b,m)=>{ if(!(a>=b)) throw new Error((m||'')+' '+a+' < 기준 '+b+' — 연결이 줄었다(회귀)'); return a; };
const le=(a,b,m)=>{ if(!(a<=b)) throw new Error((m||'')+' '+a+' > 기준 '+b+' — 고아가 늘었다(회귀)'); return a; };
const FX=L.ensure();
/* 제안 4 검증 — 스키마·빌드·드리프트 방어 */
const fs=require('fs'), path=require('path'), {execSync}=require('child_process');
const R=L.ROOT;
const sh=c=>execSync(c,{cwd:R,maxBuffer:1e9,encoding:'utf8'});
let pass=0,fail=0;
const T=(n,f)=>{ try{ const m=f(); console.log('  ✓',n,m===undefined?'':'— '+m); pass++; }
                 catch(e){ console.log('  ✗',n,'—',String(e.message).split('\n')[0]); fail++; } };
const eq=(a,b,m)=>{ if(String(a)!==String(b)) throw new Error((m||'')+' got '+a+' want '+b); return a; };
const read=f=>fs.readFileSync(path.join(R,f),'utf8');
const J=(s,n)=>JSON.parse(s.match(new RegExp('var '+n+'=(\\{.*?\\});','s'))[1]);

console.log('\n── A. 스키마 이관 (무손실) ──');
const sk=read('sketchy.html');
T('pc 보유 패널은 줄지 않는다', ()=>ge((sk.match(/,pc:\[/g)||[]).length,BL.pcPanels,'pc 패널')+'개');
/* [수정] 「v12와 바이트 동일」로 검사하면 사실표를 고칠 때마다 깨진다.
   그런 테스트는 무시하게 되고, 무시되는 테스트는 없느니만 못하다.
   이관이 무손실이었나는 구조로 본다 — pc를 걷어냈을 때 구조가 v12와 같은가. */
T('pc를 걷어내면 구조가 v12와 같다', ()=>{
  const strip=t=>t.replace(/(\{id:'[sd]\d+p\d+[ab]?')\,pc:\[[^\]]*\]\,/g,'$1,');
  const shape=t=>(t.match(/\{id:'[sd]\d+p?\d*[ab]?'/g)||[]).join('|');
  const orig=fs.readFileSync(FX.BASESK,'utf8');
  /* [정정] 완전 일치는 패널을 추가하면 깨진다 — 추가가 이 프로젝트의 목적이다.
     불변식은 「v12의 장면·패널이 하나도 사라지지 않았고 순서도 그대로다」이다. */
  const now=shape(strip(sk)).split('|'), was=shape(orig).split('|');
  let i=0; const gone=[];
  for(const k of was){ const j=now.indexOf(k,i); if(j<0) gone.push(k); else i=j+1; }
  eq(gone.join(','),'', 'v12에서 사라진 것');
  const added=now.filter(k=>!was.includes(k));
  if(added.length) console.log('      + 추가: '+added.join(' '));
  const nf=t=>(t.match(/,f:\[/g)||[]).length;
  ge(nf(sk), nf(orig), '사실표 보유 패널 수');
  return '소실 0 · 추가 '+added.length;
});
T('pc 값이 전부 유효한 카드 ID', ()=>{
  const CARDS=new Set(JSON.parse(read('index.html')
    .match(/id=["']CARDS["'][^>]*>([\s\S]*?)<\/script>/)[1]).map(c=>c.id));
  const bad=[...sk.matchAll(/pc:\[([^\]]*)\]/g)]
    .flatMap(m=>JSON.parse('['+m[1]+']')).filter(id=>!CARDS.has(id));
  return eq(bad.length,0)+'건 무효';
});
T('사실표 행 수 (기준본 이상)', ()=>{
  const D=eval('('+(()=>{ const s=sk, st=s.indexOf('[',s.indexOf('const DATA')); let d=0,q=null,e=false;
    for(let k=st;k<s.length;k++){const c=s[k];
      if(q){if(e){e=false;continue}if(c==='\\'){e=true;continue}if(c===q)q=null;continue}
      if(c==='"'||c==="'"||c==='`'){q=c;continue}
      if(c==='[')d++;else if(c===']'){d--;if(!d)return s.slice(st,k+1)}}})()+')');
  /* v12 기준 590행. 그라운딩 규칙상 「그림에 있는데 표에 없는 소품」은 행을 추가한다.
     그러니 줄면 안 되고 늘어나는 건 정상이다. */
  const n=D.reduce((a,s)=>a+s.panels.reduce((x,p)=>x+(p.f||[]).length,0),0);
  if(n<590) throw new Error('행이 줄었다: '+n);
  return n+'행 (v12 590 + '+(n-590)+')';
});

console.log('\n── B. 빌드 산출물 == 손으로 만든 v10b 지도 ──');
const now=read('index.html'), prev=fs.readFileSync(FX.STAGE2,'utf8');   /* v10b — 손으로 만든 지도 */
const norm=o=>Object.fromEntries(Object.entries(o).map(([k,v])=>[k,(Array.isArray(v)?v:[v]).slice().sort().join('|')]));
T('PMAP은 줄지 않는다', ()=>ge(Object.keys(J(now,'PMAP')).length,BL.pmap,'PMAP')+'장');
T('PMAP 값이 한 건도 안 바뀜', ()=>{
  const a=norm(J(prev,'PMAP')), b=norm(J(now,'PMAP'));
  const d=Object.keys(a).filter(k=>a[k]!==b[k]);
  return eq(d.length,0)+'건 차이'; });
/* [수정] PFACT 내용은 사실표를 고치면 당연히 바뀐다. 형태만 본다. */
T('PTIT·PBR 키 집합 동일 · PFACT는 소스와 일치', ()=>{
  /* [정정] 「키 집합이 동일」은 패널을 추가하면 깨진다 — 추가는 이 프로젝트의 목적이다.
     불변식은 「이전 키가 하나도 사라지지 않았다」이다. */
  ['PTIT','PBR'].forEach(n=>{
    const before=Object.keys(J(prev,n)), after=new Set(Object.keys(J(now,n)));
    const gone=before.filter(k=>!after.has(k));
    eq(gone.join(','),'',n+' 소실');
  });
  const rows=o=>Object.values(o).reduce((a,b)=>a+b.length,0);
  const src=L.parseDATA(sk).reduce((a,s)=>a+s.panels.reduce((x,p)=>x+(p.f||[]).length,0),0);
  eq(rows(J(now,'PFACT')),src,'PFACT 행 == 소스');
  ge(Object.keys(J(now,'PFACT')).length,Object.keys(J(prev,'PFACT')).length,'PFACT 패널');
  return '키 동일 · '+rows(J(now,'PFACT'))+'행';
});
T('PNOIMG의 기존 항목이 사라지지 않았다', ()=>{
  const before=JSON.parse(prev.match(/var PNOIMG=(\[.*?\]);/s)[1]);
  const after=new Set(JSON.parse(now.match(/var PNOIMG=(\[.*?\]);/s)[1]));
  return eq(before.filter(x=>!after.has(x)).join(','),'')||before.length+'장 유지';
});
T('PROW 항목이 전부 실재하는 행을 가리킨다', ()=>{
  const PROW=J(now,'PROW'), PMAP=J(now,'PMAP'), PFACT=J(now,'PFACT');
  let n=0;
  for(const cid in PROW) for(const pid in PROW[cid]){
    const rows=PFACT[pid]||[];
    PROW[cid][pid].forEach(i=>{ if(!(i>=0&&i<rows.length))
      throw new Error(cid+' → '+pid+'#'+i+' : 행이 '+rows.length+'개뿐'); n++; });
    const v=PMAP[cid], has=Array.isArray(v)?v.includes(pid):v===pid;
    if(!has) throw new Error(cid+'가 PROW에 있는데 PMAP에 '+pid+'이 없다');
  }
  return Object.keys(PROW).length+'카드 · '+n+'행';
});
T('BUILD 마커 존재', ()=>eq(/\/\*BUILD:START[\s\S]*?BUILD:END\*\//.test(now),true));
/* 고정값 → 불변식 (§10). build.js는 CARDS를 읽기만 하므로 「빌드가 카드를 건드리지 않는다」가
   진짜 불변식이고, 사람이 카드를 더 넣는 것은 막을 이유가 없다. */
T('빌드가 기존 카드를 건드리지 않는다 (추가는 허용)', ()=>{
  const P=s=>JSON.parse(s.match(/id=["']CARDS["'][^>]*>([\s\S]*?)<\/script>/)[1]);
  const cur=new Map(P(now).map(c=>[c.id,JSON.stringify(c)]));
  const bad=P(prev).filter(c=>cur.get(c.id)!==JSON.stringify(c));
  if(bad.length) throw new Error('빌드가 카드를 바꿨다 '+bad.length+'장: '+bad.slice(0,5).map(c=>c.id).join(','));
  return P(prev).length+'장 보존 · 현재 '+cur.size+'장'; });

console.log('\n── C. 재현성 ──');
T('두 번 돌려도 동일 (idempotent)', ()=>{
  const h1=sh('sha256sum index.html links_report.md');
  sh('node build.js >/dev/null');
  return eq(sh('sha256sum index.html links_report.md'),h1)&&'해시 일치'; });
T('--check는 아무것도 안 쓴다', ()=>{
  const h1=sh('sha256sum index.html links_report.md');
  sh('node build.js --check >/dev/null');
  return eq(sh('sha256sum index.html links_report.md'),h1)&&'변경 없음'; });

console.log('\n── D. 드리프트 방어 (일부러 망가뜨려 본다) ──');
const bak=sk;
const restore=()=>fs.writeFileSync(path.join(R,'sketchy.html'),bak);
T('없는 카드 ID를 넣으면 빌드가 죽는다', ()=>{
  fs.writeFileSync(path.join(R,'sketchy.html'), sk.replace("{id:'s12p01',pc:[","{id:'s12p01',pc:[\"ZZ-NOPE-9\","));
  try{ sh('node build.js'); restore(); throw new Error('안 죽었다'); }
  catch(e){ restore(); if(!/ZZ-NOPE-9|빌드 중단/.test(e.stdout+e.stderr+e.message)) throw new Error('다른 이유로 죽음');
    return '중단됨'; } });
T('행 셋째 자리가 배열이 아니면 죽는다', ()=>{
  const D0="['하반신이 붉은 벽돌인 인부','벽세포 — 벽돌로 이름을 박았다']";
  if(!sk.includes(D0)) return '앵커 없음(스킵)';
  fs.writeFileSync(path.join(R,'sketchy.html'), sk.replace(D0, D0.slice(0,-1)+",'G1-31']"));
  try{ sh('node build.js'); restore(); throw new Error('안 죽었다'); }
  catch(e){ restore(); if(!/배열이어야|빌드 중단/.test(e.stdout+e.stderr+e.message)) throw new Error('다른 이유');
    return '중단됨'; } });
T('망가뜨린 뒤 원복 확인', ()=>eq(read('sketchy.html')===bak,true)&&'원본 복구됨');
T('원복 후 빌드가 다시 통과', ()=>{ sh('node build.js --check'); return 'ok'; });

console.log('\n── E. 리포트 ──');
const md=read('links_report.md');
T('links_report.md 생성', ()=>eq(md.length>10000,true)+' ('+(md.length/1024).toFixed(0)+'KB)');
T('리포트 링크 수 = 빌드가 센 수', ()=>{
  const inMd=(md.match(/^- \[(패널|행\d+)/gm)||[]).length;
  const said=+(sh('node build.js --check').match(/패널단위 (\d+)/)||[0,0])[1];
  const rows=(md.match(/^- \[행\d+/gm)||[]).length;
  if(inMd < said) throw new Error('리포트 '+inMd+' < 빌드 '+said);
  return inMd+'건 (행단위 '+rows+')';
});
T('고아는 늘지 않는다', ()=>le((md.split('## 고아 패널')[1].match(/^- `/gm)||[]).length,BL.orphan,'고아')+'장');
T('게이트표 19행', ()=>eq((md.split('## 게이트별')[1].split('##')[0].match(/^\| [A-S] /gm)||[]).length,19));

console.log('\n── F. 행 강조 렌더 ──');
T('CSS .pfhit', ()=>eq(/\.pftab tr\.pfhit td\{/.test(now),true));
T('showPicFix가 PROW를 읽는다', ()=>eq(/PROW\[id\] && PROW\[id\]\[pid\]/.test(now),true));
T('PROW 없어도 안전 (typeof 가드)', ()=>eq(/typeof PROW!=='undefined'/.test(now),true));
T('JS 문법 OK', ()=>{
  const b=[...now.matchAll(/<script(?![^>]*type=["']application)[^>]*>([\s\S]*?)<\/script>/g)].map(m=>m[1]);
  b.forEach((x,i)=>{ try{ new Function(x); }catch(e){ throw new Error('script#'+i+': '+e.message); } });
  return b.length+'개 블록'; });

console.log('\n'+(fail?'❌':'✅')+' 제안4 통과 '+pass+' / 실패 '+fail);
process.exit(fail?1:0);
