# lesson/audio — 낭독 음성의 목록과 검수 기록

- **음성 파일(MP3)은 여기 두지 않는다.** 2026-11-20 부터 음성만 담는 저장소 [`BAEggman/biology2-audio`](https://github.com/BAEggman/biology2-audio)(GitHub Pages)에 둔다 — 주소 `https://baeggman.github.io/biology2-audio/<과>_<sid>_v<판>.mp3`. 같은 주소(baeggman.github.io) 아래라 브라우저에는 같은 사이트다: 재생 · 자동 넘김 · 「자동 시작」이 그대로 된다(첫 재생을 브라우저가 막으면 「시작」을 한 번 누르는 것도 전과 같다).
- 까닭: GitHub Pages 한 사이트의 한도가 1 GB 다. 이 저장소(그림 · 작업 파일 포함 약 0.5 GB)에 낭독 전체(약 0.7 GB)를 얹으면 넘친다.
- `manifest.json` — 구간마다 `{src(온전한 https 주소), text(그 구간의 say 그대로), status: "ready", sha256}`. 재생기(`lesson/narration-player.js`)는 `text` 가 지금 대본과 글자까지 같을 때만 녹음을 틀고, 아니면 기기 음성으로 읽는다.
- `reviews/` — 묶음마다의 검수 기록(누가 · 어떻게 들었나 · 사람 청취 여부). 2026-11-20 의 세 묶음은 옮기기 전 기록이라 `path` 가 옛 자리(`lesson/audio/…`)로 적혀 있다 — 파일은 이름 그대로 `biology2-audio` 에 있다(sha256 같음).
- 새 음성을 싣는 법: `tools/plan/2026-11-20/명세_낭독_제작_검수.md` §7 · §11. 올린 음성 파일의 이름을 바꾸거나 지우지 않는다 — 다시 녹음하면 판 번호를 올린 새 이름으로.
- `hold.json` — **검수 보류** 구간 `{과: {sid: 대장 항목 ID}}`. 손으로 고치지 않고 `python3 tools/audio/mkhold.py` 가 대장(`tools/audit/2026-11-20/issues.json`)에서 만든다 — 글을 아직 못 고친 최우선 · 「과학·범위」 중요 항목이 걸린 구간. 재생기는 이 구간을 스스로 읽지 않고(3.5초 뒤 다음 · 상태 「검수 보류 — 내용 확인 중」) 손으로 넘겼을 때만 기기 음성으로 읽는다(녹음은 틀지 않는다). `test/verify_hold.js` 가 파일과 대장이 같은지 · 재생기의 동작을 본다.
- `tools/audio/locked.json` 의 `다시_녹음` — 잠긴 구간 가운데 글이 바뀌어 manifest 에서 뺀 녹음(파일은 남김). 다시 만들면 판 번호를 올린다.
