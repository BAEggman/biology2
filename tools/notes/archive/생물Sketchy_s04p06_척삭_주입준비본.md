# `s04p06` 「척삭 상회 — 위·앞·뒤가 곧 이름이다」 — 주입 준비 완료본

**그림만 있으면 바로 들어간다.** 설계·근거·사실표·bx·q블록·함정·숫자·카드링크가 전부 확정돼 있다.
크롬 확장이 멈춰 생성만 못 했다. 아래 프롬프트를 Gemini **Pro**(Flash 아님) 새 채팅에 붙여넣고
나온 그림을 올리면 검수→주입→배포만 남는다.

> **왜 이 패널인가** — 사용자 발언: 「나의 오답 데이터를 보면 척삭동물의 특징을 많이 틀린 걸 볼 수 있다.」
> 현재 `s04p05`에는 척삭동물 4대 특징 중 **척삭 하나만** 그려져 있다(5행). 나머지 셋이 없다.

---

## 노리는 것

**척삭동물 4대 특징** — 자리가 곧 이름이다:

| 특징 | 소품 | 왜 그 자리인가 |
|---|---|---|
| **척삭**(notochord) | 지붕 밑을 앞뒤로 관통하는 **굵은 통짜 들보** | 속이 찬 막대 하나가 몸을 꿴다 |
| **등쪽 속 빈 신경관** | 그 들보 **바로 위**에 얹힌 **속 빈 회색 관** | 「등쪽」이라 위, 「속 빈」이라 관 |
| **인두열**(pharyngeal slits) | **앞벽**에 세로로 뚫린 좁은 틈 여럿 | 인두 = 목이라 앞쪽 |
| **항문 뒤 꼬리**(post-anal tail) | **뒷문보다 더 뒤로** 뻗은 부속 건물 | 뒷문(항문)보다 **뒤**에 있는 것이 이름 전부 |

**+ 두삭 vs 피낭** — 오른쪽 작은 가게가 멍게다. 성체는 **인두열(새열)만** 남기고 다 잃는다.

## 기출 근거 (기계 대조 완료)

- **BM하 #1176** 「척삭동물 중 유생 때는 인두·새열·근육질 꼬리에 척삭과 배신경색을 갖지만, 성체가 되며 꼬리·척삭·신경계 대부분이 없어지고 **새열만 갖는** 동물은?」 → **④ 멍게**. 오답 ① 창고기(평생 척삭 유지) ★★
- **BM하 #1198 ③** 「척삭동물의 4가지 특징은 **신경다발(신경삭)·척삭·인두열·꼬리**이다」 — 옳은 선지로 출제 ★
- 캠벨 34장

---

## 프롬프트 (Gemini Pro · 새 채팅 · 첨부 없음)

```
Hand-drawn educational mnemonic illustration. Ink linework with soft watercolour washes. Warm cream and pale gold palette, with dusty teal and brick red accents. Thin even ink outlines of light weight, light flat washes, no heavy shading. Flat even lighting, plain off-white background. Slightly cartoonish, clear silhouettes. Every object distinctly separated and readable. Single square panel, exactly as wide as it is tall. Draw it straight from the side, flat on, not from an angle and not from above. The drawing runs right to the edges — there is no drawn border or frame line around the picture. No text, no letters, no numbers anywhere in the image. No lettering or signage anywhere. No extra props, no unrelated tools, no decorative clutter.

A quayside street seen straight from the side. Two wooden shop buildings stand on the stone quay, a big one on the left and a small one on the right, with a gap of empty street between them. There are no people anywhere in the picture.

THE BIG SHOP ON THE LEFT. One straight thick wooden beam runs horizontally along the whole length of this building, just under the roofline, and both of its cut ends stick out past the walls so it is plainly one single solid rod. Resting directly on top of that beam, and running parallel along the whole same length, is one grey pipe, and at each end of the pipe you can see straight into its open round mouth so it is plainly hollow. The beam is solid and below; the pipe is hollow and above it.

The front wall of the big shop, the wall facing left towards the street, has a row of tall narrow vertical slits cut through it from top to bottom, evenly spaced, so daylight shows through them.

The rear wall of the big shop has one small closed back door in it. Beyond that back door, further to the right, the same building continues as a long low extra wing that juts out well past the back door and ends in a rounded tip. The back door is plainly in front of that extra wing, and the extra wing is plainly behind the back door.

THE SMALL SHOP ON THE RIGHT. It is squat and rounded and sits fixed flat on the stone quay with no gap underneath. It has the same row of tall narrow vertical slits cut through its front wall as the big shop. But it has no beam at all, no pipe at all, and no extra wing behind it — its back wall is plain and flat. One wide funnel opens out of its roof and a thin stream of water pours down into that funnel.

Hanging on the outside front wall of the small shop is one framed picture, and the picture shows a tiny version of the big shop on the left, complete with its beam, its pipe, its slits and its extra wing.

Apart from those two buildings, the framed picture, the funnel and the stone quay, there is nothing else in the picture.

The composition fills the entire frame from edge to edge with no empty space above or below.
```

