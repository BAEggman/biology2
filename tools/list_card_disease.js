#!/usr/bin/env node
/* 「목록 카드 병」 진단 — 답이 목록인 통합본이 여러 판에 한 조각씩 걸린 자리.
 *
 * 왜 병인가
 *   「균류 5군은?」 처럼 답이 목록인 카드를 다섯 판에 하나씩 걸면, 학생은 어느 판을
 *   봐도 목록 전체를 못 떠올린다. 그리고 음차·후크 감사는 그 판이 안 그린 나머지
 *   이름을 전부 미달로 잡는다 — 감사가 틀린 게 아니라 연결이 틀린 것이다.
 *
 * ★★ [판정 2026-08-25] **데이터가 아니라 감사가 틀렸다.**
 *   index.html 의 showPicFix() 를 읽어 보면 PMAP 에 든 **판을 전부 펼쳐** 그림과
 *   사실표를 나란히 그리고, 링크 글도 「🖼 그림으로 보기 — 제목A + 제목B」로 이어 붙인다.
 *   즉 배열 카드의 학생은 **여러 판을 한 화면에서 본다**. 목록이 나뉘어 있어도 다 보인다.
 *   그러니 통합본을 뗄 이유가 없다 — 뗄 것이 아니라 감사의 증거 범위를 넓히는 것이 맞다.
 *   audit_loanwords.js 를 「그 카드가 걸린 판 전부의 합」으로 고쳤고 174 → 152장이 됐다.
 *
 *   ⚠ 그래도 이 도구는 남긴다. 통합본이 **엉뚱한 판**에 걸린 경우를 찾는 데 쓴다 —
 *   판이 둘인데 한쪽이 답과 아무 상관 없으면 그건 진짜 잘못된 연결이다.
 *
 * 쓰기: node tools/list_card_disease.js          → 요약
 *       node tools/list_card_disease.js --full   → 판·행까지
 */
const fs=require('fs'), path=require('path');
const R=path.dirname(__dirname);
const s=fs.readFileSync(path.join(R,'sketchy.html'),'utf8');
const i=s.indexOf('[', s.indexOf('const DATA'));
let d=0,q=null,e=false,end=0;
for(let k=i;k<s.length;k++){const c=s[k];
 if(q){if(e){e=false;continue}if(c==='\\'){e=true;continue}if(c===q)q=null;continue}
 if(c==='"'||c==="'"||c==='`'){q=c;continue}
 if(c==='[')d++;else if(c===']'){d--;if(!d){end=k+1;break}}}
const DATA=eval('('+s.slice(i,end)+')');
const CARDS=JSON.parse(fs.readFileSync(path.join(R,'index.html'),'utf8')
  .match(/id=["']CARDS["'][^>]*>([\s\S]*?)<\/script>/)[1]);
const A={}; for(const c of CARDS) A[c.id]=c;
const strip=x=>String(x==null?'':x).replace(/<[^>]+>/g,'');

/* 통합본 → 분할본 목록 */
const splits={};
for(const c of CARDS){ const m=String(c.id).match(/^(.+)#(\d+)$/); if(m) (splits[m[1]]=splits[m[1]]||[]).push(c.id); }

/* 카드 → [{panel,row}] */
const where={};
for(const sc of DATA) for(const p of (sc.panels||[])) (p.f||[]).forEach((r,k)=>{
  for(const id of (r[2]||[])) (where[id]=where[id]||[]).push({p:p.id,k,prop:strip(r[0])});
});

const rows=[];
for(const [id, locs] of Object.entries(where)){
  if(/#\d+$/.test(id)) continue;                 /* 분할본 자신은 건너뛴다 */
  const panels=[...new Set(locs.map(x=>x.p))];
  if(panels.length<2) continue;                  /* 한 판에만 있으면 병이 아니다 */
  const sp=splits[id]||[];
  const spLinked=sp.filter(x=>where[x]);
  rows.push({id, panels, locs, sp, spLinked, a:strip((A[id]||{}).a||''), q:strip((A[id]||{}).q||'')});
}
rows.sort((x,y)=> (y.sp.length-x.sp.length) || (y.panels.length-x.panels.length));

const full=process.argv.includes('--full');
const withSp=rows.filter(r=>r.sp.length);
console.log('여러 판에 걸린 통합본 '+rows.length+'장 · 그중 분할본이 있는 것 '+withSp.length+'장');
console.log('  → 분할본이 있으면 통합본을 떼고 분할본만 건다\n');
for(const r of (full?rows:withSp)){
  console.log((r.sp.length?'★ ':'  ')+r.id.padEnd(10)+' 판 '+r.panels.length+' · 분할본 '+r.sp.length
    +'(걸린 것 '+r.spLinked.length+')  '+r.q.slice(0,48));
  console.log('     A: '+r.a.slice(0,100));
  console.log('     걸린 곳: '+r.locs.map(x=>x.p+'#'+x.k).join(' '));
  if(r.sp.length) console.log('     분할본: '+r.sp.map(x=>x+(where[x]?'('+[...new Set(where[x].map(y=>y.p+'#'+y.k))].join(',')+')':'✗미연결')).join(' '));
  console.log();
}
