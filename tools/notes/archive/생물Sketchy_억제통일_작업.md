# 「억제」 심볼 통일 — 진단과 작업

2026-08-02 · 590행 전수 + Sketchy 공식 자료 대조

---

## 1. 앞선 진단을 정정한다 (두 번째)

내가 **「억제 8장면을 자물쇠로 통일」**이라 했다. **틀린 틀이었다.**

Sketchy 공식 설명은 이렇다:

> every character and action corresponds to **a specific mechanism of action, indication, side effect, or clinical consideration**

**심볼은 「구체적 사실」 하나에 붙는다.** 「억제」 같은 추상 범주에 붙는 게 아니다. 반복 심볼(catalase cat)도 **특정 실체**에 붙는다.

그래서 「억제니까 전부 자물쇠」로 뭉개면 **정보가 사라진다.** 경쟁적 저해(가짜 열쇠)와 비경쟁적 저해(옆구리 망치)는 **기전이 달라서 다르게 그린 것**이고, 그 차이가 곧 시험 포인트다.

---

## 2. 다시 세어본 결과

26행 / 12장면을 한 행씩 읽으니 **「억제」는 하나가 아니라 셋**이다.

| 갈래 | 심볼 | 상태 |
|---|---|---|
| **약물·독물이 표적을 막는다** | 🔒 **금색 자물쇠** | **6장면 일관** — s02 s10 s17 s19 |
| **단백질이 단백질·DNA를 억제한다** | 🧍 **사람이 몸으로 막는다** | **4장면 일관** — s15 s19p02 s25p01 s25p02 |
| **구조적으로 못 하게 한다** | 개별 | s11(쐐기) 등 — 통일 대상 아님 |

**두 개의 규칙이 이미 각각 잘 지켜지고 있었다.** 내가 이걸 하나로 보고 「8장면 미적용」이라 센 것이다.

### 진짜 미적용 — 3장면뿐

약물·독물인데 **자물쇠 표지가 없는** 곳:

| 패널 | 무엇이 빠졌나 | 약물 |
|---|---|---|
| `s14p03` 억제제 격자 | 2×2 네 자리 전부 | 콜히친 · 사이토칼라신 · 택솔 · 팔로이딘 |
| `s24p01` 저해제 세 자리 | 가짜 열쇠 · 망치 · 껌 | 경쟁적 · 비경쟁적 · 무경쟁적 저해제 |
| `s32p03` 방해자 셋 | 벽돌 봉함 · 축의 쐐기 | 시안화물/CO · 올리고마이신 |

세 장면의 공통점: **약을 여러 개 늘어놓은 격자형 패널**인데, 같은 구조인 `s10p02`(억제제 자물쇠)만 자물쇠를 썼다.

### 충돌 — 1행뿐 (이미 고쳤다)

`s10p01`에서 **자물쇠 = 코돈**이었다. 바로 옆 `s10p02`에서는 **자물쇠 = 억제제**다. **한 장면 안에서 충돌**이라 가장 아팠다.

```
「머리 모양이 서로 다른 열쇠 셋이 같은 자물쇠 하나에」
                              ↓
「머리 모양이 서로 다른 열쇠 셋이 같은 열쇠구멍 하나에」
```

**그림은 안 건드렸다. 부르는 이름만 바꿨다.** 이제 자물쇠 11행이 전부 「막는다」로 통일됐다.

---

## 3. 핵심 원칙 — 바꾸지 말고 **얹어라**

세 장면 다 **기존 구분을 그대로 두고 자물쇠만 추가**한다.

- `s24p01`의 가짜 열쇠 / 망치 / 껌은 **그대로 둔다** — 기전 차이가 사실이다
- 거기에 **작은 금색 자물쇠를 단다** — 「이 셋은 약이다」라는 표지

정보 손실 0, 표지 추가. 이게 Sketchy가 실제로 하는 방식이다 — 장면은 고유하되 **약이라는 표지는 공통**.

