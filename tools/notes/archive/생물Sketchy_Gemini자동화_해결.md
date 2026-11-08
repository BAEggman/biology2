# Gemini 그림 자동화 — 프롬프트부터 회수까지 (2026-08-20 완성)

> 사용자 요청: 「**여러번 생성되어있던데 다음 생성부터는 네가 최대한 회수하는 방향으로 해보자**」
>
> **해결됐다. 이제 사용자가 첨부할 필요가 없다.** 아래 다섯 단계가 전부 자동이다.

---

## ★★ 전체 고리 — 다섯 단계

### ① 프롬프트를 컴포저에 넣는다

```js
const PROMPT = "...";
const ed = document.querySelector('div[contenteditable="true"], rich-textarea div[contenteditable]');
ed.focus();
document.execCommand('selectAll', false, null);
document.execCommand('insertText', false, PROMPT);
String(ed.innerText.length)          // 길이가 돌아오면 성공
```

### ② 보내기 — ★ 반드시 ①과 **다른 tool call**에서

```js
const b = [...document.querySelectorAll('button')]
  .find(x => x.getAttribute('aria-label') === '메시지 보내기' && !x.disabled);
if (b) b.click(); b ? 'clicked' : 'none'
```

`'none'`이 나오면 **직전 생성의 중지 버튼이 안 사라진 것**이다. 확인:

```js
[...document.querySelectorAll('button')].some(x => x.getAttribute('aria-label') === '대답 생성 중지')
```

`true`면 **대화 URL로 navigate 해서 새로고침**한 뒤 ①부터 다시 한다.

### ③ 완성을 기다린다 — 보통 5~8분

```js
await new Promise(r => setTimeout(r, 10000));
const stop = [...document.querySelectorAll('button')].some(x => x.getAttribute('aria-label') === '대답 생성 중지');
const im = [...document.querySelectorAll('img')].map(i => i.naturalWidth + 'x' + i.naturalHeight);
[String(stop), im.join(',')]
```

⚠ **`naturalWidth`가 한동안 `0`이다.** 페이드인이 끝나야 1024가 된다.
`stop`이 `false`인데 큰 이미지가 안 보이면 **URL로 navigate 해서 새로고침**하면 즉시 뜬다.
없다고 판단하고 다시 보내면 판을 하나 낭비한다.

### ④ ★★ 다운로드 버튼을 **내가** 누른다 (2026-08-20 신설)

```js
const im = [...document.querySelectorAll('img')].filter(i => i.naturalWidth > 400).pop();
const host = im.closest('single-image');
const b = [...host.querySelectorAll('button')]
  .find(x => (x.getAttribute('aria-label') || '').includes('다운로드'));
if (b) b.click(); b ? 'clicked' : 'none'
```

`single-image` 안의 버튼 셋: `이미지 공유` · `이미지 복사` · **`원본 크기 이미지 다운로드`**.
누르면 사용자 Mac의 `~/Downloads`에 **원본 해상도**(2752×1536 또는 2816×1536)로 떨어진다.

### ⑤ ★★ Downloads에서 집어 온다

**⚠ `device_list_dir`를 쓰지 말 것.** 이 Downloads 폴더는 파일이 수백 개라
한 번 부를 때마다 **2만 토큰**이 든다. `device_bash`로 최신 하나만 뽑는다.

```bash
# mcp__remote-devices__device_bash
ls -t "$HOME/mnt/Downloads"/Gemini_Generated_Image_*.png | head -1
```

그 다음 `device_stage_files`로 컨테이너에 올린다 (경로는 **기기 절대경로** `/Users/mac/Downloads/...`):

```
mcp__remote-devices__device_stage_files
  paths: ["/Users/mac/Downloads/Gemini_Generated_Image_xxxx.png"]
→ /mnt/user-data/uploads/Downloads/Gemini_Generated_Image_xxxx.png
```

그리고 여느 때처럼 설치한다:

```python
from PIL import Image
im = Image.open(SRC).convert('RGBA')
bg = Image.new('RGBA', im.size, (247, 241, 224, 255)); bg.alpha_composite(im)
im = bg.convert('RGB')
w = 1024; h = round(im.height * w / im.width)
im.resize((w, h), Image.LANCZOS).save('img/<패널>.webp', 'WEBP', quality=92, method=6)
```

---

## 접근 권한 — 한 번만 받으면 된다

`mcp__remote-devices__get_device_info` → `connectedFolders`가 비어 있으면
`device_request_folder_access(["~/Downloads"], reason="...")`를 부른다.
사용자가 허용하면 **그 세션 동안** 읽고 쓸 수 있다.
2026-08-20에 허용받았고 `/Users/mac/Downloads`로 잡혔다. 기기 이름은 `m1-local`(macOS arm64).

⚠ 세션이 바뀌면 다시 받아야 한다. 새 세션에서 그림 작업을 시작하기 전에 먼저 확인한다.

---

## ★ 못 하는 것 — base64로 캔버스를 떠 오는 길은 막혀 있다

`javascript_tool`로 이미지를 캔버스에 그려 `toDataURL`까지는 되는데,
반환값이 `[BLOCKED: Base64 encoded data]`로 걸러진다. **우회하지 않는다.**
④+⑤가 정식 경로이고 원본 해상도까지 얻으므로 더 낫다.

---

## 프롬프트를 쓸 때 (실패에서 역산한 것)

| 규칙 | 왜 |
|---|---|
| **4,000자 안쪽** | 넘으면 거절되거나 오류가 난다 |
| **문단 제목은 소문자** | 전부 대문자로 강조하면 거절 확률이 오른다 |
| **숫자로 「넷」이라 하면 안 지킨다** | 자리를 **번호로 매겨 순서**를 준다 — `left to right: 1. … 2. …` |
| **크기는 배수로** | 「성한 것의 3분의 1 길이」처럼 |
| **「없다」는 「닿지도 않는다」까지** | 없다고만 쓰면 옆 것이 침범한다 |
| **`what must be true` 목록을 끝에** | 지켜야 할 것을 한 번 더 못 박는다 |
| **해부·피부 단면 같은 말은 피한다** | `s27p01`이 두 번 거절당한 원인이 `a wide band of layered **skin** in cross section`이었다. `a cutaway of the **ground**, like rock strata`로 바꾸니 통과했다 |
| **거절당한 대화는 버린다** | 새 채팅에서 보낸다 |

## 편집(수정)은 재생성보다 낫다

「Keep this picture exactly as it is and change one single thing.」으로 시작하고
**바꿀 것 하나만** 적은 뒤 **바뀌지 않아야 할 것을 나열**한다.
2026-08-20 `s44p01`에서 두 번 편집해 딸의 초롱 겹침을 맞췄다 —
첫 편집은 겹치게는 했지만 초롱이 셋이 됐고, 둘째 편집에서 「정확히 둘」을 못 박아 해결했다.

## Gemini는 자기가 안 지킨 것을 스스로 말해 준다

응답 본문에 「다만 ~는 요청과 다르다」를 적어 준다. **응답 텍스트를 먼저 읽으면 검수 시간을 아낀다.**
