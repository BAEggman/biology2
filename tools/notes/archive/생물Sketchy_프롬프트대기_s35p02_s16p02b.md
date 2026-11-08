# 붙여넣을 프롬프트 3개 + 심볼 충돌 처리 결과 (2026-08-15)

Gemini **Pro + 확장된 사고 모델**, 각각 **새 대화**에 통째로 붙여넣는다.
그림을 받으면 픽셀 검증 → 사실표 정정 → 빌드·테스트·래칫·푸시.

---

## ★ 먼저 — 심볼 충돌 셋 중 **둘은 그림 문제가 아니었다**

전면 감사가 「높음」으로 올려 뒀던 것을 실측해 보니 둘은 **낱말 문제**였고,
그림을 하나도 안 고치고 배포까지 끝냈다.

| 충돌 | 판정 | 근거 | 커밋 |
|---|---|---|---|
| **s17p03 자물쇠** | ✅ 그림 정상 | 자물쇠 어두운 화소 평균 **RGB (86,79,71) = 검은 쇠**. 덱 규칙은 「**금색** 자물쇠 = 약물」이다(견줌: s02p01 금색 화소 25.9% vs 여기 13.4%, 그나마 대부분 둘레 나무 문짝). 게다가 여기 자물쇠는 **막는** 물건이 아니라 멀리서 온 열쇠가 **여는** 대상이라 방향도 반대다 | `f9b5aa1` |
| **s38p03 고리** | ✅ 그림 정상 | 오각판 고리 실측 **왼쪽 5개 · 오른쪽 4개**(오른쪽 꼭짓점 하나 빔) — 사실표와 정확히 일치. 낱말 충돌은 s38p01#5를 「두 겹 고리」→「**겹친 원판 둘**」로 바꾼 `7b2fb05`에서 이미 갈렸다 | `7c05413` |
| **s32p02 물방울** | ❌ **그림을 고쳐야 한다** | 이 패널에서 **물 = H⁺**인데 #4만 **물방울 = H₂O**다 | 아래 ③ |

★ **교훈**: 감사표의 「심볼 충돌」은 낱말만 보고 올린 것이 섞여 있다.
**그림을 픽셀로 재 보기 전에는 재생성을 결정하지 않는다.** 오늘 두 건을 그렇게 아꼈다.

---

## ① s35p02 「비율이 바뀌는 세 갈래」 — 유전자 흐름 칸

**왜**: 오른쪽 두 웅덩이가 처음부터 반반이라 「흐름으로 같아졌다」의 **변화가 그림에 없다.**
위→아래 배치가 왼쪽·가운데의 「전/후」와 같은 문법이라 **한 집단의 전후**로도 읽힌다.
**고침**: 오른쪽만 **좌우 두 웅덩이 × 위(닫힘·서로 다름) / 아래(열림·같아짐)**.

```
Hand-drawn illustration for a study card, vintage children's science book style: clean black ink outlines, soft colored-pencil shading, flat cream-ivory background; the only colours are pale blue-green water, warm brown wood and muted clothes. THREE COLUMNS side by side, each showing a population of beads floating in water. Every bead is either a solid dark-grey bead or a hollow white bead. COLUMN 1 on the left, natural selection: a tall flask-shaped upper pool and a lower pool joined by a narrow neck. The upper pool holds an even mix, about half dark beads and half white beads. Across the neck stands an upright round sieve, held by a person standing beside it. White beads are caught on top of the sieve in a heap and none get through. The lower pool contains ONLY dark beads. COLUMN 2 in the middle, genetic drift: the same two pools, but the neck between them is pinched extremely narrow and NOBODY stands there. The upper pool is again about half dark and half white. Only a thin trickle of beads passes the narrow neck. The lower pool is almost entirely white beads with just two or three dark ones. Below that lower pool, drawn fully inside the frame, a person dips a ladle into it and pours one scoop into a separate small puddle standing apart on the ground, and that small puddle contains ONLY dark beads. COLUMN 3 on the right, gene flow: this column is built differently from the other two. It shows FOUR pools arranged as two pairs, one pair above the other, and in each pair the two pools sit SIDE BY SIDE, left and right, joined by a wooden sluice gate between them. In the UPPER pair the sluice board is fully lowered and shut; the left pool of that pair is almost all dark beads and the right pool is almost all white beads, so the two pools look clearly different from each other. In the LOWER pair the same sluice board is raised wide open, beads stream through the opening in BOTH directions, and now BOTH pools hold the same even mix of about half dark and half white. There are exactly two arrows in the whole picture, both in that lower opening: one above pointing right and one below pointing left. No text, letters, numbers or labels anywhere.
```

**검증**: 왼쪽 아래 = 검은 구슬만 · 가운데 목이 극단적으로 잘록하고 사람 없음 · 국자와 작은 웅덩이가
화면 안에 · 오른쪽 **위** 두 웅덩이가 확연히 다름 · 오른쪽 **아래** 둘이 같아짐 · 화살표 양방향 둘.

---

## ② s16p02b 「2차 전달자 — 판과 자갈 창고」

