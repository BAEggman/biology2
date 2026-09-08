# tools/repro — 진짜 브라우저로 버그를 재현하는 자리

jsdom 스모크(`test/smoke_picfix.js`)가 통과하는데도 사용자가 겪는 버그가 있었다.
2026-09-06 의 「정답 미리보임」이 그랬다 — 전파는 이미 막혀 있었고, 진짜 원인은 **연타**였다.
사람 손의 리듬(Space 두 번 · 탭 두 번)은 합성 이벤트로는 안 나온다. 그래서 playwright 로
실제 클릭·실제 탭을 넣어 본다.

```
node tools/repro/repro_picfix.js   # 데스크톱 클릭 · 모바일 탭 — 「계속」 한 번
node tools/repro/repro2.js         # Space 연타 · 더블클릭 · 두 번 탭  ← 여기서 잡혔다
node tools/repro/repro3.js         # 잠금이 정상 조작을 막지 않는지
```

★ 재현이 되면 **먼저 스모크에 그 길을 적고**(실패하는 것을 확인한 뒤) 고친다.
