#!/usr/bin/env node
/* 구간 단위 잠금 규칙 — tools/audio/stoprules.py (2026-11-22 덧붙임 지시 §4.1)
   ① 열린 항목은 그 항목의 sids 구간만 「안 됨」 · ② grp 가 걸린 과는 모든 구간 「안 됨」
   · 그림 범위 항목의 상자와 겹치는 구간은 「볼 것 — 다시 그릴 구역」 · 닫힌 항목은 막지 않음
   · triage.py · lock_stops.py 가 같은 모듈을 쓴다(규칙이 둘로 갈리지 않게). */
const {execFileSync}=require('child_process'), path=require('path'), fs=require('fs');
const R=path.join(__dirname,'..');
const py=`
import sys, json
sys.path.insert(0, ${JSON.stringify(path.join(R,'tools/audio'))})
from stoprules import classify
L = {'stops': [
  {'sid':'s1','say':'a','box':None},
  {'sid':'s2','say':'b','box':[[0,0,100,100]]},
  {'sid':'s3','say':'c','box':[[50,50,100,100]]},
  {'sid':'s4','say':'d','box':[400,400,50,50]},
]}
def kinds(iss): return {s:v[0] for s,v in classify('LXXx', issues=iss, lesson=L).items()}
it = lambda **k: dict({'id':'LXXx-01','lesson':'LXXx','sids':['s3'],'state':'reproduced','fix0':'글'}, **k)
out = {
 'text_s3': kinds([it()]),
 'closed':  kinds([it(state='verified')]),
 'grp':     kinds([it(grp='복제공사장')]),
 'basis':   kinds([it(grp='기본서대조')]),
 'pic':     kinds([it(fix0='그림')]),
 'picscope':kinds([it(fix0='글', scope='그림(구역)')]),
 'textpic': kinds([it(fix0='글→그림')]),
 'other':   kinds([it(lesson='LYYy')]),
}
print(json.dumps(out))
`;
const o=JSON.parse(execFileSync('python3',['-c',py]).toString());
let bad=0; const ok=(c,m)=>{console.log((c?'  ✓ ':'  ✗ ')+m); if(!c) bad++;};
const eq=(a,b)=>JSON.stringify(a)===JSON.stringify(b);
ok(eq(o.text_s3,{s1:'넘음',s2:'넘음',s3:'안 됨',s4:'넘음'}),'항목이 s3 에만 닿으면 s3 만 안 됨 ①');
ok(eq(o.closed,{s1:'넘음',s2:'넘음',s3:'넘음',s4:'넘음'}),'닫힌(verified) 항목은 막지 않는다');
ok(Object.values(o.grp).every(k=>k==='안 됨'),'grp 가 걸린 과는 모든 구간 안 됨 ②');
ok(eq(o.basis,o.text_s3),'「기본서대조」 표시는 기호 묶음이 아니다');
ok(eq(o.pic,{s1:'넘음',s2:'볼 것',s3:'안 됨',s4:'넘음'}),'그림 항목: 상자가 겹치는 s2 는 볼 것(다시 그릴 구역) · 안 겹치는 s4 · 상자 없는 s1 은 넘음');
ok(eq(o.picscope,o.pic),'scope 가 있으면 fix0 보다 scope 를 본다');
ok(eq(o.textpic,o.text_s3),'「글→그림」은 글 범위로 본다(구역 표시 없음)');
ok(eq(o.other,{s1:'넘음',s2:'넘음',s3:'넘음',s4:'넘음'}),'다른 과의 항목은 막지 않는다');
for(const f of ['tools/audio/triage.py','tools/audio/run/lock_stops.py','tools/audit/2026-11-20/dropped.py']){
  const src=fs.existsSync(path.join(R,f))?fs.readFileSync(path.join(R,f),'utf8'):'';
  ok(/from stoprules import[^\n]*classify/.test(src),f+' 가 stoprules.classify 를 쓴다');
}
console.log(bad?'\n❌ 잠금 규칙 '+bad+'곳 실패':'\n✅ 잠금 규칙(구간 단위) 통과');
process.exit(bad?1:0);
