const L=require('./_lib');
const FX=L.ensure();
/* 제안 1 단독 검증 */
const fs=require('fs'), {JSDOM}=require('jsdom');
const NEW=require('path').join(L.ROOT,'index.html'), OLD=FX.BASE;
const h=fs.readFileSync(NEW,'utf8'), o=fs.readFileSync(OLD,'utf8');
let pass=0,fail=0;
const T=(n,f)=>{ try{ const m=f(); console.log('  ✓',n,m===undefined?'':'— '+m); pass++; }
                 catch(e){ console.log('  ✗',n,'—',e.message); fail++; } };
const eq=(a,b,m)=>{ if(String(a)!==String(b)) throw new Error((m||'')+' got '+a+' want '+b); return a; };
const J=(re,s)=>JSON.parse((s||h).match(re)[1]);

const PMAP=J(/var PMAP=(\{.*?\});/s), PTIT=J(/var PTIT=(\{.*?\});/s);
const ALL=require(FX.DATAJSON).flatMap(s=>s.panels.map(p=>p.id));
const flat=v=>Array.isArray(v)?v:[v];

console.log('\n── 죽은 링크 ──');
T('깨진 참조 0', ()=>eq(Object.values(PMAP).flatMap(flat).filter(p=>!ALL.includes(p)).length,0));
T('s20p01/s12p02 잔존 0', ()=>eq(Object.values(PMAP).flatMap(flat).filter(p=>['s20p01','s12p02'].includes(p)).length,0));
T('옥신 5장 → s20p01a', ()=>['P1-3','P1-3#2','P1-12','P1-13','P1-14'].map(k=>eq(PMAP[k],'s20p01a',k)).length);
T('시토키닌 2장 → s20p01a', ()=>['P1-4','X-PL-28'].map(k=>eq(PMAP[k],'s20p01a',k)).length);
T('억제계 5장 → s20p01b', ()=>['P1-6','P1-6#2','P1-7','P1-8','P1-8#3'].map(k=>eq(PMAP[k],'s20p01b',k)).length);
T('걸친 2장은 배열', ()=>['S-PL-14','X-PL-27'].map(k=>{
  if(!Array.isArray(PMAP[k])) throw new Error(k+' 배열 아님');
  return eq(PMAP[k].join(','),'s20p01a,s20p01b',k); }).join(' / '));
T('G1-95 → s12p02a', ()=>eq(PMAP['G1-95'],'s12p02a'));
T('G1-26 오태깅 삭제', ()=>{ if(PMAP['G1-26']) throw new Error('아직 있음'); return 'ok'; });
T('삭제는 G1-26 하나뿐', ()=>eq(Object.keys(J(/var PMAP=(\{.*?\});/s,o)).filter(k=>!(k in PMAP)).join(','),'G1-26'));
T('PMAP 706 → 705', ()=>eq(Object.keys(PMAP).length,705));
T('카드ID 전부 실재', ()=>{
  const ids=new Set(JSON.parse(h.match(/id=["']CARDS["'][^>]*>([\s\S]*?)<\/script>/)[1]).map(c=>c.id));
  return eq(Object.keys(PMAP).filter(k=>!ids.has(k)).length,0); });

console.log('\n── PTIT ──');
T('106패널 전수', ()=>eq(Object.keys(PTIT).length,106));
T('누락 0', ()=>eq(ALL.filter(p=>!PTIT[p]).length,0));
T('유령 0 (s20p01·s12p02 제거)', ()=>eq(Object.keys(PTIT).filter(p=>!ALL.includes(p)).length,0));
T('s31·s32·s33 제목 생김', ()=>['s31p01','s32p01','s33p03'].map(p=>{
  if(!PTIT[p]) throw new Error(p+' 없음'); return p; }).length+'개 확인');

console.log('\n── 커버리지 ──');
T('커버 패널 80 → 83', ()=>eq(new Set(Object.values(PMAP).flatMap(flat)).size,83));
T('고아 26 → 23', ()=>{
  const u=new Set(Object.values(PMAP).flatMap(flat));
  return eq(ALL.filter(p=>!u.has(p)).length,23); });

console.log('\n── 회귀 ──');
T('CARDS 무변경', ()=>{ const g=s=>s.match(/id=["']CARDS["'][^>]*>([\s\S]*?)<\/script>/)[1];
  return eq(g(h)===g(o),true)&&'동일'; });
T('EXAM 무변경', ()=>{ const g=s=>s.match(/id=["']EXAM["'][^>]*>([\s\S]*?)<\/script>/)[1];
  return eq(g(h)===g(o),true)&&'동일'; });
T('localStorage 키 무변경', ()=>eq((h.match(/KEY\s*=\s*['"]([^'"]+)/)||[])[1],'bio_srs_v1'));
/* 이 둘은 v10a 시점의 성질이다 — 현재 HEAD가 아니라 그때 스냅샷을 본다 */
T('v10a 시점엔 picFix 미도입', ()=>eq(/picFix/.test(fs.readFileSync(FX.STAGE1,'utf8')),false));
T('script 개수 동일', ()=>eq((h.match(/<script/g)||[]).length,(o.match(/<script/g)||[]).length));
T('JS 문법 OK', ()=>{
  const b=[...h.matchAll(/<script(?![^>]*type=["']application)[^>]*>([\s\S]*?)<\/script>/g)].map(m=>m[1]);
  b.forEach((x,i)=>{ try{ new Function(x); }catch(e){ throw new Error('script#'+i+': '+e.message); } });
  return b.length+'개 블록'; });
T('jsdom 파싱 + 필수 엘리먼트', ()=>{
  const d=new JSDOM(h).window.document;
  return eq(['picLink','grades','ansBlock','qText','aText'].filter(i=>!d.getElementById(i)).length,0); });
T('v10a 용량 증가 ≤10KB', ()=>{   /* v10a 시점의 성질 — 현재 HEAD가 아니다 */
  const dd=fs.statSync(FX.STAGE1).size-fs.statSync(OLD).size;
  if(dd>10*1024) throw new Error((dd/1024).toFixed(1)+'KB'); return '+'+(dd/1024).toFixed(1)+'KB'; });

console.log('\n'+(fail?'❌':'✅')+' 제안1 통과 '+pass+' / 실패 '+fail);
process.exit(fail?1:0);
