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
  ['verify_answerkey.js','답 열쇠 · 이름 장부 — 군더더기(㉮)를 내지 않음 · 꼭 필요한 이름은 남김 · 면제마다 까닭 · 장부 줄마다 갈래 · 상태'],
  ['verify_stoprules.js','잠금 규칙 — 열린 항목은 닿는 구간만 · grp 는 과 전체 · 다시 그릴 구역은 볼 것 · triage · lock_stops · dropped 가 같은 규칙'],
  ['verify_names.js','문 1 이름 고리 — 과마다 N + N′ 가 늘지 않음 · 닫은 과 0 · N/N′ 짝은 모두 이름 장부에 · 감사 끝난 과의 장부 줄은 갈래 · 상태 · 새 면제 통만'],
  ['verify_canon.js','문 2 기호 일관 — canon.json 의 개념은 정본 물건으로 · 같은 물건 · 다른 뜻은 예외에만 · 기준선 밖 어긋남 0'],
  ['verify_boards.js','문 3 판 낱말 — obj 의 간판 · 말풍선 · 확대경 · 화면 · 화살표 · 글자 정거장이 늘지 않음 · 허용마다 까닭'],
  ['verify_standing.js','상시 요청 문 — CLAUDE.md · 상시요청.md 의 요청 여섯(상태 · 증거) · 「끝」의 증거 · 6+1 문(기준선 뒤 hook · obj 바꿈은 tools/cue/jobs 기록)'],
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
