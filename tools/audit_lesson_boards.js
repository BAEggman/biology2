#!/usr/bin/env node
/* audit_lesson_boards.js — 문 3 · 판 낱말(2026-11-23 · 11-19 지시서 §4.3 · 상시 요청 지시서 §4).
 * obj(보이는 것)에 판 · 화살표 · 글자를 적은 정거장을 찾는다 — 사건이 나르지 않고 판이 설명하는 그림(채점표 P4 · 부호 D1 · D2 · D3)의 글 쪽 흔적.
 * 허용은 tools/cue/boards_ok.json(「과|sid」 → 「허용 — 까닭」 · 채점표 §8 의 허용 꼴). 글에 안 적힌 판은 눈 검사가 잡는다.
 * 사용: node tools/audit_lesson_boards.js [--json]   · 모듈: require(...).scan() → [{과, sid, 낱말, 허용}] */
const fs = require('fs'), path = require('path');
const { ROOT, lessons, strip } = require('./lesson_lib');
const WORDS = /(간판|안내판|표지판|말풍선|확대경|돋보기 속|모니터|화면|포스터|훈련판|칠판|도표|그래프|화살표|벽보|차트|글자|명찰|이름표|게시판|설계도|지도판|표지)/g;
function scan() {
  const OKF = path.join(ROOT, 'tools/cue/boards_ok.json'), OK = fs.existsSync(OKF) ? JSON.parse(fs.readFileSync(OKF, 'utf8'))['허용'] || {} : {};
  const out = [];
  for (const L of lessons()) for (const s of L.stops) { const w = [...new Set(strip(s.obj).match(WORDS) || [])]; if (w.length) out.push({ 과: L.id, sid: s.sid, 낱말: w, 허용: OK[L.id + '|' + s.sid] || null }); }
  return out;
}
function byLesson(rs) { const m = {}; for (const L of lessons()) m[L.id] = 0; for (const r of rs) if (!r.허용) m[r.과]++; return m; }
module.exports = { scan, byLesson, WORDS };
if (require.main === module) { const r = scan(); if (process.argv[2] === '--json') console.log(JSON.stringify(r)); else { for (const x of r) console.log(x.과, x.sid, x.낱말.join(' · '), x.허용 ? '(허용)' : ''); console.log('정거장', r.length, '· 과', new Set(r.map(x => x.과)).size, '· 허용', r.filter(x => x.허용).length); } }
