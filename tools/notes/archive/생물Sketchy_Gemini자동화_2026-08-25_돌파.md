# Gemini 자동화 — 2026-08-25 돌파

## 한 줄

**좌표로 누르지 말고, 요소를 DOM 에서 찾아 마우스 이벤트 열 개를 순서대로 쏜다.**
지난 여러 세션이 「모드 선택 메뉴가 안 열린다」 「송신 버튼이 안 먹는다」로 막혔던 것이
전부 이 하나였다.

## 왜 안 됐나

Angular Material 은 **hover 계열 이벤트가 먼저 오지 않으면 클릭을 무시**한다.
그리고 `computer left_click` 은 좌표만 보내는데, 스크린샷 좌표와 페이지 좌표가 어긋나 있다
(실측: 스크린샷 1263px · `innerWidth` 1527 · `devicePixelRatio` 2.2).
그래서 좌표를 아무리 맞춰도 「hover 없는 클릭」이 되어 무시됐다.

지난 세션들이 「스크린샷을 먼저 찍으면 가끔 된다」고 적었던 것도 같은 이야기다 —
스크린샷이 마우스를 그 자리로 옮겨 hover 를 일으켰던 것이다. 우연에 기대던 것을 확정으로 바꿨다.

## 되는 방법

```js
const b = [...document.querySelectorAll('button')]
  .find(x => /모드 선택 도구/.test(x.getAttribute('aria-label') || ''));
const r = b.getBoundingClientRect(), cx = r.x + r.width/2, cy = r.y + r.height/2;
for (const t of ['pointerover','pointerenter','mouseover','pointermove','mousemove',
                 'pointerdown','mousedown','pointerup','mouseup','click'])
  b.dispatchEvent(new MouseEvent(t, {bubbles:true, cancelable:true, composed:true,
                                     clientX:cx, clientY:cy, button:0,
                                     buttons: t.includes('down') ? 1 : 0}));
```

**앞의 다섯(hover 계열)이 핵심**이다. `click` 만 쏘면 안 먹는다.

이 방법으로 되는 것 — **모드 메뉴 열기 · 메뉴 항목 고르기 · 메시지 보내기 · 이미지 내려받기.**

## 모델 고르기 (2026-08-25 UI)

컴포저 오른쪽의 알약 버튼: `aria-label="모드 선택 도구 열기, 현재 ○○ 모드 사용 중"`.
열면 네 줄이 뜬다 — `3.5 Flash-Lite` · `3.7 Flash` · `3.1 Pro` · `확장된 사고 모델`.
`[role="menuitem"]` 로 잡아 같은 이벤트 열 개를 쏜다. 알약이 「Pro」로 바뀌면 된 것이다.

⚠ **대화 안에서는 이 알약이 안 보인다.** 새 채팅 화면에서만 뜬다 —
모델은 대화를 시작할 때 정해지고 그 대화 내내 유지된다. 그러니 **새 대화를 팔 때 Pro 로 맞춰 두면
그 대화에서 이어 보내는 것은 전부 Pro** 다.

## 내려받기 — 탭 하나에 한 번 (재확정)

2026-08-21 에 「대화가 무거워서였다」로 정정했었는데, **2026-08-25 에 그림 3장짜리 가벼운
대화에서도 똑같이 걸렸다.** 같은 탭에서 두 번째 클릭은 조용히 무시된다 — 오류도 안 난다.
대화 URL 로 `navigate` 해서 새로고침해도 **안 풀린다.**

```
tabs_create_mcp
→ navigate(대화 URL)
→ 10초 대기
→ computer scroll 아래로 (JS scrollTop 만으로는 지연 로딩이 안 풀린다)
→ 6~8초 대기
→ 다운로드 버튼에 **이벤트 열 개**
```

## 파일 회수 경로

```
device_bash:        ls -t "$HOME/mnt/Downloads"/Gemini_Generated_Image_*.png | head -1
device_stage_files: paths=["/Users/mac/Downloads/<이름>"]      ← ★ 기기 경로로 준다
→ /mnt/user-data/uploads/Downloads/<이름>   (2048×2048 PNG)
```

⚠ `device_bash` 가 찍어 주는 `/sessions/.../mnt/Downloads/...` 경로를 그대로 주면 거부된다
(“is not inside a folder connected to Cowork”). 연결된 폴더는 `/Users/mac/Downloads` 다.

## 설치

```python
from PIL import Image
im = Image.open(SRC).convert('RGBA')
bg = Image.new('RGBA', im.size, (247,241,224,255)); bg.alpha_composite(im); im = bg.convert('RGB')
w = 1024; h = round(im.height*w/im.width)
im.resize((w,h), Image.LANCZOS).save('img/<pid>.webp', 'WEBP', quality=92, method=6)
```

## 그림 프롬프트에서 이번에 배운 것

### ★ 「개수를 세라」는 부담을 소품에 나눠 준다

`s37p01` v1 은 못을 2·2·3·4 로 박으라고 했더니 사다리와 걸쇠에 **제 구슬이 달려** 2를 못 세게 됐고,
청회색은 넷이 아니라 셋, 칸은 다섯이 아니라 넷, 고리는 넷이 아니라 셋이 됐다.

v2 에서 고친 것 —
- 「사다리·걸쇠에는 **둥근 부분이 하나도 없다**」로 경쟁자를 지웠다
- 2 는 못이 아니라 **사다리의 가로대**와 **걸쇠의 배**가 직접 나르게 했다 (셀 것이 절반으로 줄었다)
- 「count them: five」처럼 **세라고 말했다**

그러니 다섯 가지 개수가 다 맞았다. **한 그림에서 세게 하는 것은 두세 가지가 한계**다.

### ★ 부정형은 「없다」만으로 부족하다

`s08p03` v1 은 「자갈 넷」이 여섯이 됐다(달걀판으로 읽혔다). v2 에서
「다섯째 자리는 없다 · 어느 줄에도 셋째 자리는 없다 · 세 번째 줄은 없다 · 달걀 상자가 아니다」로
**틀릴 수 있는 모양을 하나하나 막으니** 정확히 넷이 나왔다.

### ★ 몸에서 떼어 놓게 한다

들고 있는 물건이 소매에 가리면 세지지 않는다. 「**몸에서 떼어 앞으로 들고, 보는 쪽으로 살짝 기울여
윗면 전체가 보이게**」라고 쓰면 가림이 사라진다.
