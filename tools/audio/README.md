# 녹음 묶음 도는 법 (2026-11-21 · Opus 5.5)

녹음 묶음만 이어 가는 세션은 이 쪽 · `tools/plan/2026-11-20/명세_낭독_제작_검수.md` · 지시서 §15 부터 끝 · `locked.json` 의 `_뜻` 만 읽고 시작한다. 인계문 전문은 다시 읽지 않는다(내용은 감사 대장 `tools/audit/2026-11-20/issues.json` 에 있다 — 글 · 그림 일감을 열 때만 대장 줄 번호로 그 과 대목을 읽는다).

## 지킬 것(속도 때문에 건너뛰지 않는다)
- `locked.json` 에 있는 구간만 녹음. 구간 단위 잠금 ①~⑤(⑤ 그 구간의 글 · 과학을 직접 읽기).
- 보내기 전 대본 sha256 맞추기 → 따로 연 Gemini 가 원문 없이 받아 적기 → 다른 곳만 필청 A/B → 뜻이 바뀌면 다시. 떨어진 것은 싣지 않고 까닭을 적는다.
- 올린 뒤 Pages 200 · sha256 확인. 번들 앞 `node test/all.js`.
- Gemini 탭 둘 · 새 대화 사이 1분 이상. 확인 화면 · 로그인 · 한도는 사용자에게.
- 만든 수 · AI 검수 통과 · 사람 청취 · 공개 확인을 따로 센다. 사람 청취는 사용자가 말할 때만 `lesson/audio/heard.json`.

## 한 묶음의 흐름(파이프라인 — 탭이 놀지 않게)
1. **눈 검사(한 묶음 앞서)** — `python3 tools/cue/mkreaders.py <L> /tmp/eyeN/<L>`(답 열쇠 `<L>.key.json` 은 판 밖으로 옮긴다) → sonnet 독자 ㄱ·ㄴ·ㄷ 를 배경으로(동시 20 안) · 지시문은 `tools/kit/` 의 독자 틀(판 폴더만 읽게).
2. **분류 → 잠금** — `python3 tools/audio/triage.py /tmp/eyeN /tmp/eyekeysN <L>...` 로 구간마다 넘음/볼 것/안 됨 표 → 볼 것은 손으로 · ⑤ 글 읽기 → `python3 tools/audio/run/lock_stops.py`(같은 규칙 · 쪽지 `승급/<L>.md` · 원문 `눈검사/<L>/`) → `node test/all.js` → 커밋.
3. **대본** — `OUT=… node tools/audio/run/mktts.js <L>...`(ttsNorm · {L_sid:{t,h}}) → `python3 tools/audio/scan_misread.py <json>` 로 오독 기록 낱말 · 낱글자 · 수 찾기 → 사전 줄은 생성 때 EXTRA 로.
4. **대본을 Gemini 에** — 기기 `~/Downloads/b2audio/` 에 commit → stage → Gemini 탭에 `<input type=file>` 을 만들어 file_upload → `localStorage.b2tts2` 에 합침.
5. **생성** — 새 대화 · 태스크 모드 → `localStorage.b2gen`(= `run/gen.js`)을 AsyncFunction 으로: `(PRE, KS, EXCL, EXTRA, v, zip, TITLE)`. 대본 sha 가 하나라도 어긋나면 보내지 않는다. 한 그룹 11~17 구간.
6. **받기** — 「biology_X 다운로드」 버튼을 find → computer left_click(JS click 은 내려받지 않음) → 기기에서 `bash proc2.sh <zip> <tag>`(MP3 · 해시 `hashes_20261121.txt`) → `python3 split.py <tag>`(3.4MB 이하 `rv_<tag>_N.zip`).
7. **검수** — 새 대화 · 태스크 · 업로드 메뉴의 숨은 file-input 에 rv ZIP(둘까지 — 둘째는 메뉴를 다시 열고) → `run/review_prompt.txt`({N}) → 답이 오면 `eval(localStorage.b2cmp)`(= `run/compare.js`) → 다른 곳은 A/B 필청 질문을 같은 대화에.
8. **판정** — `DEC=… python3 run/dec.py <id_v> CLEAR|CLEAR_ALLOWED_VARIANT|REDO|HOLD <검수> [메모]`. 뜻이 바뀌면 REDO(사전 줄을 붙여 v2). 사전을 붙이고도 같은 낱말이 두 번 틀리면 HOLD(세션 끝에 방법을 바꿔 한 번에).
9. **공개** — 통과 MP3 를 stage → github.com/BAEggman/biology2-audio/upload/main 에 3.8MB 씩 file_upload(여러 번 쌓임) → 커밋 → 클론으로 sha · Pages 에서 fetch 로 200 · sha.
10. **기록** — `tools/audio/batches/<날짜>-batch-NN.json`(accepted · rejected_attempts · extra) → `python3 tools/audio/add_batch.py` → `node test/all.js` → 커밋 → 번들 `<GitHub main>..main` 을 Downloads 에(새 이름) → 청취표 `청취_*.md` · `batches/속도.md` 한 줄.

## 함정
- 긴 프롬프트를 넣으면 탭 제목이 프롬프트 전체가 된다 — `setInterval` 로 제목을 줄인다(스크린샷 · 탭 목록이 넘친다).
- Gemini 탭을 셋 이상 · 새 대화를 잇달아 열면 CAPTCHA. 둘 · 1분 간격.
- device_commit_files 는 같은 이름을 캐시한다 — 새 이름으로.
- 기기 Downloads 에서는 지우기 권한이 없다 — `zip` 명령(임시 파일 바꿔치기)도 실패한다. zipfile 로 새 파일을 만든다.
- 받아 적기 JSON 은 `pre` 가 아니라 `div` 에 올 때도 있다 — 마지막 `message-content` 에서 첫 `{` 부터 괄호를 세어 자른다.
- 검수자의 「의→에」 · 띄어쓰기 · 수를 한글로 적기는 소리가 같아 허용. 낱말이 바뀌면 A/B 로 확인.
- 계정 이름 · Gemini 대화 주소 · 인계문 원문은 저장소에 넣지 않는다.

## 연장
| 파일 | 하는 일 |
|---|---|
| `run/gen.js` | 생성 요청(대본 sha 대조 · 태스크 모드 확인 뒤에만 보냄) |
| `run/review_prompt.txt` | 원문 없는 받아 적기 요청 |
| `run/compare.js` | 받아 적기 ↔ 대본 문장 대조 |
| `run/proc2.sh` · `run/split.py` | (기기) ZIP → MP3 · 해시 · 검수 ZIP |
| `run/mktts.js` | 잠긴 구간의 낭독 입력 JSON |
| `run/dec.py` | 구간 판정 기록 |
| `run/lock_stops.py` | 구간 단위 잠금(①~④ 기계 규칙 · 쪽지 · 원문 복사) |
| `triage.py` | 독자 결과 → 넘음/볼 것/안 됨 표 |
| `scan_misread.py` · `오독기록.json` | 잘 틀리는 낱말을 미리 사전에 |
| `add_batch.py` | 묶음 spec → manifest · reviews |
