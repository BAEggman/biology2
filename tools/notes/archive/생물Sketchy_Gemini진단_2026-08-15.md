# Gemini 진단 — 2026-08-15 (지난 진단을 갈아치운다)

## ★ 한 줄 결론

**계정은 살아 있다. 죽는 것은 브라우저 쪽 Angular다.**
죽는 자리가 둘로 나뉜다 — **① 응답 렌더링**, **② 전송 자체**.
지난 세션의 「빈 응답 = 계정 문제」는 **오진이었다.**

---

## ① 응답이 안 보이는 것 — 새로고침하면 있다

`Reply with just the word OK.` 를 보냈더니

- 대화 제목이 「Simple Confirmation Response」로 **바뀌었다** → 서버는 답을 만들었다
- 그런데 `message-content` 가 **빈 문자열**이고 정지 버튼(「대답 생성 중지」)이 **안 사라진다**
- **같은 대화 URL로 다시 들어가니 `OK` 가 그대로 있었다**

이미지도 같다.

- blob `<img>` 가 붙는데 `naturalWidth === 0` 이다
- **새로고침하면 화면에는 정상으로 그려진다**
- ★ `naturalWidth 0` 은 **판정 근거가 못 된다** — 확장 프로그램의 JS 컨텍스트가 blob 크기를 못 읽을 뿐이고
  픽셀은 화면에 있다. **스크린샷으로 확인해야 한다.**

### 절차

```
보낸다 → 40~60초 → 같은 대화 URL로 navigate(새로고침) → 스크린샷
```
`stop` 버튼이나 `naturalWidth` 를 기다리지 마라. 안 없어지고 안 채워진다.

---

## ② 전송이 안 되는 것 — 이쪽이 진짜 막힘

**하루에 두 번 같은 일이 벌어졌다.** 둘 다 「텍스트 몇 건 + 이미지 1건」을 보낸 뒤였다.

### 실패한 방법 (전부)

| 방법 | 결과 |
|---|---|
| `send.click()` (JS) | 에디터에 글자 그대로 남음 |
| Pointer/Mouse 이벤트 조합 + click | 같음 |
| `computer` 실제 마우스 클릭 (스크린샷으로 좌표 확인) | 같음 |
| **`computer type` 실제 키보드 타이핑** → 보내기 클릭 | ★ **글자는 정상으로 들어가는데 전송만 안 된다** |
| 실제 타이핑 → 에디터 안 클릭 → Enter | 같음 |
| 탭 새로고침 · 새 탭 · 새 창 | 같음 |
| `resize_window` | 한 번은 뚫렸고(아래) 그다음엔 안 통했다 |

★ **실제 키보드로 친 글자도 전송이 안 된다**는 것이 결정적이다.
「Angular가 DOM 주입을 못 본다」는 가설은 **틀렸다.** 보내기 자체가 죽는다.

### 한 번 뚫렸던 조건 — 재현이 안 된다

창이 **실제로 크기가 바뀌었을 때**(composer가 화면 밖에 잘려 있다가 보이게 됐을 때)
직후에 전송이 나갔다. 이미 최대화된 창에 `resize_window` 를 걸면 스크린샷 크기가
그대로여서(= 실제로 안 바뀜) 아무 효과가 없었다.
→ **창이 실제로 리사이즈될 때만** 효과가 있는 듯하다. 신뢰할 만한 방법은 아니다.

### 길이는 원인이 아니다

- 28자 → 나갔다 · 3,546자(v3) → 나갔다 · 3,315자(v4 축약) → **안 나갔다** · 4,786자(v4) → 안 나갔다
- 같은 28자도 나중에는 안 나갔다
→ **길이가 아니라 세션 상태다.**

### 그래서 규칙

**이미지 한 장을 뽑고 나면 그 세션은 곧 잠긴다고 보고 움직인다.**
- 그림 작업은 **한 번에 한 장**을 목표로 한다
- 잠기면 **프롬프트를 고치지 말고 즉시 도해로 돌린다**
- 사용자에게 브라우저를 한 번 완전히 닫았다 열어 달라고 하는 것이 가장 빠를 수 있다(미검증)

---

## ③ 좌표 환산 — 스크린샷 ≠ CSS 픽셀

`innerWidth` 로 비율을 계산하면 **틀린다.** 실측:

```
창 A: 스크린샷 1291×764 · innerWidth 1163 → 순진한 비율 1.110  (틀림)
       실제                                → x: ×1.2196 · y: ×1.2196 + 24
창 B: 스크린샷 1247×792 · innerWidth 1163 → 또 다르다
```

