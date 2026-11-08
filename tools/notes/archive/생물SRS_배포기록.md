# 생물 SRS 앱 배포 기록

## 현재 라이브 (v10 — 그림↔카드 연결 배관 + 빌드 파이프라인)

- **URL**: https://baeggman.github.io/biology2/
- **저장소**: BAEggman/biology2 (main)
- **커밋(tip)**: `823957a` — "chore: npm 스크립트"
- **배포일**: 2026-08-02
- **author/committer**: `BAEggman <75311069+BAEggman@users.noreply.github.com>`, 무서명

### 커밋 6개 (되돌리기 쉽게 쪼갰다)

| 커밋 | 내용 |
|---|---|
| `c701122` | **v10a** 죽은 그림 링크 16장 수리 · PTIT 106패널 전수 (+9/−6줄) |
| `a178c1b` | **v10b** 오답 시 그림+요약+사실표 자동 노출 · img/ 95장 분리 (+65/−6줄) |
| `192a8b2` | **v10c** 연결 지도를 build.js 생성물로. 사실표가 단일 소스 |
| `34b0722` | **v10d** 검증 스위트 118종을 저장소에 넣음 |
| `f083806` | test: shallow clone 안내 |
| `cdefb4d` `823957a` | `.nojekyll` · npm 스크립트 |

### 파일 SHA256 (2026-08-02 v10)

| 파일 | SHA256 | bytes |
|---|---|---|
| `index.html` | `14dc8293631020acab70c4a0d12ea029a08e723276c7f02043814189c8dc7128` | 2,767,307 |
| `sketchy.html` | `497675b44e2694fb19772614098659849857bcdf7b6431271d46f901b7eeb508` | 14,561,419 |
| `build.js` | `54c00f79362c683fe266f56163e8af56b6a1a04763a809597ebfd444b85f715a` | 9,933 |
| `links_report.md` | `74c09e7b8fb30642e13a8bc07b8052daa3b0aa36c5d52c8c886f3c3e549e1b45` | 62,796 |
| `img/*.webp` | 95장 · 10.16MB · 평균 109KB · 최대 192KB | — |

**⚠️ `index.html`의 SHA 고정 불변식은 폐기됐다.** v9~v12 내내 `2c6cd373…`로 무변경이었으나 v10a에서 처음 바뀌었다. 이제 index.html은 매 배포마다 바뀐다 — 아래 「배포 검증 불변식」의 내용 기반 검사로 대체한다.

### 라이브 검증 ✅

- 전체 클론 후 바이트 대조 — index/sketchy/build/links_report + **img 95장 전부 일치**
- 깨끗한 클론에서 `npm i && npm test` → **118종 전부 통과**
- Pages 라이브(WebFetch `?cb=`) — `<title>` = `생물 SRS · 마이크로`, `links_report.md` 서빙 확인(연결 705/5531 · 고아 23)
- `.nojekyll` 추가 — Pages가 Jekyll을 거치지 않고 `img/`를 정적 서빙

---

## v10이 고친 것

### 근본 원인: PMAP을 손으로 관리했다

v9에 만든 `PMAP`(카드→패널)·`PTIT`·`picLink`·딥링크는 **인프라가 100% 완성돼 있었다.** 그런데 그 뒤 패널을 쪼개고(s20p01→a/b, s12p02→a/b) 장면을 12장 더 그리는 동안 지도를 안 고쳤다. 결과:

- **연결률 706/5,531 = 12.8%에서 정지**
- **죽은 링크 16장** — 클릭하면 13.88MB 받고 페이지 맨 위에 떨어진다. `sketchy.html` 수신부가 `if(el)`이라 조용히 실패
- **고아 패널 26장** — s31·s32·s33(세포호흡·전자전달계·대사) 10장이 통째로
- PTIT 누락 15 → 버튼에 `s31p01`이라고 ID가 그대로 노출

### v10a — 죽은 링크 수리

재배정 근거는 전부 사실표 대조:

| 카드 | 근거 소품 | → |
|---|---|---|
| P1-3, P1-3#2, P1-12, P1-13 | 줄기의 지퍼가 열림 (옥신) | `s20p01a` |
| P1-14 | 가위로 자른 자리에 곁가지 둘 (정단우성) | `s20p01a` |
| P1-4, X-PL-28 | 붓칠한 쪽만 초록 (시토키닌) | `s20p01a` |
| P1-6, P1-6#2 | 잎의 셔터 (ABA) | `s20p01b` |
| P1-7 | 가스 맞은 열매 (에틸렌) | `s20p01b` |
| P1-8, P1-8#3 | 부목 댄 줄기 (브라시노) | `s20p01b` |
| G1-95 | 브루너샘=십이지장 · M세포 | `s12p02a` |
| **G1-26** (비타민 B3) | **대응 소품 없음 — 오태깅** | **삭제** |

