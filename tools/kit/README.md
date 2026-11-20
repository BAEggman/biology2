# tools/kit — 과를 짓는 세션이 쓰는 연장과 순서 (2026-11-14)

새 세션(새 컨테이너)에서도 그대로 일할 수 있게, 그동안 세션 임시 폴더에만 있던 연장과 순서를 여기에 모았다.
무엇을 · 어떤 차례로 할지는 `tools/plan/2026-11-14/지시서_Opus_만들것_고칠것.md`, 지난 내력과 배운 것은 `tools/audit/2026-11-10/인계서_새과.md`.

> **2026-11-20 보탬**: 지금의 차례는 `tools/plan/2026-11-20/지시서_Opus_인계문실행.md`(감사 246건 고치기 → 과 승급 → Gemini 낭독 → 통과한 것만 올림). 낭독 제작과 검수 = `tools/plan/2026-11-20/명세_낭독_제작_검수.md` · 대장 = `tools/audit/2026-11-20/README.md`. **`gen_<ID>.py --write` 앞에 `python3 tools/kit/gen_sync.py <ID> --check`** — 다른 도구가 JSON 만 고쳐 gen 42과가 낡아 있다.
>
> **2026-11-19 보탬**: 고리(소품 · 상황 · 이름 고리 · 그림 간 연결)를 정하는 법 = `tools/cue/README.md`(제안자 여섯 + 심판) · 잣대 = `tools/cue/RUBRIC.md` · 과를 짓거나 고칠 때 도는 문과 눈 검사 셋 = `tools/plan/2026-11-19/지시서_Opus_고리감사_고치기.md` §4. 아래 「과 하나의 길」의 2(사건 짓기)와 7(일치 검사)에 그것이 끼어든다.

| 파일 | 쓰임 |
|---|---|
| `gemini_helpers_1114.js` | Gemini 웹 탭에 넣는 도우미(`__prep` · `__go` · `__wait2` · `__pill`) |
| `grid.py` | 그림 한 구역을 키워 좌표 눈금을 얹음 — 상자 · 구역 편집 · PIL 좌표 잡기 |
| `일치검사_프롬프트.md` | 독자(sonnet)에게 주는 글의 틀과 결과 다루는 법 |
| `cardfull.js` | 카드의 모든 칸(q · a · it · cz · n · 자식) 보기 |
| `card_edit_note.py` | 고친 카드를 `test/baseline.json` 의 `cardEdits` 에 적기 |
| `tcommit.sh` | 전부 커밋(귀속 줄은 환경변수로 · 토큰 꼴 문자열이 있으면 멈춤) |

다른 연장(이미 저장소에 있음): `tools/prompts/zone3.py`(구역 편집 오리기 · 붙이기) · `restore_poly.py`(붙인 뒤 이웃 물건만 원래대로) · `mkcheck2.py`(일치 검사 판) · `s13_lib.py`(PIL 선 · 배지 · 단추) · `where.js`(카드가 걸린 과) · `tools/audit/boxtry.py`(상자 대 보기) · `tools/audit/apply_patch.py`(과 글 · 카드 고침) · `tools/plan/tally.js`(남은 카드 셈) · `tools/card.js`.

## 0. 저장소 준비
- 연장 여럿이 경로 `/tmp/b2` 를 박아 쓴다 → **저장소는 `/tmp/b2` 에** 둔다.
- 있으면 그대로. 없으면(새 컨테이너):
  ```sh
  git -c credential.helper= clone https://github.com/BAEggman/biology2.git /tmp/b2     # 공개 읽기 — 자격 증명 없이
  cd /tmp/b2 && npm install                                                               # jsdom(테스트)
  pip install pillow numpy opencv-python-headless scipy --break-system-packages         # 없을 때만
  ```
- GitHub main 이 지시서의 「시작 커밋」보다 뒤처져 있으면: 사용자 컴퓨터 `~/Downloads` 의 `b2_hNN.bundle` 들을 `device_stage_files` 로 가져와 **번호 차례로** `git pull /mnt/user-data/uploads/Downloads/b2_hNN.bundle main`.
- 끝으로 `node build.js --check && node test/all.js` 가 통과하는지 본다. `git config user.name / user.email` 이 비어 있으면 커밋이 안 된다(값은 앞 커밋의 것을 따른다 — `git log -1 --format='%an <%ae>'`).

