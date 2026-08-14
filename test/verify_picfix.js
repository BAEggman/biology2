const L=require('./_lib');
const BL=require('./baseline.json');
const ge=(a,b,m)=>{ if(!(a>=b)) throw new Error((m||'')+' '+a+' < 기준 '+b+' — 연결이 줄었다(회귀)'); return a; };
const le=(a,b,m)=>{ if(!(a<=b)) throw new Error((m||'')+' '+a+' > 기준 '+b+' — 고아가 늘었다(회귀)'); return a; };
const FX=L.ensure();
/* index.new.html 검증 스위트 — 제안 1·2 */
const fs=require('fs'), path=require('path');
const NEW=require('path').join(L.ROOT,'index.html'), OLD=FX.BASE, IMGDIR=require('path').join(L.ROOT,'img');
const h=fs.readFileSync(NEW,'utf8'), o=fs.readFileSync(OLD,'utf8');
let pass=0, fail=0;
const T=(name,fn)=>{ try{ const m=fn(); console.log('  ✓',name, m===undefined?'':'— '+m); pass++; }
                     catch(e){ console.log('  ✗',name,'—',e.message); fail++; } };
const eq=(a,b,m)=>{ if(String(a)!==String(b)) throw new Error((m||'')+' got '+a+' want '+b); return a; };
const grab=(re,s)=>{ const m=(s||h).match(re); if(!m) throw new Error('패턴 없음'); return m[1]; };

const PMAP=JSON.parse(grab(/var PMAP=(\{.*?\});/s));
const PTIT=JSON.parse(grab(/var PTIT=(\{.*?\});/s));
const PBR =JSON.parse(grab(/var PBR=(\{.*?\});/s));
const PFACT=JSON.parse(grab(/var PFACT=(\{.*?\});/s));
const PNOIMG=JSON.parse(grab(/var PNOIMG=(\[.*?\]);/s));
const DATA=(()=>{ const s=fs.readFileSync(FX.DATAJSON,'utf8'); return JSON.parse(s); })();
const ALL=DATA.flatMap(s=>s.panels.map(p=>p.id));

console.log('\n── A. 데이터 무결성 ──');
T('PTIT 키 == 실제 패널 수', ()=>eq(Object.keys(PTIT).length,ALL.length)+'패널');
T('PTIT에 유령 패널 없음', ()=>eq(Object.keys(PTIT).filter(p=>!ALL.includes(p)).length,0));
T('PTIT 누락 없음', ()=>eq(ALL.filter(p=>!PTIT[p]).length,0));
T('PBR 키 == 실제 패널 수', ()=>eq(Object.keys(PBR).length,ALL.length)+'패널');
/* 행 수를 상수로 박으면 사실표를 한 행 늘릴 때마다 깨진다. 소스와 대조한다. */
T('PFACT 행 수 == sketchy.html 사실표', ()=>{
  const src=L.parseDATA(fs.readFileSync(require('path').join(L.ROOT,'sketchy.html'),'utf8'))
    .reduce((a,s)=>a+s.panels.reduce((x,p)=>x+(p.f||[]).length,0),0);
  return eq(Object.values(PFACT).reduce((a,b)=>a+b.length,0), src)+'행 (소스와 일치)'; });
T('PFACT 모든 행이 2요소', ()=>eq(Object.values(PFACT).flat().filter(r=>r.length!==2).length,0));

console.log('\n── B. 제안 1: 죽은 링크 수리 ──');
const flat=v=>Array.isArray(v)?v:[v];
T('PMAP 깨진 참조 0', ()=>eq(Object.values(PMAP).flatMap(flat).filter(p=>!ALL.includes(p)).length,0));
T('s20p01/s12p02 잔존 0', ()=>eq(Object.values(PMAP).flatMap(flat).filter(p=>p==='s20p01'||p==='s12p02').length,0));
T('G1-26이 있다면 행 단위여야 한다', ()=>{
  if(!PMAP['G1-26']) return '아직 미연결 — 허용';
  const PROW=JSON.parse(h.match(/var PROW=(\{.*?\});/s)[1]);
  if(!PROW['G1-26']) throw new Error('패널 단위로만 걸렸다');
  return '행 단위';
});
T('옥신 카드 → s20p01a', ()=>['P1-3','P1-3#2','P1-12','P1-13','P1-14'].map(k=>eq(PMAP[k],'s20p01a',k)).length+'장');
T('ABA·에틸렌·브라시노 → s20p01b', ()=>['P1-6','P1-6#2','P1-7','P1-8','P1-8#3'].map(k=>eq(PMAP[k],'s20p01b',k)).length+'장');
T('시토키닌 계열 → s20p01a', ()=>['P1-4','X-PL-28'].map(k=>eq(PMAP[k],'s20p01a',k)).length+'장');
T('걸친 카드 2장은 배열', ()=>['S-PL-14','X-PL-27'].map(k=>{
  if(!Array.isArray(PMAP[k])) throw new Error(k+' 배열 아님');
  eq(PMAP[k].join(','),'s20p01a,s20p01b',k); return k; }).join(' '));
