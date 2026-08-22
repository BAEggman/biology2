#!/usr/bin/env node
/* 전체 검증 — node test/all.js   (필요: npm i jsdom) */
const {execSync}=require('child_process'), path=require('path');
const SUITES=[
  ['verify_links.js',  '제안1 · 죽은 링크 수리'],
  ['verify_picfix.js', '제안2 · 오답 복구 화면'],
  ['verify_build.js',  '제안4 · 빌드 파이프라인'],
  ['smoke_links.js',   '실구동 · 링크'],
  ['smoke_picfix.js',  '실구동 · 복구 화면'],
  ['verify_apply.js',  '제안5 · 승인 큐 주입기'],
  ['migrate_safe.js',  '실사용 DB 진도 보존'],
  ['verify_hooks.js',  '음성 후크 사전'],
];
let bad=[];
for(const [f,label] of SUITES){
  console.log('\n════ '+label+'  ('+f+')');
  try{ execSync('node '+path.join(__dirname,f),{stdio:'inherit'}); }
  catch(e){ bad.push(label); }
}
console.log('\n'+(bad.length?'❌ 실패: '+bad.join(', '):'✅ 전체 통과'));
process.exit(bad.length?1:0);