**왜**: 카드 다섯 중 셋이 PIP₂ → IP₃ + DAG 축인데 그림엔 민 판 **둘** + 열쇠구멍 판 하나로 **세 조각**.

```
Hand-drawn illustration for a study card, vintage children's science book style: clean black ink outlines, soft colored-pencil shading, flat cream-ivory background; muted palette of pale teal machine, grey stone, warm brown wood and muted clothes. An interior workshop room drawn in simple isometric view. On the LEFT a pale teal splitting machine stands on legs with a flat conveyor running into it, and ONE whole flat grey rectangular plate lies on that conveyor going in. The machine has one output chute, and out of it come EXACTLY TWO pieces and no more: the whole plate has been broken into exactly two halves along a jagged zig-zag line, so the two halves obviously fit back together. ONE half has a large keyhole cut right through it. The OTHER half has no keyhole and is completely plain. The plain half stays where it came out and lies flat on the workbench beside the machine; it is the ONLY plain piece in the picture, there is no second plain plate and no stack of plates anywhere. A worker in a cap carries the keyhole half away from the machine toward the right, holding it upright with both hands so the keyhole is clearly visible. On the RIGHT stands a heavy grey stone safe with its metal door swung open. The opening in the safe is cut in exactly the same keyhole shape as the hole in the plate the worker carries, the same outline and the same proportions. Small pale pebbles are pouring out of that keyhole-shaped opening and spilling across the floor toward the front, and a second worker crouches on the floor beside the spilled pebbles. There are no rings, no loops, no circles and no coiled shapes anywhere in the picture. No text, letters, numbers or labels anywhere.
```

**검증**: 조각이 정확히 둘 · 갈라진 면이 맞물림 · 민 반쪽이 하나뿐 · 열쇠구멍과 금고 구멍이 같은 모양 ·
**고리·코일이 하나도 없음**(앞방 cAMP의 「구부리기」와 갈리는 문법).

---

## ③ s32p02 「담장 끝과 물레방아」 — 물방울을 「마개 봉한 병」으로

```
Hand-drawn illustration for a study card, vintage children's science book style: clean black ink outlines, soft colored-pencil shading, flat cream-ivory background; muted palette of warm red brick, grey stone, pale blue-green water, sandy ground and muted clothes. A long brick wall runs diagonally across the picture from the lower left to the upper right, seen from the near side. On the FAR side of the wall, at the left, the water is piled up very high, its surface far above the ground on the near side. On the NEAR side the ground is dry sandy earth with only a shallow puddle. The whole base of the wall is finished with a solid course of grey stone blocks with no gaps: there is exactly ONE opening in the entire wall, a single round-topped arch near the left, and no other hole, crack, pipe or drain anywhere along the base. Through that one arch the piled-up water pours down and turns a single large wooden water wheel standing in the opening, and the water that has passed runs out onto the near ground and spreads into the shallow puddle. Further along the wall to the right there is a doorway, and in that doorway one worker hands a bundle to a second worker who has just stepped out. In the FOREGROUND on the right stands a third worker holding that bundle; exactly TWO water drops float just above his open hands, drawn as the same pale blue-green water as the water piled behind the wall; and on the ground in front of him stands ONE small glass bottle filled with that same water and closed with a cork stopper pushed firmly in. There are no beads, no pebbles and no round balls anywhere in the picture. No text, letters, numbers or labels anywhere.
```

**받은 뒤 사실표 #4**
- 소품: 「짐 + **물 두 방울** → **마개를 봉한 병 하나**」
- 사실: 「최종 전자수용체 산소가 전자와 **H⁺ 둘**을 받아 물이 된다. ★ 이 그림에서 흐르는 물은 전부 H⁺이고,
  **봉한 병만이 완성된 H₂O**다 — 봉했으니 더 이상 기울기에 끼지 않는다」

---

## ★ Gemini를 내가 직접 돌리기 위한 조건 (2026-08-15 확정)

컴포저에 글자를 넣는 유일한 길이 **실제 키보드 타이핑**인데, 키 입력은
**화면에 보이는(visible) 탭**으로만 들어간다.

```js
// 시작 전에 반드시 이걸로 확인한다
document.visibilityState   // 'visible' 이어야 한다. 'hidden' 이면 아무리 쳐도 안 들어간다
```

- `hidden` 이면 `.ql-editor` 길이가 **0**으로 나온다 — 이게 그 신호다.
- 창을 앞으로 꺼내는 것은 **도구로 못 한다**(`resize_window`·새 탭 만들기 둘 다 안 됨).
  **사용자가 Chrome 창을 한 번 클릭해 앞에 두고 그대로 두어야** 한다.
- `+` 업로드 메뉴와 보내기 버튼은 **클릭 자체가 안 먹는다** → 기존 그림을 올려 편집시키는 길은 막혀 있다.
  그래서 수정은 전부 **전체 재생성**이다.
- 모드 메뉴는 **안쪽 원소 하나에만** 클릭 이벤트를 쏜다(둘 다 쏘면 토글이 두 번 돼 원위치).
  Pro와 「확장된 사고 모델」은 **각각 따로** 켠다.