**PMAP 값에 배열 허용**(`pidList`). `S-PL-14`·`X-PL-27`은 촉진/억제를 갈라 묻는 카드라 두 패널에 걸친다. 1:1로는 표현 불가였다.

결과: 죽은 링크 **16 → 0**, 커버 패널 **80 → 83**, 고아 **26 → 23**.

### v10b — 오답 복구 화면

`picLink`는 링크라 안 누르면 안 본다. 그림이 가장 필요한 순간은 틀린 직후다.

- 등급 **0·1·2·3**에서 그림 + 요약(br) + 사실표를 그 자리에 편다. Space/Enter/계속으로 진행
- `grade()` 말미를 `advance()`로 분리 — 카드가 임의로 넘어가지 않는다
- **이미지를 `img/*.webp` 95개로 분리.** index.html은 `<img>` 태그가 0개였던 앱이다. base64 내장 시 2.68MB→16MB로 모바일에서 못 쓴다. `loading=lazy`라 틀린 카드에서만 1장 받는다
- `PBR`·`PFACT`·`PNOIMG` 주입 (+84KB). 도해 11장은 이미지 없이 표만
- 설정 토글 `DB.picFix` (기본 켬). 끄면 종전 동작

**그림이 없는 카드에서는 아무것도 안 바뀐다.** 12.75%에서만 뜬다.

### v10c — 사실표가 단일 소스

```
소스     sketchy.html DATA
         panels[].pc : ['G1-31', ...]            패널 단위
         panels[].f  : [소품, 사실, ['G1-44']]    셋째 자리 = 행 단위 (선택)

생성물   index.html /*BUILD:START ... BUILD:END*/
         PMAP PROW PTIT PBR PFACT PNOIMG  ← build.js
```

- 기존 705장을 `pc`로 **무손실 이관** (83패널). 역변환 대조로 삽입 외 변경 0 확인
- 산출물이 손으로 만든 v10b 지도와 **한 건도 다르지 않음**을 확인
- **자동 행 배정은 하지 않았다.** 용어 겹침 배정을 표본 검수하니 정밀도 55~65%. 특히 `discrim` 카드(235장)가 질문에 양쪽 개념을 담아 반대쪽 행에 붙었다 (`B0-220#1` 「니코틴성?」→ 무스카린성 행 / `N0-20#1` 「선구?」→ 후구 행). 행 배정은 승인 흐름이 있는 제안 5에서
- `PROW` 신설 — 행 링크가 있으면 복구 화면에서 그 행을 강조(노란 배경 + 왼쪽 선). 현재 0건
- **빌드가 죽는 조건**: 없는 카드 ID / 셋째 자리가 배열 아님 / 이미지 누락 / 패널 ID 중복. 일부러 망가뜨려 확인함
- **`links_report.md`** — sketchy.html이 13.88MB라 git diff가 무용지물이다. 링크 707건을 한 줄씩 적어 커밋한다. **태깅 검수는 이 파일로 한다**

---

## 검증 스위트 118종 (저장소에 있다)

```bash
npm i && npm test          # 전체
node build.js --check      # 쓰지 않고 검사만
```

| 파일 | 지키는 것 | 종수 |
|---|---|---|
| `test/verify_links.js` | 죽은 참조 0 · PTIT 106 전수 · 카드ID 실재 | 25 |
| `test/verify_picfix.js` | 복구 화면 구조 · 이미지 95 · CARDS/EXAM/키 무변경 | 43 |
| `test/verify_build.js` | 빌드 재현성 · **일부러 망가뜨렸을 때 죽는지** · 리포트 정합 | 24 |
| `test/smoke_links.js` | 앱을 띄워 실제 채점하며 링크가 살아있는지 | 6 |
| `test/smoke_picfix.js` | 세션을 돌려 오답 시 뜨고 정답 시 안 뜨는지 | 11 |
| `test/migrate_safe.js` | **실사용 DB(2,166장)를 새 버전으로 열어 진도 보존** | 9 |

기준본을 해시로 박지 않는다. `_lib.js`가 git 로그에서 **내용으로** 찾는다 — v12 = v9 딥링크 주석은 있고 `pidList`는 없는 커밋. 리베이스해도 안 깨진다. **전체 히스토리 필요** (`--depth 1`이면 `git fetch --unshallow`).

