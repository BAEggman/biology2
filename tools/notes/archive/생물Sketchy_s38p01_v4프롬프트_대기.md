# s38p01 재생성 — v4 프롬프트 (전송 대기)

**상태**: v3를 뽑아 검증했고 실패 판정. v4를 썼는데 **Gemini 전송이 막혀 못 보냈다.**
다음 세션에서 아래 프롬프트를 **그대로** 붙여 넣으면 된다. 다시 쓰지 마라.

---

## v3 결과 판정 — 무엇이 됐고 무엇이 안 됐나

한 롤에 셋을 해소하려 했다. **둘은 됐고 하나는 됐는데 다른 데가 무너졌다.**

| 항목 | v3 결과 |
|---|---|
| 퓨린 = 2고리 (E1-27) | ✅ **해결**. 「겹친 납작 원판 둘(8자)」로 바꾸니 첫 판에 정확히 둘로 나왔다. 원판을 **쌓지 말고 옆으로 붙이라**고 한 것이 주효했다 |
| 쇠못 → 나무못 (s11 재질 문법) | ✅ **해결**. 금속 너트가 사라지고 나무 못머리가 양쪽 기둥에 붙었다 |
| 구슬 → 나무 블록 (s39p03 충돌) | ✅ **해결**. 둥근 구슬이 없어지고 네모 블록이 됐다 |
| **비틀림(한 바퀴)** | ❌ **통째로 사라졌다.** Gemini가 스스로 「spiral twist는 못 그렸다, 평평한 직선 구조가 됐다」고 실토했다 → E1-30·E1-30#1·E1-30#2·E1-33 넷의 근거가 없어진다 |
| **화살표 둘(역평행)** | ❌ **통째로 사라졌다** → E1-18·E1-19 둘의 근거가 없어진다 |
| 확대 칸 갈고리 2 vs 3 | ❌ 초록 쪽이 **S자 갈고리 하나**로 나왔다(2개여야 한다). 붉은 쪽은 3개로 정확 |
| 오각형 판 | △ 있기는 한데 네모 블록과 잘 안 갈린다 |

**그래서 v3은 안 쓴다.** 옛 그림이 비틀림과 화살표를 갖고 있어 옛 그림이 낫다.
v3 원본은 `/tmp` 산물이라 남지 않는다 — v4로 새로 뽑는다.

## v4에서 바꾼 것

1. **비틀림을 「두 번 교차」로 못 박았다** — 「나선」이라는 낱말로는 안 된다.
   *the two rails cross over each other EXACTLY TWICE* + 어느 쪽이 앞으로 지나가는지까지 지정.
2. **화살표에 「빠뜨리지 마라」 제목을 붙이고** 자리·방향·길이를 따로 문장으로 못 박았다.
3. **오각형 판을 「아이가 그린 집 모양(밑변 평평·양옆 수직·뾰족한 지붕)」**으로 묘사하고
   네모 블록보다 **크다**고 명시.
4. 초록 확대 칸을 **「두 갈고리가 나란히 선 한 쌍 — 하나도 아니고 셋도 아니다」**로 다시 못 박았다.

---

## ★ 보낼 프롬프트 (v4) — 그대로 붙여 넣는다