★ **계산하지 말고 스크린샷을 찍어 보이는 자리를 클릭한다.** 그게 유일하게 맞았다.

---

## ④ 전송 성공 판정 — URL은 못 믿는다

- `.ql-editor` 길이 → 쓸모없다
- 정지 버튼 → 쓸모없다(안 사라진다)
- `location.href` 가 `/app/<id>` 로 바뀌는 것 → **거짓 양성이 있다.**
  오늘 `0189b73e…`·`963f3cb2…` 두 번 바뀌었다가 `/app` 으로 튕겼고 그 대화는 **없었다**
- ★ 확실한 것: **왼쪽 「최근」 목록에 새 대화가 생겼는지 본다.**
  ```js
  const b=[...document.querySelectorAll('button,a')].find(e=>/최근|기록|History|검색/.test((e.getAttribute('aria-label')||'')+(e.innerText||'')));
  b.click(); await new Promise(r=>setTimeout(r,2500));
  document.body.innerText.slice(0,400)
  ```

---

## ⑤ 모드 바꾸기 — 메뉴 항목은 `gem-menu-item` 이다

새 창은 **Flash**로 열릴 수 있다. 스크린샷 좌표로 클릭하면 옆 항목(확장된 사고 모델)이 눌린다.
**JS로 원소를 찾아 이벤트를 쏘는 쪽이 정확했다** (메뉴는 DOM 클릭이 먹는다 — 보내기 버튼과 다르다).

```js
const b=[...document.querySelectorAll('button')].find(x=>/모드 선택|현재 .* 모드/.test(x.getAttribute('aria-label')||''));
b.click(); await new Promise(r=>setTimeout(r,1800));
const el=[...document.querySelectorAll('gem-menu-item[role="menuitem"]')].find(e=>/^3\.1 Pro/.test((e.innerText||'').trim()));
const inner=el.querySelector('gem-menu-item-content')||el;
for(const t of [el, inner]){
  t.dispatchEvent(new PointerEvent('pointerdown',{bubbles:true,composed:true}));
  t.dispatchEvent(new MouseEvent('mousedown',{bubbles:true,composed:true}));
  t.dispatchEvent(new PointerEvent('pointerup',{bubbles:true,composed:true}));
  t.dispatchEvent(new MouseEvent('mouseup',{bubbles:true,composed:true}));
  t.dispatchEvent(new MouseEvent('click',{bubbles:true,composed:true}));
}
```
확인은 `aria-label` 로 — 「현재 Pro 모드 사용 중」/「현재 Pro Extended 모드 사용 중」.
「확장된 사고 모델」은 **모델과 별개 토글**이고, 오늘은 끄는 데 실패했다(켜져 있어도 무방해 보인다).

---

## ⑥ 글자 넣는 법 — 둘 다 된다

**A. DOM 주입** (`execCommand`·`innerHTML` 은 TrustedHTML에 막힌다)
```js
const ed=document.querySelector('.ql-editor');
ed.focus();
while(ed.firstChild) ed.removeChild(ed.firstChild);
for(const line of txt.split('\n')){const p=document.createElement('p');p.textContent=line;ed.appendChild(p);}
ed.classList.remove('ql-blank');
ed.dispatchEvent(new InputEvent('beforeinput',{bubbles:true,cancelable:true,inputType:'insertText',data:txt}));
ed.dispatchEvent(new InputEvent('input',{bubbles:true,cancelable:false,inputType:'insertText',data:txt}));
```

**B. 실제 타이핑** — `computer type`. **줄바꿈을 넣지 마라**(Enter가 섞이면 중간에 전송된다).
줄바꿈 없는 한 줄 프롬프트로 만들어 3~4토막으로 나눠 친다. 먼저 **에디터 안을 실제로 클릭**해야 한다.
⚠ `cmd+a` 는 에디터에 포커스가 없으면 **페이지 전체**를 선택한다.

둘 다 글자는 정상으로 들어간다. 막히는 것은 **전송**뿐이다.

---

## ⑦ 한 줄 검사 — 여전히 먼저 하되 해석이 바뀐다

```
Reply with just the word OK.
```
- 전송되고 새로고침해서 답이 보이면 → 그림 작업 가능. **바로 본 프롬프트를 보낸다**(시간을 끌면 잠긴다)
- **전송 자체가 안 되면 → ② 상태. 프롬프트를 고치지 말고 도해로 간다**
- 전송은 됐는데 새로고침해도 빈 채면 → 그때가 진짜 계정 문제다
