# s32p02 「담장 끝과 물레방아」 — 재생성 프롬프트 (2026-08-15)

Gemini **Pro + 확장된 사고 모델**, **새 대화**에 통째로 붙여넣습니다.

---

## 왜 고치나 — 그림을 재 보니 결함이 셋이다

현재 사실표 #4는 「짐 + 작은 구슬 둘 → 물방울 하나」인데, 그림을 확대해 보면:

| | 사실표 | 그림 실물 | 점검표 |
|---|---|---|---|
| **짐** | 앞쪽 인부가 들고 있다 | **안 들고 있다.** 위 손은 빈 주먹이고 짐은 뒤쪽 문간에만 있다 | ② 유령 |
| **구슬** | **둘** | **하나** (810~900, 700~790 구간 확대 실측) | ⑤ 셀 수 있는 것 |
| **물방울** | H₂O | 이 그림에서 물은 담장 뒤에 쌓인 것도 물레방아를 돌리는 것도 **전부 H⁺** | ④ 한 상징 한 사실 |

★ 감사표는 셋째(심볼 충돌)만 잡았다. 픽셀로 재니 앞의 둘이 더 나왔다.
**재생성 전에 그림을 재라**는 규칙이 이번에는 「고쳐야 한다」 쪽으로 답했다
(s17p03·s38p03에서는 「안 고쳐도 된다」 쪽이었다). 규칙이 양쪽으로 다 쓰인다.

## 고치는 방향

- **구슬을 없애고 물 두 방울로.** 그러면 이 그림에서 **물 = H⁺**가 끝까지 일관된다.
- **완성된 H₂O는 「마개를 봉한 병」.** 봉했으니 더 이상 흐르지 않는다 = 기울기에 끼지 않는다.
- **짐을 앞쪽 인부의 팔에 확실히 안긴다.** 한 팔로 가슴에 끼고, 다른 손은 펴서 물방울을 받는다.

---

## 프롬프트

```
Hand-drawn illustration for a study card, vintage children's science book style: clean black ink outlines, soft colored-pencil shading, flat cream-ivory background; muted palette of warm red brick, grey stone, pale blue-green water, sandy ground and muted clothes. A long brick wall runs diagonally across the picture from the lower left to the upper right, seen from the near side. On the FAR side of the wall, at the left, the water is piled up very high, its surface far above the ground on the near side. On the NEAR side the ground is dry sandy earth with only a shallow puddle. The whole base of the wall is finished with a solid course of grey stone blocks with no gaps: there is exactly ONE opening in the entire wall, a single round-topped arch near the left, and no other hole, crack, pipe or drain anywhere along the base. Through that one arch the piled-up water pours down and turns a single large wooden water wheel standing in the opening, and the water that has passed runs out onto the near ground and spreads into the shallow puddle. Further along the wall to the right there is a doorway, and in that doorway one worker hands a cloth-wrapped bundle to a second worker who has just stepped out of it. In the FOREGROUND on the right stands a third worker turned to face the viewer. He clutches an identical cloth-wrapped bundle against his chest with his LEFT arm, so that bundle is unmistakably in his own hands. His RIGHT hand is open with the palm turned up and empty. Floating just above that open right palm are exactly TWO tear-shaped drops of the same pale blue-green water as the water piled behind the wall, drawn side by side as a pair with one slightly higher than the other, and nothing else floats above his hand. On the sandy ground directly in front of his feet stands ONE small clear glass bottle, filled to the shoulder with that same pale blue-green water and stoppered shut with a brown cork pushed firmly into its neck; that corked bottle is the only container in the picture. There are no beads, no pebbles, no marbles and no round balls anywhere in the picture, and nothing is falling out of anyone's hands. No text, letters, numbers or labels anywhere.
```

---

## 받은 뒤 확인할 것 (픽셀로)

- 앞쪽 인부가 **짐을 실제로 안고 있는가** (지금 판의 유령이 이것이다)
- 펴진 손 위 물방울이 **정확히 둘**인가
- **구슬·자갈·공이 하나도 없는가**
- 병이 **하나**이고 **마개가 꽂혀** 있는가
- 담장 밑동에 아치 **하나** 말고 구멍이 없는가 (이건 원래 맞았다 — 증발 방지 확인용)

## 받은 뒤 사실표 #4를 이렇게 고친다

- 소품: 「가슴에 안은 짐 + 편 손 위 **물 두 방울** → 발 앞에 **마개를 봉한 병 하나**」
- 사실: 「최종 전자수용체 산소가 전자와 **H⁺ 둘**을 받아 물이 된다.
  ★ 이 그림에서 **흐르는 물은 전부 H⁺**이고, **봉한 병만이 완성된 H₂O**다 —
  봉했으니 더 이상 기울기에 끼지 않는다」

## 프롬프트를 어떻게 보내나

Gemini 탭이 `document.visibilityState === 'visible'` 이어야 실제 키 입력이 들어간다.
`hidden` 이면 `.ql-editor` 길이가 0으로 나온다. 창을 앞으로 꺼내는 것은 도구로 못 한다 —
**사용자가 Chrome 창을 화면 맨 앞에 두어야 한다.** 그럴 상황이 아니면 이 문서의
프롬프트 블록을 사용자가 직접 붙여넣는 쪽이 빠르다.
