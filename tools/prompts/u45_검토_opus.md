# s45u01 「탄소 공방」 설계 v1 검토 (Opus · 2026-10-27)

> 읽은 것: u45_설계.md 전문 · s45_dump.md(옛 8판 행) · 옛 그림 p01·p02·p03·p05 · 옛 블라인드 4판 · reservations.md 158줄 · hooks.json `_심볼예약`(128) + `hooks`·`_뜻이있는약어`·`_답면제` · manifest.json(덱 전체 소품 말) · srs_v8 카드 C0-150~245 · s20u03(2048×868 · 스코프·콩팥 확대) · s31p01·s31p03 그림 · u17_설계 앞 120줄 · 세션_절차.md 기록.
> 표기: ✗ = 시험에서 틀림/그림이 사실과 어긋남 · ⚠ = 위험 · ✓ = 맞음. `#n` = reservations.md 줄 번호.

---

## 0. 꼭 고칠 것 (중요한 순)
1. ✗ **「한 바퀴 = CO₂ 셋」** — 틀·행 2(「★ 한 바퀴에 셋씩」)·행 9(「한 바퀴 셋」)·bx(「한 바퀴의 셈 ATP 9 · NADPH 6」)·3단계 이름 틀/2/9. 캠벨: *“the cycle must take place three times, fixing three molecules of CO₂ — one per turn”*. 국내 교과서·기출도 「1회전 = CO₂ 1 · ATP 3 · NADPH 2」, 「3회전(CO₂ 3) = G3P 1 · ATP 9 · NADPH 6」. 카드도 전부 「3 CO₂당」(C0-160·164·167·168). → 모두 「CO₂ 셋(세 바퀴 = G3P 하나)」로.
2. ⚠ **화풍 참조 s20u03 오염** — 바탕 프롬프트가 「none of its objects」라 해 놓고 같은 스코프·콩팥을 그리라 해 서로 어긋난다. s20u03 에는 **파란 빛줄기(#125 청색광)**, **콩팥 위 파란 유리알(#122)**, **세로 틀선(#118 다른 날)**, **왼쪽 밤 → 오른쪽 아침 하늘**이 있다. 하늘을 베끼면 맨 왼쪽 작업장(캘빈)이 밤이 된다 = 「캘빈 회로 = 암반응 = 밤」 오개념(C0-178과 반대). → 「스코프 · 콩팥 꼴만 빌리고 나머지는 금지」로 쓰고, 햇살은 따뜻한 금빛으로.
3. ✗ **E1 「five-segment rod snapped into two three-segment pieces」** — 5 → 3 + 3 이 되어 산수가 안 맞는다(Gemini 는 2 + 3 으로 그린다). 새 문법의 핵심인 「5 + 1 = 3 + 3」은 **방울이 한 마디가 된다**는 것이 보여야 선다. 옛 p01 결함(「긴 판자와 부러진 조각이 같은 막대인가」)도 그대로다. → §5 E1 v2.
4. ✗ **행 10 「물건이 왼쪽 방에서 가운데로 … 건너간다」를 나르는 물건이 그림에 없다.** 편집 E5~E7 어디에도 문을 건너는 것이 없다. 옛 p05 블라인드 결함(「문이 한 방향도 물건이 건너간다도 그림에 없다」) 그대로다. → 마디 둘 토막(2탄소 = 포스포글리콜산/글리콜산)이 문마다 하나씩 건너가게.
5. ⚠ **첫 방 스코프가 밝은 방울을 「집기만」 한다** — 행 11 「붙였다 · O₂ 소모」와 ★15 「같은 효소 두 길」은 **같은 막대(RuBP)에 같은 동작**이어야 선다. → 첫 방 발톱이 밝은 방울을 **마디 다섯 긴 막대 끝에** 눌러 붙인다(작업장과 똑같이).
6. ⚠ **스코프 자세** — 눈에 댄 손망원경의 앞끝 집게로는 작업대 위 막대를 누를 수 없다(옛 p01 도 결국 손가락으로 눌렀다). 게다가 A 는 손에 듦 · B·C 는 삼각대 · D 는 손에 듦이라 「같은 물건」이 흐리다. → 넷 다 s20u03 꼴(**짧은 놋쇠 기둥 위 · 렌즈 둘레 두 갈래 놋쇠 발톱**). 사람이 6 → 4 로 준다.
7. ✗ **행 6 소품 글 「칸마다 하나씩」 ↔ 행 7 「맨 왼쪽 칸만 비었고」 가 서로 어긋난다.** p02 에서 이미 고친 것을 되살렸다(hooks.json 미끄럼틀 기록: 「막대도 여섯인데 다섯은 칸 안, 하나는 미끄럼틀 위」).
8. ⚠ **C₄ 막대가 문 하나로 오가고, 한 사람이 동작 셋(붙이기 · 건네기 · 동전 박기)을 한다.** 옛 p03 블라인드 「짧은 막대가 되돌아 나온 것이 아니라 둘 다 문 쪽으로 미는 것」이 그대로 재현된다. → 위 들창 = 방울 막대가 들어감 · 아래 들창 = 맨 막대가 나옴. 동전 박힌 맨 막대는 「놓인 상태」로(u17 교훈: 동작 대신 상태).
9. ⚠ **포도 자루가 난로(미토콘드리아) 바로 곁이고 C 집 쪽 마당이다.** 「포도당을 난로가 태워 굴뚝으로 CO₂」 = 세포호흡으로 읽히고(「광호흡은 당을 분해한다」 오답), 구역 C 소속으로도 잘못 묶인다. → 첫 방 앞 바닥으로 옮긴다. 포도는 낱알만(송이 · 줄기 = #92 글리코젠 / 곧은 줄기 = 녹말).
10. ⚠ **퍼옥시좀 통** — 「fizzing, bubbling water」의 흰 기포는 #17 O₂ 로 읽혀 「광호흡이 O₂ 를 낸다」가 된다(C0-195 정답 「소모」와 반대). 「물을 국자로 퍼 붓기」는 #119 「뿌리거나 퍼 넘기는 물방울 → H⁺」 · #108 과 겹친다. → 낱 기포 없는 **고운 흰 거품 더미**를 떠서 바닥 구멍에 버린다. 쇠테 없음(#102) · 통 밑 관 없음(#146).
11. ⚠ **약속표가 표제어를 흘린다** — reservations.md #114 「둥근 나무 방패 → NADPH 전용 (s33p02 오탄당 인산 경로 · s45p01 캘빈 회로)」가 2단계에서 「캘빈 회로」를 준다(b89 #93 선례). 괄호를 지운다. 새 약속 줄은 이 판 예시(「긴 막대 마디 다섯 = 5탄소」) 없이 일반형으로 쓴다.
12. ⚠ **덱의 탄소 문법과 부딪힌다** — s31p01 「★ 각뿔은 이 덱에서 3탄소의 모양」(6면 블록 → 각뿔 둘) · s31p02 「쐐기 = 2탄」 · s31p03 「작은 쐐기 + 블록 → **한 마디** 더 커진 블록」(실제로는 +2탄) · s31p01 「맨손으로 **막대를 꽂음** = 무기인산」. 「마디 수 = 탄소 수」를 약속표에 넣으면 ① s31p03 글이 틀린 셈이 되고 ② s31p01 의 맨 막대가 「탄소 하나」로 읽히며 ③ G3P · 3-PGA · 피루브산 · PEP 가 덱에서 두 꼴이 된다. → 약속 줄을 「마디 **진** 막대」로 한정하고 s31p01 · s31p03 글을 함께 고친다(text_fixes).
13. ⚠ **홀로 선 건물 꼴** — C 집 · D 탑이 붉은 벽돌이면 #93(간), 탑이 둥근 지붕에 문이 없으면 #94(뇌)다. 창에 살 · 십자가 있으면 #151, 셔터가 있으면 #120. → 회벽 · 나무 · 박공지붕 · 문 · 유리 없는 맨 창을 바탕에 명시.
14. ⚠ **콩팥** — 「옆벽」은 앞을 잘라 낸 정면 투시에서 모로 서 안 보인다 → 뒷벽 창 곁으로. 닫힌 쪽은 「limp」가 아니라 **바람 빠진 풍선처럼 쭈글쭈글**(s20u03 b99 → b100 에서 이것으로 행 13 이 섰다). 유리알 · 점 없음(#122).
15. ⚠ **마디 꼴** — 「dark rings divide into five equal segments」는 #77 눈금 자(특히 꽂이에 세운 막대 = 「곁에 세로로 선 눈금 자」)로 읽힌다. 또 고리를 세다가 4나 6으로 틀린다. → 크림 · 밤색을 번갈아 칠한 같은 길이 토막. 셀 막대(≈10개)만 PIL 로 보정.
16. ✗ **행 16 글에서 「CO₂ 친화도가 높다」(C0-204 답 · 옛 p03#0)가 빠졌다.** 행 19 「PEP 카르복실화효소가 유기산(말산)으로」는 첫 산물 OAA 를 건너뛴다(C0-226#2 답 = 옥살아세트산). → 글을 되살리고, 그림은 「흰 방울들 사이의 드문 어두운 방울을 낚아챈다」로.
17. ⚠ **이름 후크가 없다** — 유관속초세포(C0-208 · 214 · 218 답) · 엽육세포(C0-207 답)는 hooks.json 에 0건(면제도 없음)이다. 「안쪽 방 / 바깥 방」은 이름을 못 나른다. → §2-4 제안(관다발을 칼집처럼 감싼 방).
18. ⚠ **구역 폭** — B 22% = 방 하나 ≈ 150px 에 행 6개 + (4)의 건너가는 토막이 안 들어간다. D 는 위아래로 쌓이니 좁아도 된다. → A 37 · B 26 · C 19 · D 18, 넷 다 프롬프트에 숫자로 · 「one continuous scene, no frame lines」.
19. 짐꾼 · 동전 구멍 · 굴뚝의 방향과 개수 결함(옛 블라인드에서 그대로 나왔던 것): 막대 셋을 부채꼴로 벌림(겹침 = 옛 p02 개수 불확실) · 멜빵 · 어깨띠 금지(#5 Wee1) · 동전은 막대 「끝에 얹지」 말고 옆구리에 반쯤 박기(북채 · 망치 · #86 곤봉) · 동전 구멍 위에 떨어지는 짧은 선 둘(s31p01 문법 · 크랭크 없음 #148) · 굴뚝 방울 밑에 회색 연기 꼬리(s31p03 굴뚝 = CO₂ 와 같은 뜻 · 난로는 불 없음).
20. 땡볕 = 물결 아지랑이는 #136 「뚜껑도 그릇도 없이 오르는 김」 · s20u03 근적외 전구의 열선과 닮았다 → 하얗게 이글거리는 큰 해를 C 지붕 바로 위에만 + 바깥 방 사람 얼굴에 땀 두세 방울. 탑 위층 「dim blue」 → 그냥 어둡게(#125).

---

## 1. 생물학 정확성 — 행마다

| 행 | 판정 | 고칠 것 |
|---|---|---|
| 0 틀 | ✗ | 「캘빈 회로 한 바퀴(3 CO₂ → …)」 → 「CO₂ 셋(세 바퀴) → 3탄소 여섯 → G3P 하나 나감 · 다섯 재생」 |
| 1 루비스코 | ✓ | 가장 흔한 단백질 ✓(C0-158) |
| 2 탄소고정 | ✗ | 「★ 한 바퀴에 셋씩」 → 「★ 한 바퀴에 CO₂ 하나 — G3P 하나를 내보내려면 세 바퀴(CO₂ 셋 · RuBP 셋)」. 그림의 방울 셋 · 막대 셋은 그대로(= 세 바퀴 몫) |
| 3 6탄소 → 3-PGA 둘 | ✓ | C₃ 이름 ✓. 단 그림이 「5 + 1 = 3 + 3」을 실제로 보여야 한다(§0-3) |
| 4 환원 | ✓ | 3-PGA + ATP → 1,3-BPG → NADPH → G3P ✓ · NADPH 는 이 한 곳 ✓(C0-174) |
| 5 빛반응이 대는 것 | ✓ | 카드 C0-10 · 177 · 178 도 이 행이 나른다 — 잇기 |
| 6 3탄소 여섯 | ✓ / ✗글 | 사실은 맞음. 소품 글 「칸마다 하나씩」이 행 7 과 모순(§0-7) |
| 7 G3P 하나 | ✓ | 직접 산물 G3P ✓(C0-20 · 163). 나가는 막대가 「반짝 = 환원된 것」이어야 3-PGA 와 갈린다(§2) |
| 8 재생 | ✓ | 15 = 15 ✓ |
| 9 재생 ATP | ✗ | 「한 바퀴 셋」 → 「CO₂ 셋(세 바퀴)에 셋 · ★ ATP 는 두 곳(환원 6 + 재생 3 = CO₂ 셋에 9)」 |
| 10 기관 셋 | ⚠ | 「문이 한 방향」은 실제와 다르다. 광호흡(C2 회로)은 퍼옥시좀 → 엽록체로 **되돌아와** 글리세르산 + ATP → 3-PGA 로 회로에 재진입한다(탄소의 ¾ 회수). 그림의 흐름은 한 방향으로 두되, 글은 「차례로 건너간다」로 쓰고 「끝이 미토콘드리아」로 굳히지 않는다. bx 에 「남은 탄소는 엽록체로 되돌아와 ATP 를 쓰고 3-PGA 가 된다 — 첫 방 동전 자리가 그 값」 한 줄. ★ 덕분에 첫 방(엽록체)의 동전 자리가 생화학적으로도 맞다(글리세르산 인산화 · NH₃ 재고정 GS 는 둘 다 엽록체) |
| 11 O₂ 를 붙임 | ⚠ | O₂ 는 퍼옥시좀(글리콜산 산화효소 → H₂O₂)에서도 쓰인다. 「★ O₂ 는 여기서 소모」가 「여기서만」으로 읽히지 않게 「★ O₂ 는 쓰인다(소모) — 광호흡은 O₂ 를 만드는 쪽이 아니다」로. 그림에서 「소모」를 보이려면 밝은 방울이 막대에 **붙어 들어가야** 한다(§0-5) |
| 12 손해 셋 | ✓ | ATP · CO₂ · 당 ✓(C0-192 · 198) |
| 13 H₂O₂ | ✓ | 생기고(글리콜산 산화) 치우는(카탈레이스) 곳 ✓. 단 카탈레이스가 치우면 O₂ 가 나오므로 흰 기포 그림은 「광호흡이 O₂ 를 낸다」로 읽힌다(§0-10) |
| 14 CO₂ 방출 | ✓ | 미토콘드리아(글리신 탈탄산) ✓ |
| 15 한 효소 두 길 | ✓ | 카르복실화 vs 산소화 ✓ — 카드 C0-181 · 187 · 188 도 이 행 몫 |
| 16 C₄ 첫 고정 | ⚠ | 「⚠ O₂ 와 반응하지 않는다」에 「· CO₂ 친화도가 높다(낮은 CO₂ 에서도 잡는다)」를 되살림(C0-204) |
| 17 유관속초세포 | ✓ | 이름 후크 없음(§2-4) |
| 18 공간 분리 | ✓ | 피루브산 → PEP(피루브산 인산 디키네이스 · ATP → AMP)는 **엽육세포**에서 일어나므로 「바깥 방에서 되돌아온 맨 막대에 동전」의 자리가 맞다. 동전 하나로 충분(시험은 「ATP 가 더 든다」 C0-216). C0-210(「피루브산 → ATP 를 소모해 PEP 로 재생 → 엽육세포로 복귀」)은 그림 그대로이니 이 행에 잇기 |
| 19 CAM 밤 | ⚠ | 「PEP 카르복실화효소가 유기산(말산)으로」 → 「PEP 카르복실화효소가 OAA 로 고정 → 말산으로 바꿔 액포에」(C0-226#1 · #2 · #3) |
| 20 CAM 낮 | ✓ | 말산 → CO₂ → 낮에 회로 ✓(C0-228 · 229) |
| 21 공간 vs 시간 | ✓ | C0-230 도 잇기 |
| bx | ✗ | 「한 바퀴의 셈(ATP 9 · NADPH 6)」 → 「CO₂ 셋(G3P 하나)에 ATP 9 · NADPH 6 · 한 바퀴(CO₂ 하나)는 ATP 3 · NADPH 2 · 포도당 하나 = CO₂ 6 · ATP 18 · NADPH 12(C0-169~171)」 |

**소품이 그리는 것의 정확성**
- C₄ 동전 = 되돌아온 맨 3마디(피루브산)에 박음 = PEP 재생 ✓ 자리 · 뜻 모두 맞음.
- 짧은 막대 + 방울 = 3 + 1 = 4 → OAA · 말산 ✓(C₄ 의 수송형은 말산 · 아스파르트산 — 「4탄소 유기산」으로 충분). 안쪽 방에서 방울을 놓은 맨 막대 = 피루브산 3탄소 ✓.
- 방 순서 엽록체 → 퍼옥시좀 → 미토콘드리아 ✓ · CO₂ 방출 = 미토콘드리아 ✓ · 액포 = 항아리 ✓ · RuBP 5 ✓ · 3-PGA 3 ✓ · G3P 하나 배출 ✓ · ATP 9 / NADPH 6 은 「CO₂ 셋당」으로만 ✓.
- ✗ E1 산수(5 → 3 + 3). ⚠ 밝은 방울을 「집기만」 = 산소화(RuBP 에 붙임)가 안 보임.
- ⚠ 「빛을 직접 쓰지 않지만」(행 5) — 작업장에 햇살이 들면 「캘빈 회로가 빛을 쓴다」로도 읽힐 수 있다. 햇살은 **창턱의 동전 · 방패에만** 떨어지고 작업대는 그늘이게.

---

## 2. Sketchy 방법 — 행마다 짚을 소품이 있나

### 2-1 소품이 추상이거나 보이지 않거나 겹치는 행
| 행 | 문제 | 고침 |
|---|---|---|
| 10 | 「건너간다 · 한 방향」을 나르는 물건 없음 | 마디 둘 토막이 문 1→2 · 2→3 을 하나씩 건넌다(같은 두 빛깔 마디). 문짝은 달지 않는다(s46p01 · p02 「한쪽으로만 열리는 문 + 받침대」 = 판막 문법과 겹침) |
| 11 | O₂ 소모가 안 보임 | 밝은 방울이 마디 다섯 막대 끝에 붙는다(작업장과 같은 동작) · 어두운 방울은 밀려 떨어진다 |
| 16 | 「CO₂ 친화도가 높다」를 나르는 것 없음 | 바깥 방에는 흰 방울이 많고 어두운 방울은 드문데, 사람은 그 드문 어두운 방울만 낚아챈다 |
| 20 | 「물을 지킨다」가 약함 | (선택) 탑 밑동 둘레에만 갈라진 땅(#18 건조 = 닫는 신호 — 뜻이 같은 쪽이라 이득 · C0-236 「건조지 적응」) |
| 5 | 공방 안에서 만들지 않는다 | 창턱 바구니는 **창 밖 턱**에 · 햇살은 바구니에만 |
| 7 | 나가는 것이 G3P 인가 3-PGA 인가 | 동전 + 방패를 받은 토막만 반짝 = 환원 끝(G3P) → 꽂이의 막대 여섯도 같은 작은 반짝(약하게) · 부러진 맨 토막 = 3-PGA. 꽂이 막대에 톱니 끝을 달면 「갓 부러진 3-PGA」로 읽히니 달지 않는다 |
| 12 | 자루 자리 | §0-9 |

### 2-2 새 문법 「막대 마디 수 = 탄소 수」 — 좋은 생각인가
- **좋다(조건부).** 5 + 1 = 3 + 3(C₃ 이름) · 3 × 5 = 5 × 3(재생) · 3 + 1 = 4(C₄ 이름)를 **셀 수 있게** 하는 것은 이 장의 큰 이득이고, 옛 블라인드의 「긴 막대 vs 짧은 막대가 같은 물건인가」도 푼다.
- **조건 ①** 덱 충돌 정리(§0-12): 약속 줄은 「마디 **진** 막대」로 한정하고, s31p01 #2 「이 덱에서 3탄소의 모양」을 「해당과정 장에서는 각뿔」로, s31p03 #2 「한 마디 더 커진 블록」을 「두 탄소만큼 커진 블록」으로 고친다.
- **조건 ②** 그리는 꼴: 고리선 말고 **두 빛깔이 번갈아 칠해진 같은 길이 토막**으로(#77 눈금 자 회피 · 고리를 세다 4/6 이 나오는 오산 회피). 모든 막대의 마디 길이를 같게 해서 길이가 곧 개수가 되게 한다(긴 막대 = 짧은 막대의 5/3 배). 구슬 꼴은 금지(#111 주 「구슬 꿴 줄 = 아미노산」 · s38p01 「오각판과 블록이 번갈아」와도 갈리게 둥근 막대).
- **조건 ③** 방울은 막대 **끝 옆구리**에 붙인다. 끝축에 붙인 뾰족 물방울은 붓(hooks `_심볼예약` 솔 항목 「붓 = MSH」) · 성냥 머리(#142)로 읽힌다 — 옛 p03 그림의 항아리가 꼭 「붓 꽂은 항아리」다.
- **조건 ④** 셀 막대만 정확히: 스코프 아래 긴 막대 셋 · 부러진 토막 둘 · 짐꾼 막대 셋 · C₄ 들어가는 막대 하나 · CAM 항아리 앞 막대 하나 정도. 나머지(꽂이 다섯 · 더미 · 항아리 속)는 「같은 짧은 막대」로 두고 셈을 요구하지 않는다(PIL 보정이 10개 안쪽으로 준다).
- **조건 ⑤** 약속 줄 예: `마디 진 막대 — 마디 하나가 탄소 하나 · 막대에 붙은 어두운 방울도 탄소 하나로 센다`(이 판의 5 · 3 예시는 빼서 2단계 누설을 막는다 — b78 · b95 교훈).

### 2-3 ★ 행이 눈앞의 관계로 서는가
- **15 같은 스코프** — 지금은 약하다: A 는 손에 들고 · B 는 삼각대 · B 는 「집기만」. → 네 스코프를 s20u03 과 같은 꼴 하나로(바탕에서 하나를 잘 뽑아 **PIL 로 복사** — s20u03 v1 이 그렇게 했다) + A · B 가 **같은 막대에 같은 동작, 방울만 다름**. 그러면 「같은 물건 · 같은 동작 · 다른 방울 → 오른쪽은 굴뚝으로 탄소가 새고 동전이 빠진다」가 한눈에 선다.
- **18 펌프의 값과 이득** — 고리의 방향이 안 보이면 「펌프」가 안 선다(옛 p03 행 3 cold P). 들창 둘 + 동전 박힌 맨 막대(상태) + C 위에만 있는 해.
- **21 공간 vs 시간** — C 와 D 가 붙어 있고 같은 「짧은 막대 + 방울」 동작이 두 곳에 있어 선다. 다만 탑의 두 층이 「위아래로 가른 두 방(= 공간)」으로 읽힐 위험이 있다 → **같은 사람(같은 옷) · 같은 무늬 항아리**를 위아래에 두고 층 사이에 사다리(한 집 · 두 때). C 의 바깥 방 사람과 D 위층 사람을 **같은 옷**으로 하면 「둘 다 PEP 카르복실화효소」(★21 후반)도 그림이 된다.
- **14 「들어오면 고정 · 나가면 광호흡」** — 한 장에 들어와서 처음으로 셀 수 있게 되었다 ✓(굴뚝 방울에 방향 꼬리만 달면).

### 2-4 이름 후크 (새로 필요)
- **유관속초세포** = 維管束鞘 = 관다발을 감싼 칼집. 안쪽 방을 「**가는 관 다발(s45p08 의 관다발과 같은 물건)을 가운데 두고 두꺼운 벽이 칼집처럼 감싼 작은 방**」으로 하고 바깥 방이 그것을 둘러싸게(크란츠 화환 꼴 = 실제 배치). ⚠ 관은 곧고 뻣뻣하게 · 붉은 웅덩이 금지(#43 말피기관 「말총처럼 흘러내린 관 다발 + 붉은 웅덩이」).
- **엽육세포** = 잎살. 바깥 방 벽을 잎살 무늬(초록 · 잎맥)로(s20u03 잎 단면 벽과 같은 결).
- 둘 사이 들창 = s14p04 의 「두꺼운 벽을 뚫은 짧은 통로 — 통로 속까지 같은 벽지」(원형질연락사)와 같은 꼴로 하면 덱 문법이 맞고 C0-209(원형질연락사)까지 이 행이 나른다.

---

## 3. 예약 충돌 (규칙 173) — 소품 말마다

| 소품 | 부딪히는 것 | 위험 | 바꿀 것 |
|---|---|---|---|
| 루비 렌즈 스코프 | #34 ✓(쓰는 예약) | — | s20u03 꼴 그대로: 짧은 놋쇠 기둥 · 두 갈래 놋쇠 발톱(「iron pincer claw」 · 「tripod」 말고) |
| 집게/발톱 | #23 놋쇠 못 개수(스코프에 리벳이 세어지면) | 낮 | 리벳 · 나사 없음 |
| 어두운 방울 | #16 ✓ · #4 자갈 · #124 평형석(둥글게 그려지면) | 중 | 늘 물방울꼴. E5 의 「rolls」는 공을 부른다(옛 p05 가 그렇게 그렸다) → 「slides/falls」 |
| 밝은 방울 | #17 ✓ | 낮 | 「glowing」을 지운다(빛 · 에너지로 읽힘) · s20u03 의 흰 둥근 기포 |
| 동전 | #8 ✓ · #101 네모 칩 · #86 곤봉(막대 끝에 얹은 원반 = 북채 · 망치 — 옛 p02 블라인드) | 중 | 테 있는 납작 금화 · 막대 옆구리에 반쯤 박기 |
| 동전 바구니 | #136 반쯤 젖힌 바구니(가둬 둠) · #140 매단 바구니 | 낮 | 뚜껑 없는 얕은 바구니 · 놓인 것 |
| 방패 | #114 ✓ — 그러나 그 줄의 괄호가 표제어를 흘림 | 중 | 줄 114 괄호 삭제 · 창턱 「방패 더미」는 접시 · 바퀴 더미로 읽히니 벽에 기대 세운 둘(배꼽 박힌 둥근 방패) |
| 꽂이 · 빈 칸 | #22 모듈 쟁반(피함 ✓) · #7 「V 자리가 빈 꽂이(움푹한 홈) = 오지 않은 날」 | 낮 | 세운 슬리브 꽂이 · 빈 칸은 미끄럼틀이 붙은 칸 하나뿐 |
| 마디 막대 | #77 눈금 자 · #142 성냥 머리 · 붓(hooks 솔 항목) · #12 지팡이(세워 들면) · s31p01 맨 막대 = 무기인산 · s31p01 각뿔 = 3탄소 | 중~높 | §2-2 |
| 미끄럼틀 | 덱에 다른 뜻 없음(s33p02 활송 · #157 활송로는 꼴이 다름) | 낮 | 놀이터 미끄럼틀 꼴 ✓ |
| 뒷벽 구멍 | #116 「담장에 다른 구멍 = 짝풀림제」 · #134 뒷문 = 기저외측막 | 낮 | 문틀 없는 작고 둥근 구멍 · 뒤에 물 없음 |
| 짐꾼 | #5 어깨띠(멜빵 · 지게끈) · #111 사람이 멘 자루 개수 · #79 두꺼운 굽 | 중 | 띠 · 끈 없이 손으로 어깨에 · 납작 신발 |
| 걸상 | s45p06 무지개 걸상(같은 단원 u02) | 낮 | 작은 등받이 없는 의자 또는 빼고 방울이 바닥으로 떨어짐 |
| 동전 구멍 | #147 · #148 동전 투입구 펌프(Na⁺-K⁺) | 중 | 벽의 맨 틈 · 기계 · 크랭크 · 손잡이 없음 · 떨어지는 선 둘 |
| 나무 물통 | #102 금속 양동이(쇠테) · #98 드럼통 · #146 맨 구멍 물줄기(옛 p05 의 통 밑 배수관) | 중 | 나무 테 · 통 밑 관 없음 |
| 거품 | #17 흰 둥근 기포 = O₂ | 높 | 낱 기포 없는 고운 거품 더미 |
| 국자로 퍼 붓기 | #119 퍼 넘기는 물방울 = H⁺ · #108 퍼 넘기는 팔 | 높 | 물이 아니라 거품 덩이를 떠 버림 · 물방울 · 물줄기 없음 |
| 바닥 구멍 | #146 · #116 | 낮 | 그대로 |
| 주름 무쇠 난로 | s28p02 「난로 = 화학 에너지」 · s19p02d 「주름 통 = 미토콘드리아」 | 낮 | 불 · 열 없음(「미토콘드리아가 에너지를 낸다 → 광호흡이 ATP 를 만든다」 오독 차단) |
| 굴뚝 | s31p03 굴뚝 = CO₂ 방출(같은 뜻 ✓) · #121 연보라 구름 = 에틸렌 · #133 둥근 관 = 핏줄 | 낮 | 회색 연기 꼬리 + 어두운 방울 하나 |
| 포도 자루 | #111 ✓(땅에) · #92 가지 포도 = 글리코젠 / 곧은 줄기 포도 = 녹말 · #90 「포도알」 낱말 금지 | 중 | 낱알 · 송이 · 줄기 없음 · 자리 옮김 |
| 두 방 집 | #134 뒷문 · s46p01 · p02 일방 문짝 = 판막 · s14p04 통로 = 원형질연락사(같은 뜻으로 쓰면 이득) | 낮 | 문짝 없는 들창 둘 · 뒷문 없음 |
| 해 · 땡볕 · 아지랑이 | #136 오르는 김 · #127 열만 내는 까만 전구(s20u03 열선) · #118 「해 뜬 맑은 날 = 정상」 | 중 | 하얗게 이글 + 땀 · 해는 C 위에만 · 물결선 금지 |
| 탑 | #94 돔 지붕 · 문 없음 = 뇌 · #93 붉은 벽돌 홀로 선 건물 = 간 | 높 | 회벽 · 박공 · 문 · 사다리 |
| 초승달 · 둥근 해 | #80 ✓ | — | 보름달 금지 ✓ |
| 밤 층 「dim blue」 | #125 파란 빛 = 청색광(= 기공 여는 신호 → CAM 밤 열림 까닭을 잘못 댐) | 중 | 그냥 어둡게 · 창 밖만 검은 밤하늘 |
| 콩팥 | #14 ✓ · #122 파란 유리알(s20u03 그대로 베낌) | 높 | 맨 초록 · 유리알 · 점 없음 · 닫힘은 쭈글 |
| 질그릇 항아리 | #153 항아리 물높이 = 관 끝에서 나오는 양 · #102 주(물 그릇) | 낮 | 「dry, no water」 |
| 맨 막대 더미 | #12 지팡이 · 장작 | 낮 | 3마디 짧은 막대 그대로 |
| 창 · 창턱 · 햇살 | #151 격자창 개수 · #120 롤 셔터 · #125 파란 유리창 · 빛줄기 · #88 창턱에 놓인 배턴 | 중~높 | 유리 · 살 없는 맨 창 · 금빛 햇살 · 창턱에 막대 금지 |
| 셔츠 | #39 단추 한 줄 넷 = CD4 · #5 띠 · #1 모자 | 중 | 깃 없는 풀오버 · 단추 · 벨트 없음(옛 p01 은 벨트를 맸다) |
| C₄ 식물 예시 | #13 옥수수 알갱이 = 옥신 | 높 | 옥수수는 그리지 마라(예시는 bx · 그리려면 사탕수수만) |
| 틀선 | #118 = 다른 날 · s20u03 오른쪽 끝에 실제 틀선이 있다 | 높 | 「no frame lines or panel dividers」 |

---

## 4. 블라인드 오독 위험

1. **방 셋 ↔ 두 방 집** — B · C 가 같은 「작은 방들」이라 1단계에서 「방 다섯」 · 「C 가 넷째 기관」으로 묶일 수 있다. → C 는 마당 건너 따로 선 집 + **방 속의 방**(크란츠 꼴)으로 B 의 「한 줄로 늘어선 방」과 꼴부터 다르게.
2. **A + B 한 구역으로 묶임** — 같은 건물이라 1단계 구역 수가 3이 될 수 있다 → 작업장과 방 셋 사이는 문 하나 뚫린 통벽 · 크기 대비(큰 홀 vs 좁은 방 셋). (선택) 첫 방 벽을 작업장과 같은 연초록으로 하면 「첫 방 = 엽록체」(옛 p05 결함 「초록이 하나도 없다」)가 서고, 캘빈 회로도 같은 엽록체라는 것이 맞아진다.
3. **스코프가 넷** — 꼴이 다르면 「효소 넷」으로 읽힌다 → 한 꼴 PIL 복사. 그러면 「어디서나 루비스코 · 바깥 방(엽육)에만 없다」가 오히려 사실을 나른다(C0-208).
4. **짐꾼 방향 · 고리** — 오른쪽으로 걷거나 정면을 보면 고리가 끊긴다 → 「faces left, back to the stand, striding toward the scope」. 짐꾼 막대 셋 + 스코프 곁 막대 셋 = 여섯을 「분자 여섯」으로 셀 위험 → 짐꾼 막대에만 동전(= 재생된 것)으로 갈린다.
5. **들창 · 구멍** — G3P 출구가 「문」이면 #134(뒷문 = 기저외측막), C₄ 문 하나면 방향 불명(옛 p03). → 작은 둥근 구멍 / 위 · 아래 들창.
6. **동전 개수** — 그림의 동전은 1(환원) · 3(재생) · 1(헛돈) · 1(C₄) + 바구니다. 「환원에 ATP 1개」로 셀 수 있다. 셈을 바라면 창턱을 「동전 여섯 · 방패 여섯 한 줄」로(환원 6 + 재생 3 = 9 · NADPH 6 — C0-167 · 168 을 그림이 나름). 아니면 창턱은 셀 수 없는 더미로(셀 수 있는 둘 · 셋은 다른 뜻으로 읽힌다).
7. **밤낮 탑과 #118** — 탑 층은 틀선 칸이 아니니 #118 은 걸리지 않는다. 진짜 위험은 ① 화풍 참조에서 베껴 온 틀선 ② 옛 p03 처럼 상자 꼴 테두리로 그려져 「칸」이 되는 것 → 지붕 · 문 · 사다리가 있는 건물로. 「다른 조건」으로 읽혀도 밤/낮이라 해롭지 않다.
8. **포도 자루** — 「출력(당이 만들어짐)」 vs 「손실」: 홀쭉 · 옆구리 구멍 · 굴러 나간 포도 · 난로와 떨어진 자리(§0-9).
9. **땡볕 위치** — 하늘의 해가 탑 위층(밤) 곁에 오면 모순으로 읽힌다 → C 지붕 바로 위 낮게.
10. **CAM = 공간 분리로 읽힘** — §2-3 의 같은 사람 · 같은 항아리 · 사다리.
11. **3단계 이름 누설 점검** — 소품 말은 없다 ✓. 다만 18 「C₄ — 공간 분리의 대가와 이득」과 21 「C₄ 공간 vs CAM 시간」이 「공간」으로 겹쳐 같은 물건에 이어질 수 있다 → 18 을 「C₄ — 펌프의 값(ATP)과 덕(고온 · 강광)」으로. 2 · 9 · 틀의 「한 바퀴」는 §1 대로 고친다.
12. **약속표 누설** — #114 괄호(§0-11). 새 줄은 일반형으로.

---

## 5. 구도 · Gemini 실현성

### 5-1 폭과 사람
- 40/22/19/19 → **A 37 · B 26 · C 19 · D 18**. B 는 방 셋에 벽 넷이라 실폭이 가장 좁고 행이 가장 빽빽하다(행당 폭 A 4.4% · B 3.7% · C 6.3% · D 9.5%).
- 사람 6 → **4**(A 환원 장인 · 짐꾼 / C 바깥 방 / D 위층). A 스코프 사람과 D 아래층 스코프 사람을 빼고 스코프는 기둥에 세운다. B 의 「떠도는 손」은 빼고 국자는 「통 테에 걸쳐 기울어 거품을 떨구는」 상태로(u17 b83 교훈: 손이 물건 곁에 있으면 「건넨다」로 읽힘).
- 바탕은 큰 덩어리 · 자리 · 사람 · 스코프 넷 · 밤낮 · 콩팥 상태 · 해 · 꽂이 · 통 · 난로 · 항아리까지만 둔다. 막대 마디 · 방울 · 동전 · 토막 · 들창 · 자루는 편집으로.

### 5-2 잘못 그려질 것
| 소품 | 위험 | 대책 |
|---|---|---|
| 손망원경 + 앞끝 집게로 막대 누르기 | 자세가 불가능해 손가락으로 누름(옛 p01) | 기둥 스코프 |
| 마디 막대 | 개수 흔들림 · 대나무 · 자 | 두 빛깔 토막 + PIL |
| 주름 난로 | 옛 p05 에서 잘 나옴 | 불 없음만 명시 |
| 아지랑이 | 김 · 연기로 | 쓰지 않음 |
| 옆벽 콩팥 | 모로 서서 안 보임 | 뒷벽 |
| 「rolls」 방울 | 공 | 물방울꼴 · 미끄러짐 |
| 한 사람 세 동작(C) | 하나만 그림 | 동작 하나 + 상태 둘 |
| 짐꾼 막대 셋 | 겹침 | 부채꼴 |
| 국자 방향 | 통 안으로 붓기(옛 p05) | 상태 묘사 |
| 하늘 · 빛 | s20u03 의 밤 → 아침 · 파란 빛줄기를 베낌 | 명시 금지 |

### 5-3 바탕 프롬프트 v2 (제안 — 한 줄로 이어 쓴다)
`Copy only the drawing style of the attached picture — clean ink linework with soft watercolor washes, cream paper, a thin black border with a beige margin, muted colors. Reuse exactly two object designs from it and nothing else: (a) its brass spyglass with a ruby-red front lens standing on a short brass post, with two thin curved brass prongs around the lens; (b) its pair of green kidney-shaped cells, but plain green with no blue beads or dots. Do NOT copy its greenhouse, glass roof, clock, hourglass, light bulbs, blue light beams, its vertical frame line, or its night-to-morning sky. Draw ONE continuous wide panorama, about 2.4 times as wide as it is tall, seen straight from the front at eye level under an ordinary pale daytime sky, with no frame lines or panel dividers anywhere: a row of small buildings of whitewashed plaster and plain timber (no brick, no domes), their front walls cut away like doll's houses. No text, letters or numbers anywhere. People wear plain collarless pullover shirts and trousers — no hats, buttons, vests, belts, sashes or straps. From left to right: (1) The left 37%: one big plank-floored workshop hall with pale green walls and a long wooden workbench. At the bench's left end the ruby-lens scope stands on its short brass post, angled down at the bench top. In the middle of the bench a craftsman stands beside a round wooden shield with a central boss. In the back wall above him, a plain open window with no glass, bars or shutters lets a warm golden-yellow sunbeam fall onto its sill only. At the bench's right end stands a tall wooden stand with six upright wooden sleeves in a row. In front of the bench a porter faces left and strides toward the scope, three long rods fanned apart on his shoulder. (2) The next 26%, in the same building behind a solid wall with one doorway: three narrow rooms in a row joined by plain rectangular doorways without doors. The first room has the same pale green walls and the same ruby-lens scope on the same short post above a low bench. The second holds a wooden tub bound with wooden hoops, heaped with fine white foam like soap suds. The third holds a squat unlit cast-iron stove whose body is folded into many deep pleats like an accordion, its chimney rising through the roof. (3) The next 19%, after a strip of bare yard: a separate small one-storey house with a huge white-hot sun blazing low in the sky directly above it. Inside, a small thick-walled inner chamber stands in the middle around a bundle of thin straight vertical pipes, and a leafy-green outer room wraps around it; a sweating worker stands in the outer room. The inner chamber is crowded with floating dark-grey teardrop-shaped drops and holds the same ruby-lens scope on its short post. (4) The last 18%: a separate narrow two-storey tower with a pitched roof, a ground-floor door and a ladder between the floors. Upper floor at night: a dark room whose back-wall window shows a black sky with a thin crescent moon and stars. Lower floor in daytime: a bright room whose back-wall window shows a round yellow sun. On the back wall of each floor, beside its window, the pair of green kidney-shaped cells face each other: upstairs plump and bowed apart with an open gap between them; downstairs shrunken and wrinkled like deflated balloons, pressed shut. Each floor has the same big round dry clay jar.`
- 실패 시 다시 뽑을 것(편집으로 못 고침): 하늘이 밤 · 새벽 · 파란 빛줄기 · 틀선 · 붉은 벽돌 · 둥근 지붕 · 구역 차례 · 폭 · 탑의 위아래 밤낮.

### 5-4 편집 고침 (v1 → v2 · 각 끝에 「Add nothing else.」)
- **E1** `Under the scope, its prongs press one dark-grey teardrop drop against the side of the tip of a long rod made of five equal segments painted alternately cream and tan. Just right of it, two short rods of three such segments each lie end to end with matching jagged zigzag broken ends, as if a long rod had just snapped in two; the end segment of the right-hand piece is dark grey like the drops. Exactly three dark drops by the scope (the pressed one plus two floating) and exactly three long five-segment rods (that one plus two waiting, well apart).` → 5 + 1 = 3 + 3 이 셈으로 서고, 어두운 끝 마디가 「방금 붙은 탄소가 한쪽 3-PGA 에 들어갔다」(사실 그대로)를 보이며 「같은 막대」 연결도 된다.
- **E2** 동전은 `a flat gold coin with a raised rim pressed half into the side of one short piece` · 방패는 그 토막에 대고 세움 · `on the outside sill only: an open shallow basket of gold coins and two round shields leaning against the wall` · 창턱에 막대 금지.
- **E3** `five sleeves each hold one short three-segment rod upright, each with a tiny sparkle; the leftmost sleeve is empty and from it a little playground slide carries the sixth rod down and out through a small round hole low in the back wall (no door, no frame)`.
- **E4** `one flat rimmed gold coin pressed half into the side of each of the three long rods near its front end; the three rods fan apart from his hand so all three are clearly separate; no straps on him`.
- **E5** `The scope's prongs press one plain white round bubble against the tip of a long five-segment rod lying on the low bench, exactly as in the hall; a dark-grey teardrop drop is pushed off the bench and falling. A two-segment stub (same cream-and-tan segments) is passing through the doorway into the next room. In the wall, one flat gold coin is half sunk into a bare slot with two short falling lines above it; no machine, no crank. On the ground in front of this room, a slumped, nearly empty burlap sack with a torn hole in its side, loose single purple grapes (no stems, no bunches) rolled out on the ground.`
- **E6** `A wooden ladle rests tipped on the tub's rim over a small round drain hole in the floor, a clump of white foam sliding from it into the hole; a two-segment stub passes through the doorway toward the stove room. No water drops, no water stream, no pipe.`
- **E7** `From the top of the chimney one dark-grey teardrop drop pops out above the roof, a short wisp of grey smoke trailing below it; the two-segment stub goes in at the stove's door.` (자루는 E5 로 옮김)
- **E8** `Two small hatches in the inner chamber's wall, one high and one low. The worker snatches one dark drop from among many white bubbles in his room and pushes a short three-segment rod, the dark drop stuck to the side of its tip, into the high hatch. From the low hatch a bare short three-segment rod has just slid out onto the floor; beside it lies another bare short rod with a flat gold coin pressed half into it. Inside the chamber the scope's prongs press a dark drop against the tip of a long five-segment rod.`
- **E9** `Dark-grey teardrop drops drift in through the open gap between the plump cells; a worker in the same shirt colour as the worker in the small house sticks each onto the side of the tip of a short three-segment rod and stands the rods in the clay jar; a small pile of bare short rods beside him.`
- **E10** `The same clay jar lies tipped over; dark drops spill out freed from the rods, bare rods lying in its mouth; the ruby scope on its short post grips one freed drop against the tip of a long five-segment rod.`
- 차례: 바탕 → 스코프 하나를 고른 뒤 PIL 복사 → E1 … E10 → 마디 PIL(셀 막대만).
- 행 대조(규칙 170)에 더할 것: ⑩ 5 + 1 = 3 + 3(어두운 끝 마디) ⑪ 첫 방 막대 + 밝은 방울 ⑫ 마디 둘 토막이 문마다 ⑬ 거품 더미(낱 기포 · 물방울 없음) ⑭ 들창 위 · 아래 ⑮ 파랑 없음(빛줄기 · 방 · 유리알) ⑯ 콩팥 닫힘이 쭈글 ⑰ 띠 · 단추 · 벨트 · 멜빵 없음 ⑱ 창에 살 · 유리 없음 ⑲ 자루가 난로와 떨어짐 · 포도 송이 없음 ⑳ 건물에 벽돌 · 돔 없음.

---

## 6. 빠진 것 — 옛 판 · 카드와 대조

- **옛 판에 있었는데 새 글에서 빠짐**: p03#0 「CO₂ 친화도가 높다」(C0-204) — 꼭 되살림. p03#2 「45-5 의 헛돈과 달리 여기 동전은 제값을 한다」 — 한 장에 모였으니 ★ 한 마디로 살릴 만함(행 18). p03#4 「덥고 마를 때」의 「마름」 — (선택) 갈라진 땅.
- **그림에 이미 있는데 안 이은 카드**: C0-153(캘빈 3단계 → 틀) · C0-10 · 177 · 178(행 5) · C0-181 · 187 · 188(행 15/11) · C0-210(행 18) · C0-230(행 21) · (들창을 원형질연락사 꼴로 하면) C0-209.
- **시험 단골인데 그림이 없음**: CO₂ 셋당 ATP 9 · NADPH 6(C0-167 · 168), 포도당 하나에 CO₂ 6 · ATP 18 · NADPH 12(C0-169~171) → §4-6 의 창턱 「동전 여섯 · 방패 여섯」 안을 쓰거나 bx 로. 예시 식물(C0-186 · 202 · 222) → bx(옥수수는 그리지 마라 #13 · 그리려면 C 마당의 사탕수수 · D 창턱의 선인장. 파인애플은 #69 「유일한 과일」 문구와 부딪힘).
- **hooks · 글 잔손질**: `_심볼예약` 루비빛 스코프(s45p01 · p03 · p05) · 초승달(s45p03) · 방패(s45p01) · hooks CAM(「s45p03 오른쪽 위 칸」) · 퍼옥시좀(「s45p05 가운데 방」) · `_뜻이있는약어` · `_답면제` C4(「s45p03 이 바깥 방에서…」) → s45u01. `_심볼예약` 어두운 방울 「들어가는 쪽」 · 밝은 방울 「나오는 쪽」은 이 장에서 뒤집혀 쓰이므로(굴뚝으로 나가는 CO₂ · 붙어 들어가는 O₂) 방향 말을 지운다.

---

## 7. 글 고침 목록 (그대로 바꿔 넣을 말)
- 틀 사실: 「캘빈 회로 한 바퀴(3 CO₂ → …)」 → 「캘빈 회로 세 바퀴분(CO₂ 셋 → 3탄소 여섯 → G3P 하나 나감 · 다섯 재생)」.
- 행 2 사실 끝: 「★ 한 바퀴에 셋씩」 → 「★ 한 바퀴에 CO₂ 하나 — G3P 하나를 내보내려면 세 바퀴(방울 셋 · 막대 셋)」.
- 행 3 소품: 「방울을 받은 막대가 … 마디 셋인 토막 둘」 → 「곁에 방금 부러진 마디 셋 토막 둘 — 톱니가 맞물리고 오른 토막 끝 마디만 방울빛(5 + 1 = 3 + 3)」.
- 행 6 소품: 「칸마다 하나씩」 → 「짧은 막대도 여섯 — 다섯은 칸에, 하나는 빈 칸에서 뻗은 미끄럼틀 위」.
- 행 9 사실: 「한 바퀴 셋」 → 「CO₂ 셋(세 바퀴)에 셋 · ★ ATP 는 두 곳(환원 6 + 재생 3 = 9)」 · 소품 「끝마다」 → 「앞끝 옆구리마다」.
- 행 10 사실: 「문이 한 방향」 → 「물건이 차례로 건너간다(마디 둘 토막 = 엽록체를 떠나는 2탄소)」 · bx 「남은 탄소는 엽록체로 돌아와 ATP 를 쓰고 3-PGA 로 회로에 재진입」.
- 행 11 사실: 「★ O₂ 는 여기서 소모」 → 「★ O₂ 는 쓰인다(소모) — 광호흡은 O₂ 를 만드는 쪽이 아니다」 · 소품: 「밝은 방울을 마디 다섯 막대 끝에 눌러 붙였고」.
- 행 16 사실: 「⚠ O₂ 와 반응하지 않는다」 → 「⚠ O₂ 와 반응하지 않고 CO₂ 친화도가 높다」 · 소품: 「흰 방울 사이의 드문 어두운 방울만 낚아채」.
- 행 18 소품: 「문으로 되돌아 나오고」 → 「아래 들창으로 미끄러져 나왔고 곁의 맨 막대엔 금화가 박혔다」 · 「이글거리는 땡볕」 → 「지붕 바로 위 하얗게 이글거리는 큰 해 · 땀 흘리는 사람」.
- 행 19 사실: 「유기산(말산)으로 만들어」 → 「OAA 로 고정해 말산으로 바꿔」.
- 3단계 이름: 틀 「캘빈 회로(CO₂ 셋 = 세 바퀴)와 광호흡 · 그것을 피하는 두 길」 · 2 「탄소고정 — RuBP 가 CO₂ 를 받는다(한 바퀴에 하나)」 · 9 「재생에도 ATP — CO₂ 셋에 셋」 · 18 「C₄ — 펌프의 값(ATP)과 덕(고온 · 강광)」.
- bx: §1 bx 줄 그대로.
- 약속표: #114 괄호 삭제 · 새 줄 `마디 진 막대 — 마디 하나가 탄소 하나 · 막대에 붙은 어두운 방울도 탄소 하나로 센다`.
- text_fixes(다른 판): s31p01 #2 「★ 각뿔은 이 덱에서 3탄소의 모양」 → 「해당과정 장에서 3탄소는 각뿔(광합성 장은 마디 셋 막대)」 · s31p03 #2 「한 마디 더 커진 블록」 → 「두 탄소만큼 커진 블록」.