`migrate_safe.js`가 특히 중요하다. 진도가 전부 localStorage에 있고 백업은 사용자 손에만 있다. 배포가 진도를 날리면 되돌릴 방법이 없다.

**검증이 못 잡는 것**: 그림이 사실과 맞는지. 사실표 대조는 여전히 사람이 한다(마스터노트 §10).

---

## 배포 검증 불변식 (v10 갱신)

**index.html — SHA 고정 폐기, 내용으로 검사한다:**

1. `<script id="CARDS">` JSON 길이 = **5531**
2. `<script id="EXAM">` JSON `meta.total` = **1475**
3. `bio_srs_v1` 존재 — **localStorage 키. 바뀌면 진도가 통째로 사라진다**
4. `2027-01-01` 존재 (시험일 거버너)
5. `<script>` 블록 정확히 **5개**. JS 블록 `new Function()` 통과
6. v7 마커: `곡 생애주기` `songPlan` `playOnce` `gradeSong` `LYR.plan`
7. v8 마커: `혼동 지도` `var CONF=(function()` `CONF.mine` `confWeave` `startDrill` `confLogWrong`
8. v9 마커: `var PMAP=` `var PTIT=` `picLink` `sketchy.html` `안 되짚음` `되짚었다` `근거 없이 골랐다`
9. **v10 마커**: `BUILD:START` `pidList` `PROW` `picFix` `advance()` `img/'+pid+'.webp` `fPicFix`
10. **죽은 참조 0** — `"s20p01"` `"s12p02"`가 PMAP 값에 없을 것
11. `img/*.webp` **95장**, PNOIMG(도해) 11장 외 전 패널에 파일 존재

**sketchy.html:**

12. 완전한 HTML(`</html>`), 도메인=생물(한의학/화학 문자열 0)
13. **일관성: webp + svg == br** — 95 + 11 = 106, 다리 106
14. `pc:[` **83개** (패널 단위 링크)
15. v12 마커: `sk_bx_` `다리 모두 펼치기` `bx:` 106개

**전부 `npm test`가 자동으로 본다.** 손으로 확인할 필요 없다.

---

## sketchy.html 갱신 이력

| SHA | bytes | webp | svg | br | 커밋 | 비고 |
|---|---|---|---|---|---|---|
| `71c3168b…` | 11,977,382 | 83 | 10 | 0 | `bba768b` | 최초 허브 (다리 없음) |
| `63a541d5…` | 12,001,044 | 83 | 10 | 93 | `465d61c` | 이미지↔개념 다리 |
| `f37bba7a…` | 13,940,492 | 93 | 10 | 103 | `24fc01c` | 103패널. `<title>` stale |
| `22412f63…` | 14,554,768 | 95 | 11 | 106 | `2e7895f` | v12 접이식 다리 + 재검토 95/95 |
| `497675b4…` | 14,561,419 | 95 | 11 | 106 | `192a8b2` | **현재.** `pc` 링크 스키마 (+6.5KB) |

---

## 롤백

커밋을 쪼갠 이유가 이것이다. 클론 디렉터리에서:

```bash
git revert --no-edit 192a8b2                    # 빌드 파이프라인만
git revert --no-edit a178c1b                    # 복구 화면만
git revert --no-edit 192a8b2 a178c1b c701122    # v10 전체 → v12로
git push origin main
```

되돌아갈 지점: v12 `2e7895f` · v9 `24fc01c` · v8 `fabf6c6`.

---

## 배포 방법 (v10에서 재검증)

### 1. PAT + git push — **작동한다. 기본 경로.**

v8·v9·v12·**v10** 모두 성공. 프록시가 사용자 PAT를 덮어쓰지 않는다 — askpass로 넘기면 그대로 도달한다.

토큰: fine-grained PAT · Only select repositories → `BAEggman/biology2` · **Contents: Read and write** 하나 · 만료 1일.

