const L=require('./_lib');
L.ensure();
/* 과(lesson) 시험 오답 편지함 — SRS 가 열릴 때 편지함을 읽어 「이미 배운 카드만 · 벌점 없이 · 복습일만 오늘로」 당기는지.
   [2026-11-10] 사용자: 「오답도 SRS 일정에 반영하는게 나을거 같은데 버그가 안생기려나?」 — 그래서 불변식을 못 박는다:
   간격 · 난이도 · 틀린 횟수 · 상자는 그대로 · 안 배운 카드와 격리된 카드는 그대로 · 같은 편지는 한 번만 · 편지함은 비운다. */
const fs=require('fs'); const {JSDOM,VirtualConsole}=require('jsdom');
const FILE=process.argv[2]||require('path').join(L.ROOT,'index.html');
const html=fs.readFileSync(FILE,'utf8');
const CARDS=JSON.parse(html.match(/id=["']CARDS["'][^>]*>([\s\S]*?)<\/script>/)[1]);
const iso=d=>d.getFullYear()+'-'+String(d.getMonth()+1).padStart(2,'0')+'-'+String(d.getDate()).padStart(2,'0');
const today=iso(new Date()), later=(n)=>{ const d=new Date(); d.setDate(d.getDate()+n); return iso(d); };
const [A,B,C,D,E]=CARDS.filter(c=>c.t==='base').slice(0,5).map(c=>c.id);
const mk=(o)=>Object.assign({ef:2.3,iv:9,reps:4,lap:1,rich:0,box:4,due:later(7),lg:5,seen:true,ls:later(-2),sus:0},o);
const seed=()=>({v:3,exam:later(60),budget:120,newCap:20,sess:null,log:{},mig:0,rsn:{},sweep:{seen:{}},songs:{},
  states:{[A]:mk({}),[B]:mk({due:later(3),lap:7}),[C]:mk({seen:false,due:later(5)}),[D]:mk({sus:1}),[E]:mk({due:today})}});
function boot(store){
  const vc=new VirtualConsole(); const errs=[];
  vc.on('jsdomError',e=>{ const m=e.message.split('\n')[0]; if(!/scrollTo|Could not parse CSS/.test(m)) errs.push(m); });
  const dom=new JSDOM(html,{runScripts:'dangerously',pretendToBeVisual:true,url:'https://baeggman.github.io/biology2/',virtualConsole:vc,
    beforeParse(w){ for(const k in store) w.localStorage.setItem(k,store[k]); }});
  return {w:dom.window,errs};
}
let pass=0,fail=0;
const T=(n,f)=>{ try{ const m=f(); console.log('  ✓',n,m===undefined?'':'— '+m); pass++; } catch(e){ console.log('  ✗',n,'—',e.message); fail++; } };
const eq=(a,b,m)=>{ if(JSON.stringify(a)!==JSON.stringify(b)) throw new Error((m||'')+' 기대 '+JSON.stringify(b)+' 실제 '+JSON.stringify(a)); return true; };
console.log('\n── 과 시험 오답 편지함 ──');
const inbox=[{id:'111:s3',t:1,lesson:'L31a',sid:'s3',cards:[A,B,C,D,E,'없는-카드']}];
const before=seed();
const r1=boot({bio_srs_v1:JSON.stringify(before),lesson_srs_inbox:JSON.stringify(inbox)});
setTimeout(()=>{
  const db=JSON.parse(r1.w.localStorage.getItem('bio_srs_v1'));
  T('런타임 에러 0', ()=>{ if(r1.errs.length) throw new Error(r1.errs[0]); return 'clean'; });
  T('배운 카드는 복습일만 오늘로', ()=>eq([db.states[A].due,db.states[B].due],[today,today]));
  T('간격 · 난이도 · 틀린 횟수 · 상자 · 반복은 그대로', ()=>{ for(const id of [A,B]) for(const k of ['ef','iv','reps','lap','rich','box','lg','ls','seen','sus']) eq(db.states[id][k],before.states[id][k],id+'.'+k); return 'A · B'; });
  T('leech 직전 카드(틀림 7회)도 격리되지 않는다', ()=>eq([db.states[B].lap,db.states[B].sus],[7,0]));
  T('안 배운 카드는 그대로', ()=>eq(db.states[C],before.states[C]));
  T('격리된 카드는 그대로', ()=>eq(db.states[D],before.states[D]));
  T('이미 오늘인 카드는 그대로', ()=>eq(db.states[E],before.states[E]));
  T('없는 카드 id 는 상태를 만들지 않는다', ()=>eq('없는-카드' in db.states,false));
  T('편지함을 비운다 · 받은 표시를 남긴다', ()=>eq([r1.w.localStorage.getItem('lesson_srs_inbox'),!!(db.lin&&db.lin['111:s3'])],['[]',true]));
  T('오늘 로그 · 채점 분포를 더럽히지 않는다', ()=>eq([Object.keys(db.log||{}).length,db.mix===undefined||Object.values(db.mix).every(v=>!v)],[0,true]));
  T('홈에 알림이 뜬다', ()=>{ const el=r1.w.document.getElementById('lessonNote'); if(!el||el.classList.contains('hidden')) throw new Error('알림 없음'); if(!/2장/.test(el.textContent)) throw new Error(el.textContent); return el.textContent.trim().slice(0,40); });
  // 같은 편지를 다시 넣어도 두 번 받지 않는다 — 그사이 사용자가 A 를 복습해 복습일이 다시 미래로 갔다고 치자
  const db2=JSON.parse(JSON.stringify(db)); db2.states[A].due=later(12); db2.states[A].iv=12;
  const r2=boot({bio_srs_v1:JSON.stringify(db2),lesson_srs_inbox:JSON.stringify(inbox)});
  setTimeout(()=>{
    const d2=JSON.parse(r2.w.localStorage.getItem('bio_srs_v1'));
    T('같은 편지는 두 번 받지 않는다', ()=>eq(d2.states[A].due,later(12)));
    // 편지함이 없거나 깨져 있어도 조용히 넘어간다
    const r3=boot({bio_srs_v1:JSON.stringify(seed()),lesson_srs_inbox:'{깨진 글'});
    setTimeout(()=>{
      T('깨진 편지함에도 죽지 않는다', ()=>{ if(r3.errs.length) throw new Error(r3.errs[0]); const d3=JSON.parse(r3.w.localStorage.getItem('bio_srs_v1')); return eq(d3.states[A].due,later(7))&&'그대로'; });
      console.log('\n'+(fail?'❌':'✅')+' 오답 편지함 통과 '+pass+' / 실패 '+fail); process.exit(fail?1:0);
    },300);
  },300);
},300);