## 1. 과 하나의 길 (사건 장면 방식 — L13c 부터)
1. **카드 읽기** `node tools/plan/tally.js ids "<그림 이름 조각>"` → `node tools/kit/cardfull.js <ids>` · 옛 판 행(`python3 tools/get_row.py` · `node tools/show_rows.js`) → 사실을 정거장으로 묶는다(물건 하나 = 사실 하나).
2. **사건 짓기** 누가 누구에게 무엇을 하는 한 순간. 사실은 그 속의 행동 · 소품. 예약(`tools/hooks.json` 의 `_심볼예약` · `lesson/symbols.html`)과 부딪치지 않는지 grep. → `tools/prompts/<ID>_설계.md`.
3. **출연진 그림**(그 세계의 인물 · 소품을 한 장에 — 이어 짓는 세계는 그 세계 과의 그림에서 오려 모으고, 새 세계는 Gemini 로 먼저 한 장) → `<ID>_src/cast_ref.webp`.
4. **S1 장면 통째**(Gemini 카본 높음 · 출연진 그림을 올림) → 1024 폭으로 오면 2048×1144 로 키움.
5. **구역 편집**(틀린 몸짓 · 가림 · 빠진 소품 · 인과) → **PIL**(개수 · 자리 · 옮기기 · 빛깔 · 배지) → 다시 만드는 길 `<ID>_build.sh`(같은 픽셀인지 확인) · 원본은 `<ID>_src/*.webp`(무손실).
6. **글** `gen_<ID>.py --write` → `lessons/<ID>.json`(obj = 보이는 것만 · fact ≤ 60자 · hook · say ≤ 560자 · box · cards / src) → 그림 `lesson/img/<ID>.webp`(`Image.save(…, 'WEBP', quality=85, method=6)`).
7. **일치 검사**(`일치검사_프롬프트.md`) ✕ 0 까지 + 끝 그림 · 끝 글로 한 번 더.
8. **예약** `reserve_<ID>.py`(새 물건 · 바뀐 꼴을 `_심볼예약` 에) → `python3 tools/lesson_sid.py <ID>` · `node tools/build_lesson.js <ID>`(기호 사전 수가 줄지 않았는지) · `node build.js` · `node build.js --check` · `node test/all.js`.
9. **셈** `node tools/plan/tally.js pic` 에서 그 그림이 ✅ 인지.
10. **커밋 · 번들 · 문서 · 보고**(아래 4).

본보기: `tools/prompts/L13d_설계.md` · `L13d_prompt_scene.txt` · `L13d_build.sh` · `L13d_pil.py` · `gen_L13d.py` · `reserve_L13d.py`(새 과) / `L13b_*2*`(다시 지은 과).

## 2. Gemini 몰기 (Claude in Chrome)
- 탭: 사용자의 Chrome 에 열린 gemini.google.com. 모드 알약이 **「카본 높음」**이어야 한다(사용자 지시 — Flash · 다른 모드 금지). `__pill()` 로 확인하고, 아니면 사용자에게 알린다.
- 도우미 넣기: `gemini_helpers_1114.js` 를 javascript_tool 로 실행. 프롬프트는 `window.__T = {S1:"…", Z1:"…"}` 로 넣어 둔다(파일로도 `<ID>_prompt_scene.txt` 에 남긴다).
- 그림 한 장:
  1. 새 채팅(왼쪽 위 「새 채팅」 — 화면을 찍어 자리를 확인) → 3초.
  2. `await __prep('LABEL')` → find `"file input labeled LABEL"` → `file_upload`(올릴 파일은 **세션이 내준 폴더** `/mnt/user-data/outputs/<ID>/` 에 있어야 한다).
  3. 3초 뒤 `await __go(window.__T.X)` — 돌려준 `thumbs` 가 비었으면 그림이 안 붙은 것.
  4. 30 ~ 90초 뒤 `await __wait2('LABEL')`(아직이면 `pending:true` — 더 기다린다) → 사용자의 `~/Downloads/LABEL_<ms>.png`.
  5. `device_stage_files(["/Users/mac/Downloads/LABEL_<ms>.png"])` → `/mnt/user-data/uploads/Downloads/` 에서 꺼내 쓴다.
- 같은 채팅에서 이어 고치기(「방금 그림에서 이것만」)는 새로 올리지 않고 `__go(prompt)` 만.
- 받은 그림은 **반드시 눈으로**(`grid.py` 로 키워서) 본다 — 글자 · 숫자 · 손가락 · 겹침 · 시킨 것만 바뀌었는지. Gemini 는 「NO buttons」 같은 금지를 어긴다(지우고 센다).
- 약관 · 동의 · 로그인 창이 뜨면 멈추고 사용자에게 알린다(2026-11-14 의 「동의」 한 번은 그때 그 창에만 준 허락).