**검수 때 반드시 셀 것**: 들보가 **관 아래**인가(위아래가 바뀌면 실격) · 뒤채가 **뒷문보다 뒤**인가 ·
작은 가게에 **틈만 있고 들보·관·뒤채가 없는가** · 액자 속 그림에 **넷이 다 있는가** · 사람이 0명인가.

---

## 주입할 것 (전부 확정)

**패널 위치**: `s04` 장면 `panels` 배열 끝 (`s04p05` 뒤)
**`pc`**: `["S-AN-13"]`

### 사실표

```
['지붕 밑을 앞뒤로 관통하는 굵은 나무 들보 하나 — 양 끝이 벽 밖으로 튀어나와 통짜임이 보인다','척삭(notochord). 속이 찬 막대 하나가 몸을 앞뒤로 꿴다. 척추가 아니라 척삭이다 — 척추동물에서는 나중에 척추가 이 자리를 대신한다'],
['그 들보 바로 위에 나란히 얹힌 회색 관 — 양 끝이 뚫려 속이 보인다','등쪽 속 빈 신경관(dorsal hollow nerve cord). 「등쪽」이라 들보보다 위에 있고 「속 빈」이라 관이다. 무척추동물의 신경삭은 배쪽이고 속이 차 있다 — 정확히 반대다'],
['앞쪽 길 쪽 벽에 세로로 뚫린 좁은 틈 여럿 — 빛이 새어 나온다','인두열(pharyngeal slits). 인두는 목이라 앞쪽에 있다. 물을 걸러 먹는 데 쓰다가 어류에서 아가미가 된다',["J0-29"]],
['뒷문보다 더 뒤로 길게 뻗어 나간 부속 건물','항문 뒤 꼬리(post-anal tail). 뒷문(항문)보다 뒤에 있다는 것이 이름 전부다 — 항문 앞이면 꼬리가 아니다'],
['오른쪽 작은 가게 — 들보도 관도 뒤채도 없고 앞벽의 틈만 남았다','피낭동물(멍게, 미삭동물). 성체는 넷 중 인두열(새열)만 남기고 척삭·꼬리·신경계 대부분을 잃는다',["N2-3","N2-3#1"]],
['그 가게는 부두에 딱 붙어 있고 지붕의 깔때기로 물이 쏟아져 들어간다','성체 멍게는 고착 생활을 하며 물을 걸러 먹는다(여과섭식)',["N2-3#2"]],
['작은 가게 벽에 걸린 액자 — 어릴 적엔 왼쪽 큰 가게와 똑같았다','유생 때는 네 가지를 다 갖는다. 반대로 두삭동물(창고기)은 성체가 되어도 넷을 그대로 유지한다',["N2-2","N2-2#1","N2-2#2"]]
```

**새 링크 8장** (전부 미연결 확인): `S-AN-13` `J0-29` `N2-2` `N2-2#1` `N2-2#2` `N2-3` `N2-3#1` `N2-3#2`
⚠ `N1-32`(척삭동물 4대 특징)는 **이미 `s04p05`에 패널단위로 걸려 있다.** PMAP은 카드→패널 1:1이라
p06으로 옮기려면 p05의 `pc`에서 빼야 한다 — **건드리지 말고 그대로 두는 쪽을 권한다.**

### `br`

```
척삭동물의 네 가지가 건물 하나에 다 있다 — <b>들보(척삭)</b> · <b>그 위의 속 빈 관(등쪽 신경관)</b> · <b>앞벽의 틈(인두열)</b> · <b>뒷문보다 뒤로 뻗은 뒤채(항문 뒤 꼬리)</b>. <b>위·앞·뒤라는 자리가 곧 이름이다.</b> 오른쪽 작은 가게는 어른이 되며 틈만 남기고 다 잃었다.
```

### `bx` (백틱 리터럴 — 백틱·`${` 금지)