> **자물쇠를 달지 않는 것**: `s32p03`의 **DNP(짝풀림제)**. 이건 막는 게 아니라 **새게 하는** 것이다. 자물쇠를 달면 거짓말이 된다. 담장 구멍 그대로 둔다.

---

## 4. 재생성 프롬프트 3개

**기존 이미지를 참조로 넣고 최소 편집만 시킨다.** 전체 재생성보다 안전하다 — 통과한 요소가 사라지는 교체 현상(마스터노트 보조규칙)을 피한다.

각각 **새 창에서** 돌린다(규칙 7 — 앞 그림의 배경이 넘어온다).

---

### ① `s14p03` — 세포 물류센터 · 억제제 격자

```
Keep this image exactly as it is. Change nothing about the existing layout,
figures, poses, props, colors, or background.

Add exactly four small gold padlocks, one per quadrant, each hanging on the
restraint that is already in that quadrant:
- top-left: a gold padlock on the bound wrists
- top-right: a gold padlock on the bound wrists
- bottom-left: a gold padlock clamped on the iron bar
- bottom-right: a gold padlock clamped on the iron bar

Each padlock is small — at least four times smaller than the head of the
nearest figure. Bright metallic gold, clearly distinct from the muted palette.
No other change. No extra props, no unrelated tools, no decorative clutter.
```

> 자물쇠를 **구속 도구 위에** 단다. 「중합 억제(못 붙임) / 탈중합 억제(못 뗌)」 구분은 손목·쇠막대가 계속 나른다.

---

### ② `s24p01` — 효소 공장 · 저해제 세 자리

```
Keep this image exactly as it is. Change nothing about the existing layout,
figures, poses, props, colors, or background. In particular keep the fake key
in the keyhole, the hammer at the side, and the gum, exactly as drawn.

Add exactly three small gold padlocks, one attached to each of the three
interfering objects:
- one gold padlock hanging from the fake key that is stuck in the keyhole
- one gold padlock hanging from the hammer
- one gold padlock stuck onto the gum

Do not add a padlock to the pile of spare keys.

Each padlock is small — at least four times smaller than the head of the
nearest figure. Bright metallic gold. No other change.
No extra props, no unrelated tools, no decorative clutter.
```

> **여분 열쇠 더미(기질 농도)에는 안 단다.** 그건 약이 아니라 기질이다.

---

### ③ `s32p03` — 물레방아 담장 · 방해자 셋

```
Keep this image exactly as it is. Change nothing about the existing layout,
figures, poses, props, colors, or background. In particular keep the hole in
the wall with leaking water and the reddened glowing wall exactly as drawn.

Add exactly two small gold padlocks:
- one gold padlock on the brick-sealed pump house at the end of the wall
- one gold padlock on the wedge driven into the waterwheel axle

Do not add any padlock to the leaking hole in the wall.

Each padlock is small — at least four times smaller than the head of the
nearest figure. Bright metallic gold. No other change.
No extra props, no unrelated tools, no decorative clutter.
```

> **담장 구멍(DNP)에는 안 단다.** 짝풀림제는 막는 약이 아니다. 「담장이 성한가」로 셋을 가르는 원래 설계가 그대로 산다.

---

## 5. 생성 후

받은 이미지 3장을 대화에 올려주면:

1. 사실표에 자물쇠 행 추가 (`s14p03`·`s24p01`·`s32p03`)
2. `img/*.webp` 교체 + sketchy.html 내장분 교체
3. `npm run build` → 검증 118종
4. 배포

**실패 판정 기준**: 자물쇠가 지정한 개수만큼, 지정한 물건 위에, 다른 건 안 바뀐 채로 붙었는가. 하나라도 어긋나면 재시도(새 창).

---

## 6. 한 줄

**「억제」는 하나가 아니라 셋이었고, 두 규칙은 이미 잘 지켜지고 있었다.
진짜 할 일은 격자형 패널 세 장에 자물쇠를 얹는 것과, 이미 고친 이름 충돌 하나였다.**
