const L=require('./_lib');
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
T('pc가 83개 패널에 삽입', ()=>eq((sk.match(/,pc:\[/g)||[]).length,83));
T('pc 역변환하면 원본과 동일', ()=>{
  const orig=fs.readFileSync(FX.BASESK,'utf8');   /* v12 기준본 */
  const back=sk.replace(/(\{id:'[sd]\d+p\d+[ab]?')\,pc:\[[^\]]*\]\,/g,'$1,');
  return eq(back===orig,true)&&'삽입 외 변경 0';
});
T('사실표 590행 유지', ()=>{
  const D=eval('('+(()=>{ const s=sk, st=s.indexOf('[',s.indexOf('const DATA')); let d=0,q=null,e=false;
    for(let k=st;k<s.length;k++){const c=s[k];
      if(q){if(e){e=false;continue}if(c==='\\'){e=true;continue}if(c===q)q=null;continue}
      if(c==='"'||c==="'"||c==='`'){q=c;continue}
      if(c==='[')d++;else if(c===']'){d--;if(!d)return s.slice(st,k+1)}}})()+')');
  return eq(D.reduce((a,s)=>a+s.panels.reduce((x,p)=>x+(p.f||[]).length,0),0),590);
});

console.log('\n── B. 빌드 산출물 == 손으로 만든 v10b 지도 ──');
const now=read('index.html'), prev=fs.readFileSync(FX.STAGE2,'utf8');   /* v10b — 손으로 만든 지도 */
const norm=o=>Object.fromEntries(Object.entries(o).map(([k,v])=>[k,(Array.isArray(v)?v:[v]).slice().sort().join('|')]));
T('PMAP 705장 그대로', ()=>eq(Object.keys(J(now,'PMAP')).length,705));
T('PMAP 값이 한 건도 안 바뀜', ()=>{
  const a=norm(J(prev,'PMAP')), b=norm(J(now,'PMAP'));
  const d=Object.keys(a).filter(k=>a[k]!==b[k]);
  return eq(d.length,0)+'건 차이'; });
T('PTIT·PBR·PFACT 동일', ()=>['PTIT','PBR','PFACT']
  .map(n=>eq(JSON.stringify(J(prev,n))===JSON.stringify(J(now,n)),true,n)).length+'개');
T('PNOIMG 동일', ()=>eq(JSON.parse(now.match(/var PNOIMG=(\[.*?\]);/s)[1]).join()
                       ===JSON.parse(prev.match(/var PNOIMG=(\[.*?\]);/s)[1]).join(),true));
T('PROW 신설 (지금은 0건)', ()=>eq(Object.keys(J(now,'PROW')).length,0)+'건 — 제안5 대상');
T('BUILD 마커 존재', ()=>eq(/\/\*BUILD:START[\s\S]*?BUILD:END\*\//.test(now),true));
T('CARDS 무변경', ()=>{ const g=s=>s.match(/id=["']CARDS["'][^>]*>([\s\S]*?)<\/script>/)[1];
  return eq(g(now)===g(prev),true)&&'동일'; });

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
T('707개 링크가 전부 적힘', ()=>eq((md.match(/^- \[(패널|행\d+)/gm)||[]).length,707));
T('고아 23장 명시', ()=>eq((md.split('## 고아 패널')[1].match(/^- `/gm)||[]).length,23));
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