```
Draw ONE hand-drawn illustration for a study card, in the style of a vintage children's science book: clean black ink outlines with soft colored-pencil shading, on a flat cream-ivory background. Muted palette only — pale wood, olive green, rusty red, warm brown, charcoal grey.

SCENE: a wooden ladder that WINDS like a spiral staircase, running diagonally across the frame from the lower-left corner up to the upper-right corner. Separately, in the lower-right area of the frame, two single rungs are drawn again at a much larger size.

THE WINDING — this is the most important thing in the picture
The two side rails of the ladder are not parallel lines; they wind around each other like the two strands of a twisted rope.
Along the length of the ladder the two rails cross over each other EXACTLY TWICE, which is one complete turn of the twist.
At the first crossing the left rail passes in front of the right rail; at the second crossing the right rail passes in front of the left rail.
Between the crossings the ladder looks wide, and at each crossing the ladder pinches narrow, so the eye can see it turning.
Do not draw a flat straight ladder.

THE TWO SIDE RAILS
Each rail is built from just two kinds of parts, joined alternately: a big flat PENTAGON PLATE of pale wood, then a small SQUARE WOODEN BLOCK, then a pentagon plate, then a square block, repeating from the bottom end to the top end.
Every pentagon plate is unmistakably five-sided, shaped like a child's drawing of a house: a flat bottom edge, two upright sides, and a pointed roof on top.
Every square block is a small plain cube of pale wood, clearly smaller than a pentagon plate, with no point and no roof.
There are no beads, no round balls and no spheres anywhere on the rails.
There is no rope, no cord, no string, no chain and no wire anywhere in the whole picture.
At every place where a pentagon plate meets a square block — on the left rail and on the right rail alike, with none skipped — one small PALE WOODEN PEG is driven through, and its round wooden head is clearly visible from the front.
Every peg in the picture is plain pale wood, the same wood as the plates and the blocks.
There are no metal nails, no nuts, no bolts, no screws, no washers and no grey hardware of any kind in the picture.

THE RUNGS
There are exactly TEN rungs from the bottom end of the ladder to the top end — ten rungs in that one complete turn.
Each rung is two short wooden bars that meet at the middle of the rung; the outer end of each bar sits in a pentagon plate on its rail.
At the inner end of one bar is a BIG PIECE: exactly two flat round plaques fused side by side, like a figure eight lying flat.
At the inner end of the other bar is a SMALL PIECE: exactly one flat round plaque on its own.
Every rung has exactly one big piece and exactly one small piece, so all ten rungs are the same length and the ladder keeps the same width all the way along.
The big piece is on the left rail in some rungs and on the right rail in other rungs, in an irregular order.
In any one rung the two pieces are the same colour: some rungs are olive green and some rungs are rusty red.
Where the big piece and the small piece meet at the middle of the rung, one small charcoal-grey clasp bites them together.

THE TWO ARROWS — these must not be left out
There are exactly TWO arrows in the picture, drawn in the same black ink as the outlines, floating in the empty cream background.
One long thin arrow floats in the empty space to the LEFT of the ladder, running parallel to the rails and pointing UP toward the top-right.
One long thin arrow floats in the empty space to the RIGHT of the ladder, running parallel to the rails and pointing DOWN toward the bottom-left.
Each arrow is a straight line with one solid black arrowhead, and each is about as long as three rungs are wide.

THE TWO ENLARGED RUNGS, LOWER RIGHT
Two single rungs are drawn much larger, one above the other, clearly separated from the ladder.
In both of them the big piece is on the left and the small piece is on the right.
The big piece is exactly TWO flat round plaques fused side by side — unmistakably two plaques, never three, and never a stack of discs.
The small piece is exactly ONE flat round plaque.
The hooks sit in the gap halfway between the big piece and the small piece.
In the upper enlarged rung the two pieces are olive green, and there are exactly TWO charcoal-grey hooks: two separate hooks standing side by side, a clear pair — not one hook, not three.
In the lower enlarged rung the two pieces are rusty red, and there are exactly THREE charcoal-grey hooks standing side by side.
The clasps, the hooks and the arrowheads are the only dark objects in the picture.

No text, no letters, no numbers and no labels anywhere in the image.
```

---

## 받은 뒤 반드시 할 것 — 픽셀로 센다

1. 기둥 **양쪽**에 못머리가 있는가 (v3 이전엔 오른쪽에만 있었다)
2. 확대 칸: 큰 조각이 **원판 둘**인가 · 갈고리가 **2개 / 3개**인가
3. 레일이 **두 번 교차**하는가
4. 화살표가 **정확히 둘**이고 방향이 반대인가
5. 칸이 **열 개**인가

## 통과하면 사실표를 고친다 (★그린 것만 건다)

| 행 | 지금 | 고칠 것 |
|---|---|---|
| #0 | 「칸이 기둥에 붙는 자리마다 박힌 **쇠못**」 | 「기둥에서 오각판과 나무 블록을 잇는 **나무못**」 — 못이 나무인 것이 이 골격이 DNA라는 뜻이다(s11 재질 문법과 같은 편) |
| #2 | 「오각형 판과 **구슬**이 번갈아」 | 「오각형 판과 **네모 나무 블록**이 번갈아」 |
| #5 | 소품 자리에 「두 겹 **고리**」 | 소품 낱말에서 「고리」를 뺀다 → 「**겹친 원판 둘** / 원판 하나」. 사실 문장에서만 화학 용어로 「2고리·1고리」를 쓴다 |

## ★ 새로 찾은 심볼 충돌 — 같은 장면 s38 안이다

- `s38p03#6` 「오각판 다섯 꼭짓점의 **고리**」 = **-OH**
- `s38p01#5` 「두 겹 **고리** / 한 겹 **고리**」 = **염기 고리**

같은 게이트, 심지어 **같은 장면**에서 「고리」가 두 뜻이다. 당장은 s38p01 소품 낱말에서
「고리」를 빼는 것으로 피하고, **s38p03을 다시 그릴 때 -OH를 「작은 손잡이」로 바꾼다**.
작업큐에 남긴다.
