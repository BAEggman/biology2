#!/bin/sh
# L43g_build.sh <workdir> — L43g 「담장 밖 두루마리 마당의 문어 소동」 그림을 처음부터 다시 만든다(같은 픽셀).
#  S1(Gemini 카본 높음 · 출연진 = L43f 담 밖 + L13b 망토 · 깍둑썰기 기계 · 문어 + L48e 분쇄 통 · 두 탭에서 동시에 → S1a 씀)
#  → 그림 통째 고침 E1(새 채팅에 S1a 를 올림 · 두 탭): 긴 꼬리 여백 · 갉힌 짧은 두루마리 · 머리 여백에 앉은 씨름꾼(뒤에 ZK 로 판다) · 맞는 토막 · 접은 전구체 → E1b = 바탕(1024 → 2048)
#  → 구역 편집: ZD2(깍둑썰기 기계에서 쏟아지는 짧은 토막과 바닥 더미 — 첫 ZD 는 오림이 낮아 더미가 잘려 버림) · ZS(사슬 가운데 고리를 잘라 내자 빛남)
#    · ZH2(벽 못에 매달린 구슬 사슬만 지움 — 상자를 그 자리로) · ZP(우는 일꾼의 종이: 글씨 같은 자국 → 빛깔 네모 · 갉힌 꼬리)
#    · ZO(찢기는 두루마리를 빛깔 네모 종이로 · 치켜든 토막 초록 · 빨강 · 노랑 · 파랑 / 오른쪽 문어는 토막을 덮어 누름)
#  → L43g_pil.py(찢긴 조각의 네모 차례를 토막과 같게 · 문어 머리의 「S3」 같은 자국 지움 · 웃는 일꾼 뺨의 눈물 지움) → ZQ(잘린 토막 더미를 둥글게 · 낱장 종이 지움)
#  일치 검사 1회 뒤: ZM(기계 둘레 통째 — 망토가 끈으로 묶은 두루마리 둘을 윗구멍에 밀어 넣으며 눈이 휘둥그레 · 기계 뒤 문어가 토막을 치켜들고 다른 다리로 두루마리를 찢음
#    · 오른쪽 일꾼은 반으로 접은 긴 종이를 먹이고 접힌 U 자 고리가 손 아래로 늘어짐 — 같은 채팅 둘째 고침 ZM2a 를 씀)
#    → ZW(씨름꾼(→ 판다) 머리 뒤로 삐져나온 두루마리 지움 · 망토 자락의 얼룩 정리) → ZF(일꾼 다리 이음매 · 무릎 사이 남은 종이 조각 지움)
#    → 일치 검사 2회 뒤: ZT(탁자 밑 「호스 같은 줄」 지움 · 아래 가운데 문어 머리 매끈하게 — 두 탭 가운데 ZTa)
#    → L43g_pil2.py(씨름꾼이 깔고 앉은 두루마리의 일꾼 쪽에 빛깔 네모 넷 — 씨름꾼은 네모 앞 흰 여백에 앉음 · 왼쪽 두루마리 앞머리의 회색 줄 자국 지움)
#    → 일치 검사 3회 뒤: ZR(아래 오른쪽 문어 — 껍데기만 보이고 몸이 두루마리에 묻혔다 → 머리 · 눈 · 껍데기를 드러내고 한 다리로 토막을 치켜듦)
#      · ZG(맨 왼쪽 두루마리 끝 쪽의 흐린 네모 셋 → 또렷한 빛깔 · 「갉힘」과 헷갈림)
#    → L43g_pil3.py(아래 오른쪽 문어가 치켜든 토막의 끝 두 칸을 바꿔 두루마리 네모와 앞 두 칸만 맞게 = 불완전 일치)
#    → 일치 검사 4회 뒤: ZI(깍둑썰기 기계에 들어가는 종이 — 접은 종이 두 겹 · 망토의 두 두루마리 — 에도 빛깔 네모 줄 · 「들어가는 종이엔 네모가 없는데 나오는 토막엔 있다」)
#      · ZB2(왼쪽 두루마리 꼬리의 벌레 떼 — 날개 달린 개미처럼 읽힘 → 날개 없는 은빛 좀벌레 · 종이 모서리의 「S」 같은 낙서 지움)
#      · ZC(우는 일꾼 종이 밑 — ZP 상자 아래 남은 초록 테 조각들(「Q」 같은 꼴) · 흰 부스러기 지움 · 찢긴 끝을 하나로 · 같은 채팅 셋째 고침 ZC3a)
#    → L43g_pil4.py(왼쪽 두루마리 네모 스물셋을 이 세계의 네 빛으로 · 손에 든 앞머리 종이를 흰빛 쪽으로 · 찢기는 종이 뭉치의 네모 셋)
#    → 예약 대조 뒤: ZK(두루마리 머리 여백에 앉은 붉은 샅바 씨름꾼 → 팔짱 끼고 대나무를 문 판다 — 【샅바를 맨 장사】 = APC/C(L19c) 전용 ·
#      「다른 판에 씨름 장사나 샅바를 놓지 마라」 · 일치 검사로는 안 잡히고 hooks.json 예약을 맞춰 보다 찾음 · 두 탭 가운데 ZKb)
set -e
W=${1:-/tmp/L43g_build}; D=$(cd "$(dirname "$0")" && pwd); S="$D/L43g_src"
mkdir -p "$W/z"
Z="python3 $D/zone3.py"; CM="python3 $D/colormatch.py"
python3 - "$S" "$W" <<'PY'
import sys
from PIL import Image
S, W = sys.argv[1:3]
Image.open(f'{S}/E1b.webp').convert('RGB').resize((2048, 1144), Image.LANCZOS).save(f'{W}/base0.png')
for n in ('ZD21', 'ZS1', 'ZH21', 'ZP1', 'ZO1', 'ZQ1', 'ZM1', 'ZW1', 'ZF1', 'ZT1', 'ZR1', 'ZG1', 'ZI1', 'ZB21', 'ZC1', 'ZK1'):
    Image.open(f'{S}/{n}.webp').convert('RGB').save(f'{W}/z/gem_{n}.png')
