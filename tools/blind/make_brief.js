#!/usr/bin/env node
/* 묶음 번호를 주면 세 단계의 브리프를 만든다.  node tools/blind/make_brief.js 0 */
const fs=require('fs'), path=require('path');
const R=path.join(__dirname,'..','..');
const man=JSON.parse(fs.readFileSync(path.join(__dirname,'manifest.json'),'utf8'));
const batches=JSON.parse(fs.readFileSync(path.join(__dirname,'batches.json'),'utf8'));
const resv=fs.readFileSync(path.join(__dirname,'reservations.md'),'utf8');
const b=+process.argv[2]; const ids=batches[b]; const tag='b'+String(b).padStart(2,'0');
const M=Object.fromEntries(man.map(m=>[m.pid,m]));
const outDir=path.join(__dirname,'out');
function shuffle(a){ a=a.slice(); for(let i=a.length-1;i>0;i--){const j=(i*7919+b*31)%(i+1); [a[i],a[j]]=[a[j],a[i]];} return a; }

/* ── 1단계 ── */
let s1=`# 블라인드 테스트 1단계 — 차가운 훑기 (묶음 ${tag})

당신은 한의대·편입 생물학 시험을 준비하는 학생이다. 아래 그림들은 그 시험을 위한 **기억술(mnemonic) 그림**이다 —
그림 속 물건 하나하나가 생물학 개념 하나를 나른다(소리가 비슷하거나, 모양이 닮았거나, 하는 일이 같거나, 자리가 뜻을 진다).
이 덱은 **같은 물건을 여러 판에서 같은 뜻으로** 쓰지만, 지금 당신은 그 약속을 모른다고 치자.

판마다 아래를 한다. **그림 말고는 아무것도 참고하지 마라** — 다른 파일을 열지 마라.
1. 그림에 보이는 **물건·사람·동작·배치**를 빠짐없이 적는다. 작은 것도, 배경도, 개수와 위치도. (한 줄에 하나)
2. 물건마다 그 단원의 생물학에서 **무엇을 뜻할지 짐작**한다. 모르면 「모름」. 짐작의 근거(소리/모양/뜻/자리)도 한 마디.
3. **헷갈리는 자리**를 적는다 — 서로 비슷해 보이는 물건 둘, 너무 작아 못 읽겠는 것, 무엇인지 모를 물건, 글자처럼 보이는 것.
4. 이 그림이 **한 문장으로 무엇을 가르치려는지** 짐작한다.

결과는 판마다 JSON 파일 하나로 쓴다: \`${outDir}/<pid>.s1.json\`
\`\`\`json
{"pid":"…","objects":[{"obj":"물건 설명","guess":"짐작한 개념 또는 모름","why":"근거 한 마디"}],
 "confusing":["…"],"gist":"한 문장"}
\`\`\`
파일을 다 쓴 뒤 마지막 답으로 「1단계 끝 — <pid 목록>」만 적어라.

`;
for(const id of ids){ const m=M[id];
  s1+=`## ${m.pid}\n- 단원: ${m.unit} (장면 「${m.scene}」)\n- 판 제목: 「${m.title}」\n- 그림: ${path.join(__dirname,'png',m.pid+'.png')}\n\n`; }
fs.writeFileSync(path.join(__dirname,'brief',tag+'_s1.md'), s1);

/* ── 2단계 ── */
let s2=`# 블라인드 테스트 2단계 — 이름을 준 뒤 다시 보기 (묶음 ${tag})

이제 판마다 **그 그림이 가르치려는 개념의 이름 목록**을 준다(순서는 섞었다). 그리고 이 덱이 **모든 판에서 같은 뜻으로 쓰는 물건 약속**도 준다.
같은 그림을 다시 보고, 개념마다 **그림의 어느 물건이 그것을 나르는지** 가리켜라. 잇는 고리(소리 / 모양 / 글자 / 뜻 / 자리 / 개수)도 한 마디.
어느 물건도 그 개념을 나르지 못하면 「못 찾음」이라고 솔직히 적어라 — 억지로 끼워 맞추지 마라.
개념 하나에 물건이 둘 이상이면 다 적어라. 물건 하나가 개념 둘을 나르면 그것도 적어라.

결과: \`${outDir}/<pid>.s2.json\`
\`\`\`json
{"pid":"…","map":[{"concept":"개념 이름(준 그대로)","obj":"그림의 물건 또는 못 찾음","link":"소리/모양/글자/뜻/자리/개수 + 한 마디","sure":"높음/중간/낮음"}]}
\`\`\`
파일을 다 쓴 뒤 마지막 답으로 「2단계 끝」만 적어라.

## 덱 공통 약속 (모든 판에서 같다)
${resv}

`;
for(const id of ids){ const m=M[id];
  const labels=shuffle(m.rows.map(r=>r.label)).map((l,i)=>`${i+1}. ${l}`).join('\n');
  s2+=`## ${m.pid} 「${m.title}」\n- 그림: ${path.join(__dirname,'png',m.pid+'.png')}\n- 개념 목록:\n${labels}\n\n`; }
fs.writeFileSync(path.join(__dirname,'brief',tag+'_s2.md'), s2);

/* ── 3단계 · 채점 ── */
let s3=`# 블라인드 테스트 3단계 — 채점 (묶음 ${tag})

당신은 채점자다. 판마다 **정답표**(그 판의 소품 칸과 사실 칸)와, 그림만 보고 답한 **1단계 답**(\`<pid>.s1.json\`)과 이름을 준 뒤 답한 **2단계 답**(\`<pid>.s2.json\`)이 있다. 그림도 열어 보라.
정답표의 **행마다** 아래를 매겨라.
- \`seen\` — 1단계 답이 그 행의 물건을 **알아본** 적이 있는가 (설명이 달라도 같은 물건이면 Y). Y/N
- \`cold\` — 1단계 답의 짐작이 그 행의 개념과 맞는가. Y(맞다) / P(방향은 맞는데 구체가 틀리다) / N
- \`cued\` — 2단계 답이 그 행의 개념을 **그 행의 물건**에 제대로 이었는가. Y / P(물건은 맞는데 고리가 엉뚱하다, 또는 다른 물건에 이었다) / N(못 찾음·틀림)
- \`note\` — 한 줄. 특히 **N 인 까닭**: 안 그려졌나, 너무 작나, 다른 것으로 읽혔나, 이름이 안 서나.
판 전체에 대해 \`panel_note\` 한 줄 — 1단계의 「헷갈리는 자리」와 「한 문장 짐작」이 정답과 얼마나 맞았는지.

결과: \`${outDir}/<pid>.json\`
\`\`\`json
{"pid":"…","rows":[{"n":1,"seen":"Y","cold":"N","cued":"Y","note":"…"}],"panel_note":"…"}
\`\`\`
파일을 다 쓴 뒤 마지막 답으로 「채점 끝」만 적어라.

`;
for(const id of ids){ const m=M[id];
  s3+=`## ${m.pid} 「${m.title}」 (${m.unit})\n- 그림: ${path.join(__dirname,'png',m.pid+'.png')}\n- 1단계 답: ${path.join(outDir,m.pid+'.s1.json')}\n- 2단계 답: ${path.join(outDir,m.pid+'.s2.json')}\n- 정답표:\n`;
  for(const r of m.rows) s3+=`  ${r.n}. 소품: ${r.prop}\n     사실: ${r.fact.slice(0,220)}\n`;
  s3+='\n'; }
fs.writeFileSync(path.join(__dirname,'brief',tag+'_truth.md'), s3);
console.log(tag, ids.join(' '));
