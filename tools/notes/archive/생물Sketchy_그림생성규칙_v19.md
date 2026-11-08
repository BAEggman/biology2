# 그림 생성·수정 실전 규칙 v19 — `s04p06` 척삭 상회 5판에서 역산

v18(규칙 15~19)에 **이어지는** 문서다. 2026-08-07 `s04p06`을 다섯 판 그리면서 나왔다.
전부 실패에서 역산했다.

---

## 규칙 20 — ★ **건물 안에 넣은 것은 그린 게 아니다**

`s04p06` v2에서 「지붕 밑을 앞뒤로 관통하는 들보」를 시켰더니 Gemini는
**벽에 박힌 브래킷 하나 + 벽 위의 가로 몰딩 한 줄 + 밑단 굽도리 한 줄**을 그렸다.
갈색 마스크로 재 보니 **x167~256에 90px 공백**이 있었고, 몸통 구간(3~8px)은
같은 건물의 밑단 굽도리(5~8px)와 **두께도 색도 구별이 안 됐다.**

> 즉 「하나의 막대가 몸을 꿴다」가 **그림에 없었다.**
> 아이러니하게도 연속으로 읽히는 건 **흰 관**뿐이라, 「하나가 꿴다」가
> 척삭이 아니라 **신경관에 붙어 버렸다.**

**고친 방법 — 안에 넣지 말고 벽 앞으로 뺐다.**

```
Its plank wall is completely plain and bare — no mouldings, no sills, no trim,
no rails, no horizontal wooden bands of any kind.
In front of that plain wall runs one single very thick … beam, carried on three
black iron brackets. … It never stops, never breaks and is never hidden.
```

세 가지가 같이 필요했다:
1. **벽 앞으로 뺀다** (in front of the wall) — 안에 있으면 안 그린다
2. **경쟁자를 명시적으로 금지한다** (no mouldings, no sills, no trim…) — 안 그러면 장식으로 흡수된다
3. **받침을 준다** (three black iron brackets) — 받침이 있어야 「하나가 얹혀 있다」가 성립한다

## 규칙 21 — 「화면 끝에서 끝까지」는 **다른 소품 위를 밟는다**

규칙 20을 고치려고 v4에서 「from the far left edge to the far right edge」를 썼더니
들보와 관이 **오른쪽 멍게 건물 앞을 가로질렀다.** 멍게는 척삭도 신경관도 **없어야** 하는데
그 위를 지나가 버려서 **단독 실격**이었다.

**연속성은 「끝에서 끝까지」가 아니라 「끊김 없이 + 어디서 멈추는지」로 지시한다.**

```
It begins a little way in from the left edge and stops in mid-air about two thirds
of the way across, and along that whole run it is one unbroken piece.
Nothing of the beam reaches it: there is a clear stretch of plain empty sky between
the cut right end of the beam and the barrel building, and the beam neither touches
it nor passes in front of or behind it.
```

**「없다」는 소품은 「닿지도 않는다」까지 써야 한다.** 없는 것을 없다고만 쓰면 옆 것이 침범한다.

## 규칙 22 — 프롬프트가 5,000자를 넘거나 대문자로 강조하면 **거절·오류가 난다**