PY
cd "$W"
cm() { $CM z/up_$1.png z/gem_$2.png z/cm_$2.png; }
$Z crop base0.png z ZD2 880 430 1520 790;   cm ZD2 ZD21
$Z paste base0.png z ZD2 z/cm_ZD21.png b1.png "1140,560,1400,790"                                     # 깍둑썰기 기계에서 쏟아지는 짧은 토막 · 바닥 더미
$Z crop base0.png z ZS 1520 380 2048 677;   cm ZS ZS1
$Z paste b1.png z ZS z/cm_ZS1.png b2.png "1650,460,2048,672"                                          # 사슬 가운데 고리를 가위로 · 빛나는 나머지 사슬
$Z crop base0.png z ZH2 60 460 660 798;     cm ZH2 ZH21
$Z paste b2.png z ZH2 z/cm_ZH21.png b3.png "196,500,318,798"                                          # 벽 못에 매달린 구슬 사슬 지움
$Z crop b3.png z ZP 250 660 498 800;        cm ZP ZP1
$Z paste b3.png z ZP z/cm_ZP1.png b4.png "284,682,402,800"                                            # 우는 일꾼의 종이 — 빛깔 네모 · 갉힌 꼬리
$Z crop b3.png z ZO 940 784 1580 1144;      cm ZO ZO1
$Z paste b4.png z ZO z/cm_ZO1.png b5.png "950,800,1580,1144"                                          # 찢는 문어(맞는 토막) · 덮어 누르는 문어
python3 $D/L43g_pil.py b5.png p1.png                                                                  # 찢긴 조각의 네모 차례 · 머리 자국 · 뺨의 눈물
$Z crop p1.png z ZQ 1060 690 1460 915;      cm ZQ ZQ1
$Z paste p1.png z ZQ z/cm_ZQ1.png p2.png "1150,722,1390,850"                                          # 잘린 토막 더미를 둥글게
$Z crop p2.png z ZM 700 190 1620 708;       cm ZM ZM1
$Z paste p2.png z ZM z/cm_ZM1.png p3.png "830,195,1540,706"                                           # 망토의 묶은 두 두루마리 · 찢는 문어 · 접은 종이를 먹이는 일꾼
$Z crop p3.png z ZW 760 440 1080 620;       cm ZW ZW1
$Z paste p3.png z ZW z/cm_ZW1.png p4.png "830,450,1065,612"                                           # 씨름꾼 머리 뒤 두루마리 지움 · 망토 자락
$Z crop p3.png z ZF 1240 600 1560 780;      cm ZF ZF1
$Z paste p4.png z ZF z/cm_ZF1.png p5.png "1330,640,1490,778"                                          # 일꾼 다리 이음매
$Z crop p5.png z ZT 900 660 1362 920;       cm ZT ZT1
$Z paste p5.png z ZT z/cm_ZT1.png p6.png "1030,676,1130,740;1070,860,1112,915"                      # 탁자 밑 줄 · 문어 머리
python3 $D/L43g_pil2.py p6.png p7.png                                                                 # 씨름꾼 두루마리의 빛깔 네모 넷 · 앞머리 줄 자국
$Z crop p7.png z ZR 1150 790 1762 1144;     cm ZR ZR1
$Z paste p7.png z ZR z/cm_ZR1.png p8.png "1290,795,1640,1144"                                        # 아래 오른쪽 문어 머리 · 치켜든 토막
$Z crop p7.png z ZG 220 900 520 1069;       cm ZG ZG1
$Z paste p8.png z ZG z/cm_ZG1.png p9.png "325,985,395,1045"                                          # 왼쪽 두루마리 끝 쪽 네모 셋
python3 $D/L43g_pil3.py p9.png p10.png                                                                # 치켜든 토막 끝 두 칸 = 불완전 일치
$Z crop p10.png z ZI 880 300 1560 683;      cm ZI ZI1
$Z paste p10.png z ZI z/cm_ZI1.png p11.png "1065,335,1385,683"                                       # 기계에 들어가는 종이의 빛깔 네모
$Z crop p10.png z ZB2 520 980 760 1115;     cm ZB2 ZB21
$Z paste p11.png z ZB2 z/cm_ZB21.png p12.png "540,990,760,1115"                                      # 은빛 좀벌레
$Z crop p10.png z ZC 250 735 470 859;       cm ZC ZC1
$Z paste p12.png z ZC z/cm_ZC1.png p13.png "312,760,440,859"                                         # 우는 일꾼 종이 밑
python3 $D/L43g_pil4.py p13.png p14.png                                                               # 왼쪽 두루마리 네 빛 네모 · 앞머리 · 찢기는 뭉치 네모
$Z crop p14.png z ZK 560 530 1321 958;      cm ZK ZK1
$Z paste p14.png z ZK z/cm_ZK1.png p15.png "735,540,988,958"                                         # 머리 여백에 앉은 판다(씨름꾼 → 판다)
cp p15.png final.png
echo "→ $W/final.png"
