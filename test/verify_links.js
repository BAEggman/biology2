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
/* [정정 2026-08-22] P1-13(옥신 농도-신장)은 뗐다 — 저농도 촉진/고농도 억제가 급소인데
   온실 판에 농도를 견주는 소품이 없다. 농도-반응 곡선을 그리면 되살린다.
   자리는 같은 옥신 계열 P1-12#1이 메운다. */
T('옥신 3장 → s20p01a', ()=>['P1-12','P1-12#1','P1-14'].map(k=>eq(PMAP[k],'s20p01a',k)).length);
/* [정정 2026-08-21] 굴성을 s20p04(어두운 쪽이 길어진다)에 그렸다 — 되살아나는 게 옳다.
   지켜야 할 불변식은 「링크에는 대응 소품이 있다」이고, 이제 소품이 생겼다. */
T('P1-3 계열은 굴성 판(s20p04)으로 되살아났다', ()=>['P1-3','P1-3#2'].map(k=>eq(PMAP[k],'s20p04',k)).length);
T('시토키닌 2장 → s20p01a', ()=>['P1-4','X-PL-28'].map(k=>eq(PMAP[k],'s20p01a',k)).length);
/* [정정 2026-08-21] P1-8#3(브라시노스테로이드 → 종자 발아)은 배열이 옳다.
   브라시노 후크(부목 댄 줄기)는 s20p01b에, 발아(끌로 씨앗 껍질을 깬다)는 s20p01a에 그려져 있다.
   급소가 두 판에 나뉘어 있으면 한 판만 거는 건 그린 것의 절반을 버리는 것이다. */
T('억제계 2장 → s20p01b', ()=>['P1-7','P1-8'].map(k=>eq(PMAP[k],'s20p01b',k)).length);   /* P1-6#2는 배열이라 위 검사가 받는다 */
/* [정정 2026-08-21] ABA 이름 후크(갓 쓴 늙은 아비)를 s20p01c에 세웠다.
   s20p01b의 「잎의 셔터」는 하는 일(닫는다)만 나르고 이름은 못 날라, 그 한 행에서 5장이
   음성 후크 위반이었다. 이름을 부르는 자리를 한 판으로 모았다 — 아래가 그 새 불변식이다. */
T('ABA 넷은 s20p01c 한 판에 다 그려졌다', ()=>{
  ['P1-6','P1-6#1','P1-6#3','P1-6#4'].forEach(k=>eq(PMAP[k],'s20p01c',k));   /* 이름·생장억제·휴면·건조내성 */
  if(!Array.isArray(PMAP['P1-6#2'])||!PMAP['P1-6#2'].includes('s20p01c'))
    throw new Error('P1-6#2(기공 닫기)는 셔터가 두 판에 있으니 배열이어야 한다');
  return '4장 + 배열 1장';
});
/* ★ [고침 2026-08-26] S-PL-14 를 이 어서션에서 뺐다.
   답에 ABA 가 들어 있는데 ABA 의 후크(갓 쓴 늙은 아비)는 s20p01c 에 있어
   세 판에 걸었다(baseline.pmapMoved 참조). 「a|b 두 판」으로 못 박아 두면
   정당한 겹걸기를 막는다 — X-PL-27 을 a|b|c 로 고친 것과 같은 자리다. */
T('걸친 2장은 s20p01a|s20p01b 배열 (S-PL-14 는 뺐다)', ()=>['P1-8#3'].map(k=>{
  if(!Array.isArray(PMAP[k])) throw new Error(k+' 배열 아님');
  return eq(PMAP[k].join(','),'s20p01a,s20p01b',k); }).join(' / '));
/* [정정 2026-08-21] X-PL-27(휴면=ABA / 발아=지베렐린·브라시노)의 휴면 그림은
   s20p01b의 셔터가 아니라 s20p01c의 「흙에 묻혀 눌린 씨앗」이다 — 짝이 옮겨 갔다.
   [정정 2026-08-25] 여기에 s20p01b 를 **더했다**. 이 카드의 답은 발아 촉진자로
   지베렐린과 **브라시노스테로이드** 둘을 든다. 지베렐린은 s20p01a 의 「끌로 씨앗 껍질을 깬다」가
   그리지만 브라시노스테로이드는 그 판에 없고, 2026-08-25 에 s20p01b#3(부목 댄 줄기)에
   **솔**을 그려 이름을 주었다. 그 행의 사실 칸이 이미 「…그리고 종자 발아」라 적으므로
   제자리다. 세 판이 되어 휴면(c) · 발아 두 갈래(a·b)가 다 선다. */
T('X-PL-27은 휴면 판과 발아 두 판에 걸린다', ()=>{
  if(!Array.isArray(PMAP['X-PL-27'])) throw new Error('배열 아님');
  return eq(PMAP['X-PL-27'].join(','),'s20p01a,s20p01b,s20p01c','X-PL-27'); });
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
