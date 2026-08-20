const L=require('./_lib');
const BL=require('./baseline.json');
const ge=(a,b,m)=>{ if(!(a>=b)) throw new Error((m||'')+' '+a+' < 기준 '+b+' — 연결이 줄었다(회귀)'); return a; };
const le=(a,b,m)=>{ if(!(a<=b)) throw new Error((m||'')+' '+a+' > 기준 '+b+' — 고아가 늘었다(회귀)'); return a; };
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
/* [정정 2026-08-20] P1-3·P1-3#2는 뗐다. 답이 「생산 부위 + 신장 + 정단우성 + 굴광성·굴중성」인데
   s20p01a에는 신장과 정단우성만 그려져 있고 굴광성·굴중성은 덱 어디에도 없다.
   근거는 baseline.pmapRemoved에 있고, 굴성을 그리면 되살린다. 「그린 것만 건다」. */
T('옥신 3장 → s20p01a', ()=>['P1-12','P1-13','P1-14'].map(k=>eq(PMAP[k],'s20p01a',k)).length);
T('P1-3은 뗀 채로 남아 있다 (굴성 미작화)', ()=>eq(PMAP['P1-3']===undefined&&PMAP['P1-3#2']===undefined,true));
T('시토키닌 2장 → s20p01a', ()=>['P1-4','X-PL-28'].map(k=>eq(PMAP[k],'s20p01a',k)).length);
T('억제계 5장 → s20p01b', ()=>['P1-6','P1-6#2','P1-7','P1-8','P1-8#3'].map(k=>eq(PMAP[k],'s20p01b',k)).length);
T('걸친 2장은 배열', ()=>['S-PL-14','X-PL-27'].map(k=>{
  if(!Array.isArray(PMAP[k])) throw new Error(k+' 배열 아님');
  return eq(PMAP[k].join(','),'s20p01a,s20p01b',k); }).join(' / '));
T('G1-95 → s12p02a', ()=>eq(PMAP['G1-95'],'s12p02a'));
/* [정정] v10a는 G1-26을 「어느 패널에도 대응 소품이 없다」는 이유로 지웠다.
   s12p04(회장 문 — 비타민 결핍)를 그리면서 그 소품이 생겼으므로 되살아나는 게 옳다.
   지켜야 할 불변식은 「링크에는 대응 소품이 있다」이고, 행 단위 링크가 그 증거다. */
T('G1-26이 있다면 행 단위여야 한다 (대응 소품 증명)', ()=>{
  if(!PMAP['G1-26']) return '아직 미연결 — 허용';
  const PROW=J(/var PROW=(\{.*?\});/s,h);
  if(!PROW['G1-26']) throw new Error('패널 단위로만 걸렸다 — 대응 소품이 증명되지 않는다');
  return '행 단위 '+JSON.stringify(PROW['G1-26']);
});
T('v10a에 있던 링크가 사라지지 않았다', ()=>{
  const P0=J(/var PMAP=(\{.*?\});/s,o);
  const RM=BL.pmapRemoved||{};                 /* 「그린 것만 건다」로 뗀 것 — baseline에 근거가 있어야 통과 */
  const gone=Object.keys(P0).filter(k=>!(k in PMAP)).filter(k=>{
    const r=RM[k]; if(r&&r.why) return false;
    return true; });
  return eq(gone.join(','),'')||'0건 소실';
});
T('PMAP은 줄지 않는다', ()=>ge(Object.keys(PMAP).length,BL.pmap,'PMAP')+'장');
T('카드ID 전부 실재', ()=>{
  const ids=new Set(JSON.parse(h.match(/id=["']CARDS["'][^>]*>([\s\S]*?)<\/script>/)[1]).map(c=>c.id));
  return eq(Object.keys(PMAP).filter(k=>!ids.has(k)).length,0); });

console.log('\n── PTIT ──');
T('패널 수는 줄지 않는다 · PTIT과 자기일관', ()=>{
  ge(ALL.length,BL.panels,'패널');
  return eq(Object.keys(PTIT).length,ALL.length,'PTIT 키 == 패널 수')&&(ALL.length+'패널');
});
T('누락 0', ()=>eq(ALL.filter(p=>!PTIT[p]).length,0));
T('유령 0 (s20p01·s12p02 제거)', ()=>eq(Object.keys(PTIT).filter(p=>!ALL.includes(p)).length,0));
T('s31·s32·s33 제목 생김', ()=>['s31p01','s32p01','s33p03'].map(p=>{
  if(!PTIT[p]) throw new Error(p+' 없음'); return p; }).length+'개 확인');

console.log('\n── 커버리지 ──');
T('커버 패널은 줄지 않는다', ()=>ge(new Set(Object.values(PMAP).flatMap(flat)).size,BL.cover,'커버')+'장');
T('고아 26 → 23', ()=>{
  const u=new Set(Object.values(PMAP).flatMap(flat));
  return le(ALL.filter(p=>!u.has(p)).length,BL.orphan,'고아')+'장'; });

console.log('\n── 회귀 ──');
/* ⚠ 「CARDS 5531 무변경」이라는 고정값 테스트였다. v17이 신경·감각·근육 카드 148장을
   정당하게 추가하자 깨졌다 — 마스터노트 §10이 말한 그 병의 여덟 번째다.
   불변식으로 바꾼다: 기존 카드가 유실·변형되지 않으면 통과. 추가는 진도이므로 허용한다. */
T('기존 카드가 유실·변형되지 않는다 (추가는 허용)', ()=>{
  const P=s=>JSON.parse(s.match(/id=["']CARDS["'][^>]*>([\s\S]*?)<\/script>/)[1]);
  const now=new Map(P(h).map(c=>[c.id,JSON.stringify(c)]));
  const bad=P(o).filter(c=>now.get(c.id)!==JSON.stringify(c));
  if(bad.length) throw new Error('유실·변형 '+bad.length+'장: '+bad.slice(0,5).map(c=>c.id).join(','));
  return P(o).length+'장 보존 · 현재 '+now.size+'장'; });
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
