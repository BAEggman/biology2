#!/usr/bin/env node
// lesson_plan.js — 갈아엎기 계획표를 다시 그린다 → tools/notes/갈아엎기_계획.md (묶음을 기출 카드 많은 순 · 과 후보 수 · 진척)
// 사용: node tools/lesson_plan.js   (매 세션 끝에 한 번 돌려 두면 계획과 진척이 한 장에 남는다)
const fs = require('fs'), path = require('path'), { execSync } = require('child_process');
const { ROOT, lessons } = require('./lesson_lib');
const cover = JSON.parse(execSync('node ' + path.join(__dirname, 'lesson_cover.js') + ' --json', { encoding: 'utf8' }));
const Ls = lessons();
const today = new Date().toISOString().slice(0, 10);
const S = cover.filter(x => x.kind === 's'), D = cover.filter(x => x.kind === 'd');
const sum = a => a.reduce((t, x) => ({ r: t.r + x.rows, c: t.c + x.cards, rc: t.rc + x.rowsCovered, cc: t.cc + x.cardsCovered }), { r: 0, c: 0, rc: 0, cc: 0 });
const ts = sum(S), td = sum(D);
const est = x => Math.max(1, Math.round(x.rows / 12));
let md = `# 갈아엎기 계획 — 덱 전체를 Sketchy 식 과(lesson)로 (2026-11-08 시작 · 이 표는 \`node tools/lesson_plan.js\` 가 다시 그린다 · 마지막 ${today})

> 사용자 결정(2026-11-08): **기출 카드 많은 단원부터** · **옛 덱은 과가 다 설 때까지 옆에 두기**(lesson/index.html 이 새 입구 · 기출 카드는 과의 정거장 src 로 옮겨 단다) · **d 묶음(도해)은 s 묶음을 다 세운 뒤 결정**.
> 한 과 = 한 주제 · 한 장소 · 이름 말장난 테마 · 물건 하나 = 사실 하나 · 정거장 10~15 · 16:9 한 장 · 투어(내장 TTS) · 되짚기 · 그림만 복습 · 시험. 품질 문 = 사용자 본인의 유지 검사(시험 모드) · LLM 은 투어↔그림 일치만. 그림은 일치가 서면 고정(v2 는 사용자 점수 뒤에만).
> 과 ID = L + 묶음 번호 + 글자(L16a · L16b …). 만드는 절차는 \`tools/prompts/L31a_설계.md\` 가 본보기 — 설계(테마 · 정거장 · 고리) → 바탕(Argon · 16:9 · 한 턴) → 조각 고침(zcrop · affit · zpaste) → 일치 검사(sonnet 독자 1) → \`lessons/<ID>.json\`(src 로 옛 행 지목) → \`node tools/build_lesson.js <ID> --standalone DIR\` → 사용자 Downloads.

## s 묶음(단원) — 행 ${ts.rc}/${ts.r} · 기출 카드 ${ts.cc}/${ts.c} · 과 ${Ls.length} 개 / 후보 ≈ ${S.reduce((t, x) => t + est(x), 0)} 개
| 순서 | 묶음 | 단원 | 카드 | 행 | 과 후보 | 만든 과 | 덮인 행 | 덮인 카드 |
|---|---|---|---|---|---|---|---|---|
`;
S.forEach((x, i) => { md += `| ${i + 1} | ${x.id} | ${x.unit} | ${x.cards} | ${x.rows} | ${est(x)} | ${x.lessons.join(' · ')} | ${x.rowsCovered} | ${x.cardsCovered} |\n`; });
md += `\n## d 묶음(도해 · 자 같은 표) — 행 ${td.r} · 카드 ${td.c} · s 를 다 세운 뒤 장면으로 바꿀지 참고표로 둘지 결정\n| 묶음 | 이름 | 카드 | 행 |\n|---|---|---|---|\n`;
D.forEach(x => { md += `| ${x.id} | ${x.unit} | ${x.cards} | ${x.rows} |\n`; });
md += `\n## 만든 과\n| ID | 제목 | 정거장 | 묶음 | 상태 |\n|---|---|---|---|---|\n`;
for (const L of Ls) md += `| ${L.id} | ${L.title} | ${L.stops.length} | ${L.scene || ''} | ${L.status || 'v1 · 사용자 유지 검사 대기'} |\n`;
fs.writeFileSync(path.join(ROOT, 'tools/notes/갈아엎기_계획.md'), md);
console.log(`tools/notes/갈아엎기_계획.md · s 카드 ${ts.cc}/${ts.c} · 과 ${Ls.length}`);