### 프롬프트 뼈대
- **장면(S1)**: `The attached picture shows the cast of a clean medical mnemonic cartoon (bold black ink outlines, flat bright colors, big clear shapes, cute and funny): <출연진 낱낱이>. Draw ONE wide 16:9 cartoon SCENE in exactly the same drawing style with these SAME kinds of characters. It must look like one lively moment in a story — NOT like a diagram, NOT like characters standing in a row: figures overlap at different depths and everyone is busy doing something.` + `PLACE:` + `WHAT HAPPENS (one connected story, from left to right): 1. … 2. …` + 끝에 `Leave the chests of all … plain and clearly visible. Nobody wears any badge. No text, letters or numbers anywhere.`
- **구역 편집**: `Edit the attached picture. Keep exactly the same drawing style (bold black ink outlines, flat bright colors) and keep <그대로 둘 것 낱낱이> exactly as they are, with only this change: <바꿀 것 하나>. No text, letters or numbers anywhere.`
- 배지 · 단추 · 개수는 Gemini 에게 시키지 않는다(PIL). 단추 · 배지가 올 자리(가슴 · 조끼 앞)는 「비워 두라」고 처음부터 적는다.

## 3. 구역 편집 · PIL
```sh
python3 tools/prompts/zone3.py crop  base.png z N x0 y0 x1 y1        # z/up_N.png(긴 변 1024)을 Gemini 에 올린다
python3 tools/prompts/zone3.py paste base.png z N z/gem_N.png out.png "ax0,ay0,ax1,ay1[;…]"   # 허용 상자 안만 바뀐다
python3 tools/prompts/restore_poly.py base.png out.png "x,y;x,y;…" 1.0                        # 상자에 걸린 이웃 물건은 원래 픽셀로
python3 tools/kit/grid.py out.png x0,y0,x1,y1 3 /tmp/g.png 10                                  # 키워서 확인
```
- 붙인 뒤 출력의 `inliers` 가 한 자리 수이거나 `상자별 옮김` 의 셋째 값(띠 차이)이 크면 정합이 틀렸거나 Gemini 가 틀을 다시 짠 것 — 쓰지 않는다.
- Gemini 는 **더하는 편집**(물보라 · 띠 · 얼굴 · 몸짓)은 틀을 지키고 **옮기는 편집**(물건을 다른 자리로 · 길 바꾸기)은 틀을 다시 짠다 → 옮기기 · 지우기 · 개수는 PIL, 깨끗이 다듬기는 Gemini.
- PIL 뒤에 Gemini 편집을 또 얹을 수 있다(PIL 결과를 오려 올림 — `L13b_build2.sh` 의 B8s · B9 · B10).
- 같은 픽셀: `sh <ID>_build.sh /tmp/x && python3 -c "…np.array_equal…"` 로 설치한 그림과 견준다.

## 4. 마칠 때마다 — 커밋 · 번들 · 문서 · 보고
```sh
CO_AUTHOR='<그 세션의 귀속 줄>' SESSION_URL='<그 세션 주소>' bash tools/kit/tcommit.sh /path/msg.txt
git -c credential.helper= fetch https://github.com/BAEggman/biology2.git +refs/heads/main:refs/remotes/gh/main
git merge-base --is-ancestor gh/main main && echo 그대로 || echo "갈라짐 → tools/merge/README.md"
git bundle create /mnt/user-data/outputs/b2_hNN.bundle <앞 번들의 끝 커밋 또는 gh/main>..main && git bundle verify /mnt/user-data/outputs/b2_hNN.bundle
```
- 번들은 `device_commit_files` 로 `/Users/mac/Downloads/b2_hNN.bundle` 에. `push_b2.sh`(같은 폴더)의 `BUNDLES=( … )` 에 한 줄을 보탠다 — 먼저 `cp -p push_b2.sh push_b2.sh.bak<날짜>` · 이미 올라간 번들 줄은 지운다(GitHub main 을 ls-remote 로 확인한 뒤) · 끝나면 `bash -n push_b2.sh` 와 `grep -cE "github_pat_[A-Za-z0-9_]{20,}" push_b2.sh` = 0.
- **올리기(push)는 사용자만** 한다(`push_b2.command` 를 두 번 눌러 실행 · 토큰은 사용자가 직접 넣는다). Claude 는 토큰 · 비밀번호를 넣지도 쓰지도 않는다. 토큰을 `.git/config` · 명령줄 · 환경변수 · 스크립트 · 문서에 두지 않는다. 로그를 볼 때는 `sed -E 's/github_pat_[A-Za-z0-9_]+/***/g'`.
- 문서: `tools/prompts/<ID>_설계.md` · 인계서 §6(한 줄 + 배운 것) · `tools/plan/2026-11-11/새과_장수계획.md`(§0 · §2 의 그 그림 줄) · 지시서의 진행 표 → 프로젝트 문서(`claude/새과_장수계획_2026-11-11.md` · `claude/지시서_Opus_만들것_고칠것_2026-11-14.md`)에도 같은 내용을 올린다(토큰 · 사용자 메일 주소가 없는지 본 뒤).
- 보고: 무엇을 했나 두세 줄 · 그림 · 커버율(`node tools/plan/tally.js ch` 의 합) · **「다음에 할 일」 표**(사용자 지시 1).