| 판 | 길이 | 결과 |
|---|---|---|
| v2 | 3,886자 | ✅ 생성 |
| v3 | 4,948자 · `ONE SINGLE ENORMOUS WOODEN BEAM` 같은 전부 대문자 문단 제목 | ❌ **거절** (“I'm having a hard time fulfilling your request.”) |
| v3b | 5,004자 · 대문자 제거, `skewering`→`running clean through` 등 완화 | ❌ **오류** (“I encountered an error…”) |
| v4 | 3,873자 | ✅ 생성 |
| v5 | 4,083자 | ✅ 생성 |

**4,000자 안쪽으로 유지하고, 문단 제목은 소문자로 쓴다.**
`skewering`(꿰다) 같은 폭력 함의 단어도 다른 조건과 겹치면 거절 확률을 올린다 —
`running clean through`로 바꾸면 같은 뜻이 그대로 전달된다.

## 규칙 23 — ★ 픽셀 후보정은 **원본 픽셀을 떠다 쓴다**. 새로 그리면 티가 난다

v2에서 관의 오른쪽 끝에 구멍을 그려 넣으려고 `ImageDraw.ellipse`로 검은 타원을 찍었다.
검수자가 실측으로 잡아냈다:

| | 왼쪽(생성 원본) | 오른쪽(내가 찍은 것) |
|---|---|---|
| 관벽 흰 고리 최대 휘도 | **243~252** | **114~140** (흰 고리가 아예 없다) |
| 휘도<50 연결성분 | 2개(고리·구멍 분리) | **1개로 병합** |

> 100% 배율에서 왼쪽은 파이프 구멍, 오른쪽은 **볼트 대가리**로 보였다.
> **구멍이 없는 것보다 나빴다.**

**v5에서 쓴 방법 — 반대쪽 개구부를 통째로 떠서 축소해 붙였다.**

```python
src = im.crop((124, 362, 204, 456))          # 왼쪽 개구부 원본
src = src.resize((38, 60), Image.LANCZOS)
m = Image.new('L', (38, 60), 0)
ImageDraw.Draw(m).ellipse([1, 1, 36, 58], fill=255)
m = m.filter(ImageFilter.GaussianBlur(1.2))   # 가장자리 페더
im.paste(src, (570, 478), m)
```

⚠ **단, 축소하면 선 굵기도 같이 줄어든다.** 검수자가 이것도 잡았다 —
「펜 선 굵기는 축척 불변이어야 하는데 붙여넣기 축소로 같이 줄었다」.
그래서 **붙여넣은 뒤 바깥 테를 원래 굵기(3px)로 다시 그어야** 한다.
그때도 **4배 슈퍼샘플링**을 쓰면 손그림 느낌이 살아난다:

```python
S = 4
tile = im.crop(BOX).resize((w*S, h*S), Image.LANCZOS)
ImageDraw.Draw(tile).ellipse([2,2,w*S-3,h*S-3], fill=TUBE, outline=INK, width=3*S)
im.paste(tile.resize((w, h), Image.LANCZOS), BOX[:2])
```

## 규칙 24 — 두 소품을 잇는 **한 줄의 선**이 대조를 통째로 무너뜨린다

v5에서 꼬리 첨단(721, 698)에서 멍게 건물(x≈761)까지 **길이 45px·두께 2~3px의 획 하나**가
그려져 있었다. 그 선 하나 때문에 **「멍게는 꼬리를 잃었다」가 봉합**되고
「창고에서 통으로 놓인 도교(渡橋)」로 읽혔다.

**「없다」를 가르치는 그림에서는 두 소품 사이의 빈 공간을 픽셀로 훑어라.**
지우는 데 1초, 안 지우면 패널 하나가 죽는다.

---

# Gemini 운용 — 이번에 새로 걸린 것

## ④ 전송 버튼은 **한 번 hover한 뒤에** 눌러야 먹는다

`computer` `left_click`을 정확한 좌표에 보내도 **아무 일도 안 일어나는** 일이 반복됐다.
JS로 pointerdown/pointerup/click 전부 디스패치해도 안 됐고, `Enter`도 안 먹었다.

**성공한 두 번은 공통적으로 클릭 직전에 `screenshot`이 있었다.**
스크린샷이 마우스를 그 자리로 옮겨 hover를 발생시키고(툴팁 「제출」이 뜬다),
그 상태에서 클릭하면 통과한다.

```
click(컴포저) → JS execCommand insertText → screenshot → click(1016, 506)
```

⚠ 새로고침 직후 `execCommand`가 **길이 1**을 돌려주면 컴포저가 아직 포커스를 못 받은 것이다.
컴포저를 한 번 더 클릭하고 다시 넣으면 된다.

## ⑤ 이미지가 페이드인 중에는 `naturalWidth`가 0이다

응답 텍스트에 「Here is the illustration」이 떠도 `img.naturalWidth`가 한동안 **0**이다.
`blob:` src는 붙어 있는데 디코드가 안 끝난 상태다. **10~20초 더 기다리거나 새로고침**하면 1024가 된다.
없다고 판단하고 다시 보내면 판을 하나 낭비한다.

## ⑥ Gemini는 자기가 안 지킨 것을 **스스로 말해 준다**

v4·v5 모두 응답 본문에 「다만 ~는 요청과 다르다」를 적어 줬다
(“the brown bar … is shown resting in front of it”, “the building on the left has two distinct levels”).
**응답 텍스트를 먼저 읽으면 검수 시간을 아낀다.**

---

# 적대적 검수 — 이번 실측

| 판 | 검수 결과 |
|---|---|
| `s04p06` v1 | 최상 3 — 지붕 박공 방향 탓에 들보 축과 꼬리 축이 직교 |
| `s04p06` v2 | 최상 1 · 상 2 — 들보가 세 조각, 내가 찍은 구멍이 볼트로 읽힘 |
| `s04p06` v5 | 최상 0 · 상 2 · 중 3 · 하 3 → **조건부 가** (상 2건 후보정 후 배포) |

**검수 지시문에 「무엇을 세고 무엇을 재라」를 구체적으로 적으면 품질이 확 오른다.**
이번에 효과가 컸던 지시:
- 「좌·우 개구부의 (a)테 두께 (b)흰 고리 최대 휘도 (c)보어 중심 RGB (d)보어 bbox를 **표로 비교**해라」
- 「들보 오른쪽 끝 x와 통 건물 왼쪽 외곽 x를 재서 **빈 간격의 폭을 픽셀로** 답해라」
- 「캔버스를 3×3으로 나눠 각 칸의 잉크 비율을 내라」 → 상단 중앙 0.80%(백지)를 잡아냈다
- 「직전 판은 ~로 실격이었다. **같은 실수가 재발했는지부터** 확인해라」

그리고 **내가 후보정한 자리를 미리 알려 주고 「이질적이면 반드시 지적해라」**라고 쓰면
자기 검열 없이 냉정하게 잡아 준다 — 규칙 23이 그렇게 나왔다.

---

# 참고 — `s04` 장면의 잉크 밀도 (lum<120 면적비)

| 패널 | 잉크 |
|---|---|
| `s04p01` | 7.65% |
| `s04p02` | 9.49% |
| `s04p03` | 12.02% |
| `s04p04` | 15.43% |
| `s04p05` | 11.21% |
| **`s04p06`** | **10.17%** ✅ |

새 그림이 이 범위를 크게 벗어나면 같은 장면에서 **이질적으로 보인다.**
v2는 7.37%로 하단이었고 「선이 얇은 게 아니라 화면이 비었다」는 판정을 받았다 —
선 굵기(중앙값 2.83px)는 형제와 같았고 **소품이 화면 높이의 21.7% 띠에 눌려 있던 것**이 원인이었다.
