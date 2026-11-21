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
  ['verify_srslink.js','카드 ↔ 그림 링크 이음매'],
  ['smoke_lessoninbox.js','과 시험 오답 편지함'],
  ['verify_lock.js','그림 · 글 잠금(L17e — 11-19 사용자 만족분)'],
  ['verify_saytext.js','낭독 대본 문(제어문자 · 어미 · 언어 복구 44 · 과 142 / 정거장 1,598)'],
  ['verify_hold.js','검수 보류 — hold.json 이 대장과 같고 재생기가 보류 구간을 스스로 읽지 않음'],
  ['verify_tts.js','낭독 입력 — ttsNorm(say)에 로마자 · 그리스 · 첨자 · 과 번호 0 · 소문자 낱말은 사전 · 본보기 쌍 · 과 화면에 끼움'],
  ['verify_audio.js','녹음 목록 — manifest = 지금 say · 음성 저장소 주소 · 검수 기록 · heard · 상태 글(준비 중 → AI 검수 / 들어 봄)'],
];
let bad=[];
for(const [f,label] of SUITES){
  console.log('\n════ '+label+'  ('+f+')');
  try{ execSync('node '+path.join(__dirname,f),{stdio:'inherit'}); }
  catch(e){ bad.push(label); }
}
console.log('\n'+(bad.length?'❌ 실패: '+bad.join(', '):'✅ 전체 통과'));
process.exit(bad.length?1:0);