T('G1-95 → s12p02a', ()=>eq(PMAP['G1-95'],'s12p02a'));
T('PMAP은 줄지 않는다', ()=>ge(Object.keys(PMAP).length,BL.pmap,'PMAP')+'장');
T('v10a 링크가 하나도 사라지지 않았다', ()=>{
  const P0=JSON.parse(o.match(/var PMAP=(\{.*?\});/s)[1]);
  const gone=Object.keys(P0).filter(k=>!PMAP[k]);
  return eq(gone.join(','),'')||'0건 소실';
});
T('카드ID가 전부 실재', ()=>{
  const C=JSON.parse(h.match(/id=["']CARDS["'][^>]*>([\s\S]*?)<\/script>/)[1]);
  const ids=new Set(C.map(c=>c.id));
  return eq(Object.keys(PMAP).filter(k=>!ids.has(k)).length,0);
});
T('고아는 늘지 않는다', ()=>{
  const used=new Set(Object.values(PMAP).flatMap(flat));
  return le(ALL.filter(p=>!used.has(p)).length,BL.orphan,'고아')+'장 남음(제안3 대상)';
});
T('커버 패널 80 → 83', ()=>{
  const used=new Set(Object.values(PMAP).flatMap(flat));
  return ge(used.size,BL.cover,'커버')+'장 (s20p01a·s20p01b·s12p02a 부활)';
});

console.log('\n── C. 제안 2: 오답 복구 ──');
T('picFix DOM 존재', ()=>eq((h.match(/id="picFix"/g)||[]).length,1));
T('pfNext 생성 코드 존재', ()=>eq((h.match(/id="pfNext"/g)||[]).length,1));
T('CSS .picfix 존재', ()=>eq(/\.picfix\{/.test(h),true));
T('발동 조건 g<=3', ()=>eq(/g<=3 && pidList\(PMAP\[id\]\)\.length/.test(h),true));
T('DB.picFix 토글 반영', ()=>eq(/DB\.picFix!==0/.test(h),true));
T('설정 체크박스 존재', ()=>eq((h.match(/id="fPicFix"/g)||[]).length,1));
T('advance() 분리됨', ()=>eq((h.match(/function advance\(\)/g)||[]).length,1));
T('grade가 advance 호출', ()=>eq(/save\(\);\s*\n\s*if\(DB\.picFix!==0/.test(h),true));
T('키보드 picFixOn 분기', ()=>eq(/if\(picFixOn\)\{/.test(h),true));
/* [수정 2026-08-14] 「도해 11장」 고정값은 도해를 한 장 더 그리면 깨진다 — 그리는 것이 이 프로젝트의
   목적이다. 그런 테스트는 무시하게 되고, 무시되는 테스트는 없느니만 못하다(baseline.json의 _왜와 같은 이유).
   불변식은 「도해가 줄지 않는다」이고, 「기존 항목이 사라지지 않았다」는 아래 줄이 이미 따로 지킨다. */
T('도해는 줄지 않는다', ()=>ge(PNOIMG.length,BL.noimg,'도해')+'장');
T('PNOIMG가 전부 도해', ()=>eq(PNOIMG.filter(p=>!/^d0/.test(p)).length,0));

console.log('\n── D. 이미지 파일 ──');
const files=fs.readdirSync(IMGDIR).filter(f=>f.endsWith('.webp'));
T('이미지 파일 수 == 도해가 아닌 패널 수', ()=>{
  const noimg=JSON.parse(h.match(/var PNOIMG=(\[.*?\]);/s)[1]).length;
  ge(files.length,BL.images,'이미지');
  return eq(files.length, ALL.length-noimg, '이미지 == 패널-도해')+'장';
});
T('PNOIMG 외 전 패널에 파일 존재', ()=>{
  const miss=ALL.filter(p=>!PNOIMG.includes(p)).filter(p=>!fs.existsSync(path.join(IMGDIR,p+'.webp')));
  return eq(miss.length,0);
});
T('전부 RIFF/WEBP 헤더', ()=>{
  const bad=files.filter(f=>{ const b=fs.readFileSync(path.join(IMGDIR,f));
    return b.slice(0,4).toString()!=='RIFF' || b.slice(8,12).toString()!=='WEBP'; });
  return eq(bad.length,0);
});
/* [수정 2026-08-08] 상한을 12MB → 30MB.
   12MB 는 sketchy.html 이 같은 그림을 base64 로 한 벌 더 갖고 있던 시절의 값이다
   (img/ 11.9MB + sketchy 안 15.9MB = 27MB). 그 중복을 없앴으므로 img/ 만 남았고,
   상한의 목적은 「무한정 늘지 않게」 하나다. 30MB 면 패널 260장까지 간다. */
T('합계 ≤ 30MB', ()=>{ const t=files.reduce((a,f)=>a+fs.statSync(path.join(IMGDIR,f)).size,0);
  if(t>30*1048576) throw new Error((t/1048576).toFixed(1)+'MB'); return (t/1048576).toFixed(2)+'MB'; });
/* [신규 2026-08-08] 예전에는 sketchy.html 이 그림을 base64 로 품었고, img/ 만 갈아 끼우면
   두 화면이 조용히 갈라졌다(실제로 18장이 낡았고 7장은 src="" 빈칸이었다).
   이제 sketchy.html 도 img/ 경로를 쓴다 — 원본이 하나뿐이라 갈라질 수가 없다.
   되돌아가지 않도록 「base64 가 하나도 없고 경로를 쓴다」를 못 박는다. */
T('sketchy.html에 base64 그림이 없다', ()=>{
  const sk=fs.readFileSync(path.join(L.ROOT,'sketchy.html'),'utf8');
  const n=(sk.match(/data:image\/[a-z]+;base64/g)||[]).length;
  if(n) throw new Error(n+'건 — 그림은 img/ 에만 둔다 (tools/unembed_img.py)');
  if(/const IMG\s*=/.test(sk)) throw new Error('IMG 객체가 되살아났다');
  return (fs.statSync(path.join(L.ROOT,'sketchy.html')).size/1048576).toFixed(2)+'MB';
});
T('sketchy.html이 img/ 경로로 그림을 부른다', ()=>{
  const sk=fs.readFileSync(path.join(L.ROOT,'sketchy.html'),'utf8');
  if(!sk.includes('src="img/${p.id}.webp"')) throw new Error('경로 렌더가 없다');
  return 'img/${p.id}.webp';
});

console.log('\n── E. DOM · 회귀 ──');
const {JSDOM}=require('jsdom');
let dom;
T('jsdom 파싱', ()=>{ dom=new JSDOM(h,{runScripts:'outside-only'}); return 'ok'; });
T('필수 엘리먼트 전부 존재', ()=>{
  const need=['picLink','picFix','grades','ansBlock','qText','aText','fPicFix','fNew','setSave'];
  const miss=need.filter(i=>!dom.window.document.getElementById(i));
  return eq(miss.length,0)+'/'+need.length;
});
T('picFix 초기 hidden', ()=>eq(dom.window.document.getElementById('picFix').className.includes('hidden'),true));
T('script 개수 원본과 동일', ()=>eq((h.match(/<script/g)||[]).length,(o.match(/<script/g)||[]).length));
/* 고정값 5531 → 불변식 (§10). 카드가 느는 것은 진도다. 줄거나 바뀌는 것만 회귀다. */
T('기존 카드가 유실·변형되지 않는다 (추가는 허용)', ()=>{
  const P=x=>JSON.parse(x.match(/id=["']CARDS["'][^>]*>([\s\S]*?)<\/script>/)[1]);
  const now=new Map(P(h).map(c=>[c.id,JSON.stringify(c)]));
  const bad=P(o).filter(c=>now.get(c.id)!==JSON.stringify(c));
  if(bad.length) throw new Error('유실·변형 '+bad.length+'장: '+bad.slice(0,5).map(c=>c.id).join(','));
  return P(o).length+'장 보존 · 현재 '+now.size+'장';
});
T('EXAM 블록 무변경', ()=>{
  const g=s=>s.match(/id=["']EXAM["'][^>]*>([\s\S]*?)<\/script>/)[1];
  return eq(g(h)===g(o),true)&&'동일';
});
T('localStorage 키 무변경', ()=>{
  const k=s=>(s.match(/KEY\s*=\s*['"]([^'"]+)/)||[])[1];
  return eq(k(h),k(o));
});
T('JS 문법 (script 전체 파싱)', ()=>{
  const blocks=[...h.matchAll(/<script(?![^>]*type=["']application)[^>]*>([\s\S]*?)<\/script>/g)].map(m=>m[1]);
  blocks.forEach((b,i)=>{ try{ new Function(b); }catch(e){ throw new Error('script#'+i+': '+e.message); } });
  return blocks.length+'개 블록 OK';
});
/* 「v10a 대비 +150KB 이내」도 고정값이었다 (§10). 카드·q블록이 늘면 파일은 당연히 커진다.
   원래 노린 것은 「이번 변경이 파일을 확 부풀리지 않았나」이므로, baseline에 기록한
   직전 증가분 대비 여유(150KB)로 바꾼다. 배포할 때마다 baseline.idxDeltaKB를 올린다. */
T('index.html이 갑자기 부풀지 않는다 (직전 대비 +150KB 이내)', ()=>{
  const d=Math.round((Buffer.byteLength(h)-fs.statSync(OLD).size)/1024);
  const base=(BL.idxDeltaKB==null?d:BL.idxDeltaKB);
  if(d>base+150) throw new Error('직전 +'+base+'KB → 지금 +'+d+'KB (여유 150KB 초과)');
  return '+'+d+'KB (기준선 +'+base+'KB)'; });

console.log('\n'+(fail?'❌':'✅')+' 통과 '+pass+' / 실패 '+fail);
process.exit(fail?1:0);
