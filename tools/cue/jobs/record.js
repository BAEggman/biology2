#!/usr/bin/env node
/* record.js — 6+1 일감이 바꾼 정거장(hook · obj)을 tools/cue/jobs/index.json 에 건다(2026-11-23 · 상시 요청 지시서 §2 ③).
 *   node tools/cue/jobs/record.js <일감 폴더 이름> L07b|s1 L07b|s3 …       — 그 일감(6+1 을 실제로 돌린 폴더)의 결정으로 바꿈
 *   node tools/cue/jobs/record.js <고르기 일감 폴더> L15a|s9 …               — 사용자가 고르기 화면에서 고른 고리(picks.json). 그 과의 심판 확인 기록 확인_<과>.md 가 있어야 한다
 *   node tools/cue/jobs/record.js --why 다듬음 "<무엇을 왜>" L07b|s1 …      — 고리가 아닌 글자 다듬기(맞춤법 · 띄어쓰기 · 낱말 손질)
 * 지금의 hook · obj 해시를 적는다 — 기록한 뒤 다시 바꾸면 또 걸어야 한다. */
const fs = require('fs'), path = require('path');
const { current, jobOk, jobCovers, ROOT } = require('./cuehash');
const IDX = path.join(ROOT, 'tools/cue/jobs/index.json');
const a = process.argv.slice(2); if (!a.length) { console.error('쓰는 법은 파일 머리'); process.exit(2); }
const idx = fs.existsSync(IDX) ? JSON.parse(fs.readFileSync(IDX, 'utf8')) : { '_뜻': '', '일감': {}, '다듬음': [] };
const cur = current(), today = new Date().toISOString().slice(0, 10);
const pick = ks => { const o = {}; for (const k of ks) { if (!cur[k]) { console.error('없는 정거장: ' + k); process.exit(2); } o[k] = cur[k]; } return o; };
if (a[0] === '--why') {
  const why = a[1], note = a[2], ks = a.slice(3);
  if (why !== '다듬음' || !note || !ks.length) { console.error('--why 다듬음 "<까닭>" 정거장…'); process.exit(2); }
  idx['다듬음'].push({ '날짜': today, '까닭': note, '닿은': pick(ks) });
} else {
  const job = a[0], ks = a.slice(1);
  const jd = path.join(ROOT, 'tools/cue/jobs', job);
  if (!jobOk(jd)) { console.error('6+1 을 돌린 흔적(packet · r?_가 ~ 바 · r?_judge)도, 사용자 고름 기록(picks.json + 확인_<과>.md)도 없는 일감: ' + job); process.exit(1); }
  const nc = ks.filter(k => !jobCovers(jd, k));
  if (nc.length) { console.error('이 과의 심판 확인 기록(확인_<과>.md — 카드 사실 · 예약 기호)이 없다: ' + nc.join(' ')); process.exit(1); }
  const j = idx['일감'][job] = idx['일감'][job] || { '날짜': today, '닿은': {} };
  Object.assign(j['닿은'], pick(ks));
}
fs.writeFileSync(IDX, JSON.stringify(idx, null, 1) + '\n');
console.log('기록함 —', a[0] === '--why' ? '다듬음' : a[0], a.filter(x => /\|s\d/.test(x)).join(' '));