```
<p><b>자리가 이름을 말한다.</b> 넷 중 셋은 <b>어디에 있는가</b>가 그대로 이름이다. <b>등쪽</b> 속 빈 신경관은 들보보다 <b>위</b>, <b>인두</b>열은 목이라 <b>앞</b>, <b>항문 뒤</b> 꼬리는 뒷문보다 <b>뒤</b>. 위치를 외우면 이름이 따라 나온다.</p>

<p><b>무척추동물과 정확히 반대인 자리가 둘이다.</b> 무척추동물의 신경삭은 <b>배쪽</b>이고 <b>속이 차 있다</b>(고형). 척삭동물은 <b>등쪽</b>이고 <b>속이 비어 있다</b>. 그래서 그림에서 관은 들보 <b>위</b>에 있고 양 끝이 <b>뚫려</b> 있다 — 둘 다 무척추동물과 뒤집힌 것이다.</p>

<p><b>척삭은 척추가 아니다.</b> 척삭은 속이 찬 막대 하나이고, 척추동물에서는 발생 중에 <b>척추가 그 자리를 대신</b>한다. 그래서 사람은 성체에 척삭이 없고 <b>추간판의 수핵</b>에 흔적만 남는다. 「척삭동물이면 척추가 있다」는 선지는 오답이다 — 창고기·멍게는 척추가 없다.</p>

<p><b>인두열은 처음부터 숨쉬기용이 아니었다.</b> 원래는 <b>물을 걸러 먹는</b> 여과 장치이고, 어류에 와서 <b>아가미</b>가 되었다. 기출에서는 <b>새열(鰓裂)</b>이라고도 쓴다 — 같은 것이다.</p>

<p><b>오른쪽 작은 가게가 시험에 나오는 자리다.</b> 멍게(피낭동물·미삭동물)는 <b>유생 때만</b> 넷을 다 갖고, 성체가 되면 부두에 <b>딱 붙어</b>(고착) 물을 걸러 먹으며 <b>인두열만 남긴다</b>. 벽에 걸린 액자가 그 유생 시절이다. 반대로 <b>창고기(두삭동물)</b>는 성체가 되어도 넷을 <b>그대로 유지</b>한다 — 그래서 조상 척삭동물이 창고기와 비슷했으리라 본다.</p>

<span class='q'><b>여기서 갈리는 문제.</b> <b>① 「새열만 남는 동물」을 묻는다.</b> 「척삭동물 중 유생 때는 인두·새열·근육질 꼬리에 척삭과 배신경색을 갖지만, 성체가 되며 꼬리·척삭·신경계 대부분이 없어지고 <b>새열만 갖는</b> 동물은?」 → <b>④ 멍게</b> (BM하 #1176). 오답 <b>①창고기</b>가 정확히 반대 극이다 — <b>평생 척삭을 유지</b>한다. <b>②먹장어·③칠성장어</b>는 무악류라 척삭을 성체까지 유지하고, <b>⑤뱀장어</b>는 경골어다. 액자 걸린 가게가 멍게라는 것만 붙들면 된다. <b>② 4대 특징을 나열시킨다.</b> 「척삭동물의 4가지 특징은 <b>신경다발(신경삭)·척삭·인두열·꼬리</b>이다」가 <b>옳은</b> 선지로 나온다 (BM하 #1198 ③). 넷을 셀 때 <b>「위·앞·뒤 그리고 관통하는 막대」</b>로 세면 빠뜨리지 않는다.</span>
```

### 함정 (`s04.traps`에 추가)

```
'<b>척삭은 척추가 아니다.</b> 속이 찬 막대 하나이고, 척추동물에서는 척추가 그 자리를 대신해 성체엔 추간판 수핵에만 남는다. 창고기·멍게는 척추가 없다. (캠벨 34장)',
'<b>신경관은 등쪽이고 속이 비어 있다.</b> 무척추동물의 신경삭은 배쪽이고 속이 차 있다 — 두 가지가 다 반대다. (캠벨 34장)',
'<b>항문 「뒤」 꼬리다.</b> 항문보다 뒤에 있어야 꼬리다. 항문 앞이면 꼬리가 아니다. (캠벨 34장)',
'<b>멍게는 성체에 새열만 남는다.</b> 척삭·꼬리·신경계 대부분을 잃는다. 평생 유지하는 것은 창고기다 (BM하 #1176).'
```

### 숫자 (`s04.nums`에 추가)

```
'<b>척삭동물 4대 특징</b> 척삭(관통하는 막대) · 등쪽 속 빈 신경관(위) · 인두열(앞) · 항문 뒤 꼬리(뒤)',
'<b>유지 정도</b> 두삭(창고기) = 성체도 넷 다 / 피낭(멍게) = 유생만 넷, 성체는 새열만'
```

---

## 함께 요청됐던 것 (이 패널 아님)

`s04p05`의 선구동물 **세 가게 간판**에 연체·환형·절지 **대표 동물**을 하나씩(달팽이·지렁이·게).
지금은 극피(별 다섯)만 간판이 있어 선구 쪽이 비어 있다. → **편집 작업**이라 PNG 첨부가 필요하다.
