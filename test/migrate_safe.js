const L=require('./_lib');
const FX=L.ensure();
/* 실사용 DB(도입 2166장 상당)를 심어놓고 새 index.html을 올렸을 때 진도가 보존되는지 */
const fs=require('fs'),{JSDOM,VirtualConsole}=require('jsdom'),{execSync}=require('child_process');
const NEW=fs.readFileSync(require('path').join(L.ROOT,'index.html'),'utf8');
const OLD=execSync('git show '+L.baseline()+':index.html',{cwd:L.ROOT,maxBuffer:1e9}).toString();
const CARDS=JSON.parse(OLD.match(/id=["']CARDS["'][^>]*>([\s\S]*?)<\/script>/)[1]);

// 1) 옛 버전에서 실제로 학습한 것처럼 DB를 만든다
const vc=new VirtualConsole();
let dom=new JSDOM(OLD,{runScripts:'dangerously',pretendToBeVisual:true,url:'https://x.io/',virtualConsole:vc});
let w=dom.window;
setTimeout(()=>{
  const K='bio_srs_v1';
  let db=JSON.parse(w.localStorage.getItem(K)||'null');
  if(!db){ console.log('초기 DB 없음 — 앱이 저장하도록 세션 시작'); const b=w.document.getElementById('startBtn'); b.disabled=false; b.click(); db=JSON.parse(w.localStorage.getItem(K)); }
  // 2166장 도입 + 상자/간격/함정/오답로그를 흉내낸다
  const today=new Date().toISOString().slice(0,10);
  db.states={}; db.log={}; db.log[today]=[];
  CARDS.slice(0,2166).forEach((c,i)=>{
    db.states[c.id]={ef:2.1+(i%7)/10, iv:(i%30)+1, reps:(i%5)+1, lap:i%3, rich:i%4===0?2:0,
      box:(i%6)+1, due:today, lg:[5,4,3,2,1,0][i%6], seen:true, ls:today, sus:i%97===0?1:0};
    if(i<400) db.log[today].push({i:c.id,g:i%6,t:1});
  });
  db.exam='2027-01-01'; db.budget=260; db.newCap=31; db.mix={5:900,4:200,3:400,2:100,1:300,0:266};
  const snapshot=JSON.stringify(db);
  const nStates=Object.keys(db.states).length;
  const sample=['S-PL-1','G1-31','I0-54'].filter(id=>db.states[id]).map(id=>id+':box'+db.states[id].box+',iv'+db.states[id].iv);

  // 2) 새 버전으로 그 DB를 연다
  const dom2=new JSDOM(NEW,{runScripts:'dangerously',pretendToBeVisual:true,url:'https://x.io/',virtualConsole:vc});
  const w2=dom2.window;
  w2.localStorage.setItem(K, snapshot);
  // load()는 스크립트 실행 시 이미 돌았으므로 다시 띄운다
  const dom3=new JSDOM(NEW,{runScripts:'dangerously',pretendToBeVisual:true,url:'https://x.io/',virtualConsole:vc});
  const w3=dom3.window;
  w3.localStorage.setItem(K, snapshot);
  const dom4=new JSDOM(NEW,{runScripts:'dangerously',pretendToBeVisual:true,url:'https://x.io/',
    virtualConsole:vc, beforeParse(win){ win.localStorage.setItem(K, snapshot); }});
  const w4=dom4.window;
  setTimeout(()=>{
    let p=0,f=0; const T=(n,fn)=>{try{const m=fn();console.log('  ✓',n,m===undefined?'':'— '+m);p++;}catch(e){console.log('  ✗',n,'—',e.message);f++;}};
    const after=JSON.parse(w4.localStorage.getItem(K));
    console.log('\n── 기존 진도 보존 ──');
    T('states 2166장 그대로', ()=>{ const n=Object.keys(after.states||{}).length;
      if(n!==nStates) throw new Error(n+' / 기대 '+nStates); return n+'장'; });
    T('상자·간격이 안 바뀜', ()=>{
      const s2=['S-PL-1','G1-31','I0-54'].filter(id=>after.states[id]).map(id=>id+':box'+after.states[id].box+',iv'+after.states[id].iv);
      if(s2.join('|')!==sample.join('|')) throw new Error(s2.join('|')+' ≠ '+sample.join('|'));
      return s2.join(' '); });
    T('함정(rich) 보존', ()=>{ const a=Object.values(after.states).reduce((x,s)=>x+(s.rich||0),0);
      const b=Object.values(JSON.parse(snapshot).states).reduce((x,s)=>x+(s.rich||0),0);
      if(a!==b) throw new Error(a+' ≠ '+b); return a; });
    T('격리(sus) 보존', ()=>{ const a=Object.values(after.states).filter(s=>s.sus).length;
      const b=Object.values(JSON.parse(snapshot).states).filter(s=>s.sus).length;
      if(a!==b) throw new Error(a+' ≠ '+b); return a+'장'; });
    T('오답 로그 400건 보존', ()=>{ const n=(after.log[Object.keys(after.log)[0]]||[]).length;
      if(n!==400) throw new Error(n); return n+'건'; });
    T('설정(시험일·예산·신규상한) 보존', ()=>{
      if(after.exam!=='2027-01-01'||after.budget!==260||after.newCap!==31)
        throw new Error(after.exam+'/'+after.budget+'/'+after.newCap);
      return after.exam+' · '+after.budget+'/day · 신규 '+after.newCap; });
    T('DB.v 그대로 3 (마이그레이션 미발동)', ()=>{ if(after.v!==3) throw new Error('v='+after.v); return 'v3'; });
    T('picFix 기본 켬 (필드 없어도 동작)', ()=>{
      if(after.picFix!==undefined && after.picFix!==1) throw new Error('picFix='+after.picFix);
      return after.picFix===undefined?'필드 없음 → !==0 이므로 켜짐':'1'; });
    T('홈 화면이 진도를 반영해 그려짐', ()=>{
      const home=w4.document.getElementById('home');
      if(!home||home.classList.contains('hidden')) throw new Error('홈 안 보임');
      if(!home.textContent.trim()) throw new Error('빈 화면');
      return 'ok'; });
    console.log('\n'+(f?'❌':'✅')+' 진도 보존 '+p+' / 실패 '+f);
    process.exit(f?1:0);
  },1200);
},900);
