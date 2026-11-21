#!/usr/bin/env node
/* verify_lock.js — 그림 · 글 잠금(tools/cue/lock.json)이 지켜지는지(2026-11-20 · 11-19 지시서 §4 · RUBRIC P12)
   잠긴 과마다: 글 해시 · 무손실 원본의 잠긴 구역 해시가 lock.json 과 같고, 공개 그림의 같은 구역이 원본과 문턱 안으로 같다.
   해시 계산은 tools/cue/lockhash.py(PIL). python3 · PIL 이 없으면 건너뛰고 그렇다고 알린다(통과로 치지 않음을 글로 남김). */
const fs=require('fs'), path=require('path'), {spawnSync}=require('child_process');
const ROOT=path.resolve(__dirname,'..');
const L=JSON.parse(fs.readFileSync(path.join(ROOT,'tools/cue/lock.json'),'utf8'));
const r=spawnSync('python3',[path.join(ROOT,'tools/cue/lockhash.py')],{encoding:'utf8'});
if(r.status!==0){ console.log('  ⚠ lockhash.py 를 못 돌림(python3 · PIL?) — 잠금 검사를 건너뜀\n'+(r.stderr||'').slice(0,300)); process.exit(0); }
let bad=0;
for(const line of r.stdout.trim().split('\n')){
  const g=JSON.parse(line), w=L[g.id];
  const t1=g['글']===w['글'], t2=g['그림']===w['그림'], t3=g['크기같음'] && g['공개그림차']!==null && g['공개그림차']<=(w['공개그림차_문턱']||2);
  console.log(`  ${t1?'✓':'✕'} ${g.id} 글  ${t2?'✓':'✕'} 원본 잠긴 구역(${g['픽셀수']} px)  ${t3?'✓':'✕'} 공개 그림의 그 구역(평균 차 ${g['공개그림차']})`);
  if(!(t1&&t2&&t3)) bad++;
}
console.log(bad?`\n❌ 잠금 깨짐 ${bad} — 사용자가 허락한 손질이면 lock.json 의 「까닭」에 그 말을 더하고 lockhash.py --write`:'\n✅ 잠금 그대로');
process.exit(bad?1:0);