```bash
git clone https://github.com/BAEggman/biology2.git /tmp/b2      # --depth 1 금지 (테스트가 히스토리를 쓴다)
# 파일 교체 후
git -c user.name=BAEggman \
    -c user.email='75311069+BAEggman@users.noreply.github.com' \
    -c commit.gpgsign=false commit -F <메시지파일>
mkdir -p ~/.dep && chmod 700 ~/.dep
printf '%s' '<TOKEN>' > ~/.dep/.tk && chmod 600 ~/.dep/.tk
printf '#!/bin/sh\ncase "$1" in *Username*) echo BAEggman ;; *Password*) cat "$HOME/.dep/.tk" ;; esac\n' > ~/.dep/askpass.sh
chmod 700 ~/.dep/askpass.sh
GIT_ASKPASS=~/.dep/askpass.sh GIT_TERMINAL_PROMPT=0 \
  git push origin main 2>&1 | sed "s|$(cat ~/.dep/.tk)|<TOKEN>|g"
rm -f ~/.dep/.tk ~/.dep/askpass.sh
```

`sed` 마스킹 필수 — 실패 시 에러에 토큰이 딸려 나온다.
**붙여넣은 토큰은 대화 기록에 평문으로 남는다. push 직후 revoke를 안내할 것.**

### 2. GitHub 웹 UI — 사용자가 직접 드래그. 한도 25MB

### 3. Claude in Chrome — **불가.** `file_upload`가 호출당 10MB 한도, sketchy는 13.88MB

### 4. 사용자 Mac 터미널 — `device_bash`는 네트워크 없음

### 세션 자격의 한계

`GH_TOKEN`은 `proxy-injected`. 등록된 저장소에만 주입한다. **클론은 되고 push는 거부**(`Invalid username or token`). Cowork 세션에 `add_repo` 도구는 없다.

### 네트워크

`github.com`·`api.github.com`·`raw.githubusercontent.com`·`codeload.github.com` 통과, **`baeggman.github.io` CONNECT 403**.

- 콘텐츠 대조 → **전체 클론 후 `sha256sum` 비교가 가장 확실하다.** WebFetch는 2.6MB 파일을 잘라 읽어 못 믿는다(v10에서 실제로 오판했다)
- Pages 라이브 → WebFetch(`?cb=` 캐시버스트). 작은 파일(`links_report.md`)로 확인하는 편이 정확하다

---

## 알려진 결함 (v10 시점, 미해결)

### 연결 쪽

- **연결률 12.75%** — 705/5,531. 제안 3·5 대상
- **고아 패널 23장** — s31(4) s32(3) s33(3) = 세포호흡·전자전달계·대사 10장 / s08(2) s27(2) / s06 s12 s15 s18 s23 s24 s30 d03 d04
- **행 단위 링크 0건** — 전부 `pc`(패널 단위). 제안 5에서 내린다
- 게이트 편차: I 34% · Q 28.9% vs **E 4.5% · A 5.1% · K 5.4%**

### Sketchy 방법론 쪽 (전부 미해결)

`claude/생물Sketchy_방법론평가_v12.md` 참조.

- **공용 심볼 어휘 부재 + 간섭** — 590행 중 585개 고유. 「고리」7뜻 「붉은」7뜻 「둥근」7뜻
- **muted 팔레트가 색 채널 봉인** — 색 기반 소품 47개 손해
- **q블록 32/106** — 시험 판별점이 30%만 채워짐
- **인물 복제가 유령 항목 생성** — s02p01 뚱뚱한 경비 둘 → 보조수용체가 셋으로 읽힘
- **s13p02 2×2 격자** — 장소가 아니라 표
- **J게이트 0패널**(157장) · 커버리지가 카드 질량과 역상관
- s06p01 대각선 구도로 프레임 30% 여백
- `s02p02` 1024×1017 (유일한 비정사각, 기능 무관)

---

## 진도 데이터 (2026-07-28 기준)

localStorage `bio_srs_v1`, 약 401KB, 스키마 `v: 3`. 카드 상태 2,166개, 복습 이력 1,555개.
필드 `ef, iv, reps, lap, rich, box, due, lg, seen, ls, sus` (+ v10에서 `DB.picFix` 추가, 없으면 켬).

**v10 배포가 진도를 건드리지 않는 것을 확인했다** — 2,166장 상자·간격·함정 1,084건·격리 23장·오답로그·시험일·예산 보존. `DB.v`도 3 그대로라 마이그레이션이 안 돈다.

## 확인할 두 숫자 (2026-08-14경)

- **확신 배신율 5% 이하 유지** — 8% 넘으면 기준을 너무 푼 것
- **일일 부하 337장 → 280장대 하강**

## 그 밖에

- 한글 파일명은 셸이 NFD로 반환할 수 있다. `unicodedata.normalize('NFC', s)`로 비교
- **사용자에게 보낼 PNG 파일명은 반드시 영문.** 한글 파일명은 다운로드가 깨진다
