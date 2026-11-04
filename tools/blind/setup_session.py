#!/usr/bin/env python3
"""setup_session.py — 그릴 때마다 블라인드 1세션(세션_절차.md)의 준비물을 만든다. 2026-10-13
  python3 tools/blind/setup_session.py <pid> <batch> <작업폴더> [--topic "판 표제어 정답"] [--zones "구역=표제어; …"] [--unified]
  → 작업폴더/<pid>.png · 약속표.md · A/ B/ grader/ · labels.txt(섞은 개념 이름)
    prompt_stage1_A.txt · prompt_stage1_B.txt · prompt_stage2_A.txt · prompt_stage2_B.txt · prompt_stage3_A.txt · prompt_stage3_B.txt · prompt_grader.txt
  판독자는 /tmp/b2 를 열면 안 되므로 그림과 약속표를 작업폴더에 복사해 준다(같은 것을 본다).
  채점 정답표는 tools/blind/brief/<batch>_truth.md — 먼저 node tools/blind/make_brief.js <번호> 를 돌려 둔다.
  2026-11-02(b137 부터): 2단계에 ⑤ 까닭을 묻는다 — 사용자 결정 (ㄷ) 「2번은 (ㄷ) 으로 하는데 음, 잠재적인 부작용은 별로 없을거같으니까 그렇게 해버리자」.
    지금까지는 까닭을 묻지 않아 독자가 물건만 늘어놓았고, 채점은 정답표의 ★(까닭)을 「말하지 않음」으로 깎았다(s45u02 b131 ~ b136).
  2026-11-03(b139 부터): 1단계에 「조각 스무 개 이상」 꼼꼼함 줄 — 처음 띄운 b139 독자 둘이 도구 6 ~ 7 번(앞 판들은 59 ~ 82 번)만 쓰고 얕게 답해 그 판을 버렸다.
  2026-11-03(b139 부터): 이름 고리 ★ 는 2단계 어디서든 인정 — 사용자 선택 「이름 고리 ★는 2단계 어디서든 인정 (권장)」.
    b138 에서 이름 고리 ★(porphyra · granum · 당근 · 외막/내막 · 관다발 = 묶음)를 물건 풀이에서 맞히고도 까닭 줄에 옮기지 않아 P 가 된 행이 다섯이었다.
  2026-11-04: 잣대 바꿈 — 사용자 선택 「닻 판 대조로 바꿈 (권장)」 · 「단원 줄기가 서면 Y (권장)」.
    잣대 보정 실험(b141)에서 이미 채택한 s45u01 이 지금 절차로 13 · 15 /21(b130 19 · 20) — 채점자의 엄격함이 판 점수를 움직였다.
    --anchor <닻 폴더>: 채택판의 판독(학생 답)을 같은 채점자가 같은 잣대로 함께 매겨, 이 판의 warm 평균이 닻 평균보다 2 행 넘게 낮지 않으면 통과.
    --trunk "<단원 줄기>": 판 표제어는 1순위가 단원 줄기를 세우면 Y(갈래는 구역 표제어가 따로 잰다).
    --memo <파일>: 이 판만의 채점 메모(한 줄에 하나). 표준 채점 메모(틀 행 · 구역 쪼개기 · ★ · ⚠ · 정답표 전체 · 손질 자국)는 도구가 넣는다."""
import sys, os, json, random, shutil, argparse

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
ap = argparse.ArgumentParser()
ap.add_argument('pid'); ap.add_argument('batch'); ap.add_argument('work')
ap.add_argument('--topic', default=''); ap.add_argument('--zones', default='')
ap.add_argument('--unified', action='store_true', help='단원 통합판이라고 알려 준다(b73 과 같은 조건)')
ap.add_argument('--trunk', default='', help='판 표제어의 단원 줄기(2026-11-04 — 줄기가 서면 Y)')
ap.add_argument('--anchor', default='', help='닻 폴더(tools/blind/anchor/<pid>_<batch>) — 채택판 판독을 같은 채점자가 함께 매긴다')
ap.add_argument('--memo', default='', help='이 판만의 채점 메모 파일(한 줄에 하나)')
a = ap.parse_args()
W = os.path.abspath(a.work)
man = json.load(open(os.path.join(ROOT, 'tools/blind/manifest.json'), encoding='utf-8'))
m = next(x for x in man if x['pid'] == a.pid)
truth = os.path.join(ROOT, 'tools/blind/brief', a.batch + '_truth.md')
if not os.path.exists(truth): sys.exit('정답표가 없다 — node tools/blind/make_brief.js <번호> 먼저: ' + truth)
os.makedirs(W, exist_ok=True)
for d in ('A', 'B', 'grader'): os.makedirs(os.path.join(W, d), exist_ok=True)
png = os.path.join(W, a.pid + '.png')
shutil.copy(os.path.join(ROOT, 'tools/blind/png', a.pid + '.png'), png)
shutil.copy(os.path.join(ROOT, 'tools/blind/reservations.md'), os.path.join(W, '약속표.md'))
seed = int(''.join(ch for ch in a.batch if ch.isdigit()) or 0)
labels = [r['label'] for r in m['rows']]; rng = random.Random(seed); L = labels[:]; rng.shuffle(L)
lab = '\n'.join(f'{i+1}. {l}' for i, l in enumerate(L))
open(os.path.join(W, 'labels.txt'), 'w', encoding='utf-8').write(lab + '\n')
from PIL import Image
w, h = Image.open(png).size

UNI = ' 이 판은 한 단원의 개념 여러 개를 한 장에 모은 「통합판」이다.' if a.unified else ''

def s1(X, other):
    return f"""당신은 한의대·편입 생물학 시험을 준비하는 학생이자 그림 판독자다. 아래 그림은 그 시험을 위한 암기용 그림책(Sketchy 식 — 그림 속 물건 하나가 생물학 사실 하나를 나르는 무대 그림)의 한 판이다.{UNI} 이 판에 대한 사전 정보(단원 이름 · 제목)는 일부러 주지 않는다.

그림: {png}  ({w}×{h})
당신의 작업 폴더: {W}/{X}/

규칙 — 어기면 시험이 무효다:
- 열어도 되는 것: 위 그림 하나, 그리고 당신이 그 그림에서 잘라 작업 폴더에 저장한 조각뿐이다. 같은 폴더의 다른 파일(약속표.md, labels.txt, prompt_*.txt, {other}/, grader/)은 내가 허락하기 전에는 절대 열지 마라.
- {ROOT} 아래의 어떤 파일도 열거나 검색하지 마라. 다른 폴더를 뒤지지 마라. 웹 검색도 하지 마라.
- 그림은 Read 로 본다. 작은 부분은 Python(PIL)으로 잘라 2~3배로 키워 작업 폴더에 저장한 뒤 Read 해도 된다(조각 수 제한 없음 — 꼼꼼히 봐라. 위쪽 선반, 벽에 걸린 것, 바닥의 작은 것, 손에 든 것, 개수까지).
- 꼼꼼함이 이 시험의 전부다: 답을 쓰기 전에 그림을 구역마다 조각 다섯 개 이상(판 전체 스무 개 이상) 잘라 키워서 Read 하라. 전체 그림 한 장만 보고 짐작해 쓰면 시험이 무효다.

[1단계 — 생판] 그림만 보고 답하라.
 ① 판 전체의 표제어 — 이 그림 전체가 묶는 생물학 단원·개념 — 1순위·2순위와 확신도(%).
 ② 그림을 왼쪽부터 구역으로 나눠, 구역마다: 그 구역의 표제어 하나 + 그 구역의 물건·사람·동작 각각이 나르는 생물학 사실(셀 수 있는 것은 개수까지, 근거: 소리/모양/뜻/자리/개수 한 마디). 모르면 「모름」.
 ③ 뜻 모를 물건 · 어색한 것 · 서로 헷갈리는 것 · 이어 붙인 흔적.
 ④ 이 그림이 한 문장으로 가르치려는 것.

[기록] 작업 폴더에 stage1.md 로 Write 하라(한국어, 2,500자 안팎, 표제어 후보는 **굵게**). 그다음 나에게는 아래 형식만 돌려라 — 다른 말은 붙이지 마라:
판 1순위: <표제어> (<n>%) / 판 2순위: <표제어> (<n>%)
구역1: <표제어> — 읽힌 사실 <k>개
(구역 수만큼)
잔결: <한 줄>"""

def s2(X, other):
    return f"""[2단계 — 덱 약속] 1단계 답을 확정해 적었으니 이제 {W}/약속표.md 를 Read 하라 — 이 그림책이 모든 판에서 같은 뜻으로 쓰는 「물건 = 개념」 약속 목록이다. 실제 독자는 이것을 배우고 온다. 그 어휘로 같은 그림을 다시 보고(필요하면 조각을 더 잘라 봐라) 1단계의 ①~④를 다시 답하라. 1단계 답을 고집할 필요 없고, 약속으로 더 잘 풀리는지 정직하게 판정하라. 1단계에서 놓친 물건이 보이면 더하고, 「모름」이던 물건이 풀리면 그 근거를 적어라. 약속표에 없는 물건은 억지로 약속에 끼우지 마라.
 ⑤ 까닭 — 이번에 새로 묻는 것이다. ②에 적은 사실마다 「그 물건이 왜 하필 그 모습으로 그려졌는가」를 한 마디씩 덧붙여라: 크기 · 개수 · 자리 · 빛깔 · 동작 · 곁의 물건과의 견줌(같은 것을 나란히 둠 · 하나만 다름 · 비어 있음 · 비켜 감 · 위아래로 맞섬 같은 대비)이 「그래서 무엇이 어떻게 되는가 · 왜 그런가」를 어떻게 나르는지, 그리고 그림의 어디(무엇과 무엇을 견줘서)에서 그것을 읽었는지. 그림에서 까닭이 안 읽히면 「까닭 모름」이라고 솔직히 적어라 — 그림에 없는 까닭을 지어내지 마라.
규칙은 그대로다 — 그림 · 당신의 조각 · 약속표.md 말고는 아무것도 열지 마라({other}/, grader/, labels.txt, prompt_*.txt, {ROOT} 금지).
[기록] 작업 폴더 {X}/ 에 stage2.md 로 Write(한국어, 3,500자 안팎, 표제어 후보는 **굵게**, 1단계와 달라진 곳은 「↻」 표시, 사실마다 「→ 까닭: …」 한 줄). 나에게는 1단계와 같은 형식만 돌려라."""

def s3(X):
    return f"""[3단계 — 이름 주고 되찾기] 아래는 이 판이 가르치려는 개념의 이름 목록이다(순서는 섞었다). 같은 그림을 다시 보고, 개념마다 그림의 어느 물건(또는 사람 · 동작 · 배치)이 그것을 나르는지 가리켜라. 잇는 고리(소리 / 모양 / 글자 / 뜻 / 자리 / 개수)도 한 마디. 어느 물건도 그 개념을 나르지 못하면 「못 찾음」이라고 솔직히 적어라 — 억지로 끼워 맞추지 마라. 개념 하나에 물건이 둘 이상이면 다 적고, 물건 하나가 개념 둘을 나르면 그것도 적어라.
{lab}
규칙은 그대로다(그림 · 당신의 조각 · 약속표.md 만).
[기록] 작업 폴더 {X}/ 에 stage3.json 으로 Write:
{{"pid":"{a.pid}","map":[{{"concept":"개념 이름(준 그대로)","obj":"그림의 물건 또는 못 찾음","link":"소리/모양/글자/뜻/자리/개수 + 한 마디","sure":"높음/중간/낮음"}}]}}
나에게는 「3단계 끝 — 못 찾음 <k>개」만 돌려라."""

n = len(m['rows'])
frame = [1] if a.unified else []
nf = n - len(frame)
topic_full = a.topic or (m['unit'] + ' — ' + m['title'])
trunk = a.trunk or topic_full
zone_part = (f"""- 구역 표제어: {a.zones} — 몇이 맞았나(1단계 · 2단계).
""" if a.zones else '')

# 표준 채점 메모 — b140 · b141 에서 손으로 붙이던 줄을 도구로 옮김(2026-11-04)
memo = []
if frame:
    memo.append(f"틀 행은 행 1 하나뿐이다. ★ 표시가 붙은 행도 사실 행이다 — 사실 행은 2~{n} 의 {nf} 행, 분모는 {nf}.")
if a.zones:
    memo.append("구역: 학생이 정답 구역 하나를 더 잘게 쪼개 읽어도 쪼갠 조각이 모두 그 정답 구역의 식구이고 표제어가 맞으면 그 정답 구역은 맞음으로 센다. 다른 정답 구역의 식구를 섞어 한 구역으로 묶었거나 표제어가 틀리면 틀림. 학생이 「추정」이라고 단서를 달았어도 표제어가 맞으면 맞음.")
memo.append(f"판 표제어(사용자 결정 2026-11-04 「단원 줄기가 서면 Y」): 1순위가 이 판의 단원 줄기(「{trunk}」)를 세우면 Y — 판 정답 「{topic_full}」의 하위 갈래는 구역 표제어가 따로 재므로 1순위 한 줄에 다 서지 않아도 깎지 않는다. 줄기가 다른 단원이나 같은 단원의 다른 쪽으로 가면 P, 전혀 다르면 N.")
memo.append("행이 여러 사실을 나르면(예: 「두 걸음」 · 「이름 + 성질」), 정답표 사실 칸의 ★ · ⚠ 핵심까지 읽혀야 Y 다. 핵심 하나가 빠지면 P.")
memo.append("정답표는 사실 칸이 끝까지 다 적혀 있다. 사실 칸의 ★ 는 모두 같은 무게로 본다.")
memo.append("그림에 「이어 붙인 흔적」 · 어색한 손질 자국이 보인다고 학생이 적으면, 그것이 실제로 그림에 있는지 확인해 고칠자리에 자리(대략 x · y)와 함께 적어라.")
if a.memo:
    memo += [l.strip().lstrip('-').strip() for l in open(a.memo, encoding='utf-8') if l.strip()]
memo_txt = '\n'.join('- ' + l for l in memo)

# 닻 판 — 사용자 선택 「닻 판 대조로 바꿈 (권장)」(2026-11-04)
anc = None; anchor_part = ''; anchor_out = ''; anchor_json = ''; anchor_sum = ''
pass_line = "- 통과 기준: 판 표제어(단원 줄기) Y — 1 · 2단계 둘 다 · (구역이 있으면) 구역 표제어 전부 · 사실 warm ≥ 90% — cued 기준도 함께 보고하라."
if a.anchor:
    AD = a.anchor if os.path.isabs(a.anchor) else os.path.join(ROOT, a.anchor)
    anc = json.load(open(os.path.join(AD, 'meta.json'), encoding='utf-8'))
    AW = os.path.join(W, 'anchor')
    src = os.path.join(ROOT, anc['readings'])
    for X in ('A', 'B'):
        os.makedirs(os.path.join(AW, X), exist_ok=True)
        for f in ('stage1.md', 'stage2.md', 'stage3.json'):
            shutil.copy(os.path.join(src, f'{X}_{f}'), os.path.join(AW, X, f))
    apng = os.path.join(AW, anc['pid'] + '.png'); shutil.copy(os.path.join(AD, anc['png']), apng)
    atruth = os.path.join(AW, '정답표.md'); shutil.copy(os.path.join(AD, anc['truth']), atruth)
    shutil.copy(os.path.join(AD, anc['reservations']), os.path.join(AW, '약속표.md'))
    aw_, ah_ = Image.open(apng).size
    anf = anc['facts']
    margin = '2 행' if anf == nf else f"{round(200 / anf, 1)}%p(닻의 2 행 ÷ {anf})"
    pass_line = f"""- 통과 기준(사용자 결정 2026-11-04 「닻 판 대조로 바꿈」): 판 표제어(단원 줄기) Y — 1 · 2단계 둘 다 · (구역이 있으면) 구역 표제어 전부 · **사실 warm — 이 판 두 학생의 warm Y 비율 평균이 닻 판 두 학생의 평균보다 {margin} 넘게 낮지 않으면 통과**(아래 「닻 판」). 90% 는 참고로만 적는다 — cued 도 함께 보고하라."""
    anchor_part = f"""
닻 판 — 같은 잣대로 함께 채점한다(사용자 결정 2026-11-04 「닻 판 대조로 바꿈 (권장)」. 채점자마다 엄하고 순한 정도가 달라 판의 점수가 채점자를 따라 움직인다 — 이미 채택한 판을 같은 채점자가 같은 잣대로 함께 매겨, 그 차로 판정한다).
- 닻 판: {anc['pid']}({anc['title']}) — 이미 채택한 판. 학생 둘(닻 A · 닻 B)이 위와 같은 세 단계 · 같은 물음으로 판독한 것({anc['batch']})을 그대로 다시 채점한다. 학생 답은 새로 받지 않는다.
- 파일: 그림 {apng} ({aw_}×{ah_}) · 정답표 {atruth}({anc['rows']}행 · 사실 행 {anf}) · 그 학생들이 받은 약속표 {AW}/약속표.md · 닻 A {AW}/A/stage1.md · stage2.md · stage3.json · 닻 B {AW}/B/ 같은 세 파일. 작은 부분은 잘라 키워 {W}/grader/ 에 저장해 봐도 된다.
- 닻 판의 판 표제어 단원 줄기: 「{anc['trunk']}」(판 정답 「{anc['topic']}」) · 구역 표제어: {anc['zones']}
- 닻 판만의 채점 메모: {' / '.join(anc.get('memo', [])) or '없음'}
- 위 채점 1 · 2 와 채점 메모를 닻 판에도 **같은 엄격함으로** 적용한다. 차례: 이 판({a.pid})을 먼저 다 채점해 1) ~ 3) 을 쓴 뒤 닻 판을 채점하라. 한 판의 점수를 보고 다른 판의 판정을 맞추지 마라 — 두 판 모두 그 판의 정답표와 학생 답만으로 매긴다.
"""
    anchor_out = f"""4) 닻 판: {W}/grader/닻_{anc['pid']}.json · {W}/grader/닻_{anc['pid']}.B.json — 1) · 2) 와 같은 꼴("pid":"{anc['pid']}","batch":"{anc['batch']}").
"""
    anchor_json = f""","닻":{{"pid":"{anc['pid']}","batch":"{anc['batch']}","A":{{"판1_s2_맞음":"Y/P/N","구역_s2":"k/z","warm":"x/{anf}","cued":"x/{anf}"}},"B":{{…같은 꼴}}}},"닻대조":{{"이판_warm_평균":"x.x/{nf} (p%)","닻_warm_평균":"y.y/{anf} (q%)","차":"±r 행 (±s%p)","통과":"Y/N"}}"""
    anchor_sum = """
닻: A warm x/m · B warm x/m · 평균 차 ±r 행 → warm 통과 Y/N"""

grader = f"""당신은 채점자다. 생물학 암기 그림책(Sketchy 식 — 그림 속 물건 하나가 사실 하나를 나르는 무대 그림)의 판 {a.pid} 를, 사전 정보 없는 학생 둘(A · B)이 세 단계로 판독했다. 정답표와 대조해 엄격하게 채점하라. 후하게 주지 마라 — 「약속표 덕」「이름 목록이 흘린 것」「배경지식으로 맞힌 것(그림에서 읽지 않은 것)」은 note 에 반드시 밝힌다.

파일 (모두 Read 로 연다):
- 그림: {png} ({w}×{h}). 직접 보고 학생 말이 그림과 맞는지 확인하라. 작은 부분은 Python(PIL)으로 잘라 키워 {W}/grader/ 에 저장해 봐도 된다.
- 정답표: {truth} 의 「## {a.pid}」 절 — {n}행.
- 덱 약속표(2단계에서 학생에게 준 것): {W}/약속표.md
- 학생 A: {W}/A/stage1.md (그림만 · 단원명/제목 없이) · A/stage2.md (약속표 준 뒤) · A/stage3.json (개념 이름 목록을 준 뒤 물건 되찾기)
- 학생 B: {W}/B/ 같은 세 파일
이 밖의 파일(sketchy.html, manifest.json, 다른 out/ 파일 등)은 열지 마라.

채점 1 — 행마다(n=1..{n}), 학생마다:
- seen (Y/N): 1·2단계 어디서든 그 행의 물건을 알아보고 적었는가(설명이 달라도 같은 물건이면 Y). 틀 행이 있으면 「구역을 정답대로 나눠 읽었는가」.
- cold (Y/P/N): 1단계(약속표 없이, 단원명·제목도 없이) 짐작이 그 행의 개념과 맞는가. P = 방향은 맞는데 구체가 틀림/모자람.
- warm (Y/P/N): 2단계(약속표를 본 뒤) 짐작이 그 행의 개념과 맞는가. 2단계에는 사실마다 「→ 까닭」(그 모습이 왜 그렇게 그려졌는지 · 그림의 무엇을 견줘 읽었는지)을 적게 했다 — 정답표 사실 칸의 ★ 는 두 갈래로 판정한다 — ⓐ **이름 고리 ★**(「~ 가 곧 이름이다」 · 그리스말 · 라틴말 말뿌리 · 소리 고리처럼 그 물건에 그 이름을 붙인 까닭)는 2단계 어디서든(물건 풀이 줄이든 까닭 줄이든 — 1단계에서 말하고 2단계에서 거두지 않았으면 그것도) 말했으면 Y, ⓑ **그 밖의 ★**(견줌 · 개수 · 자리 · 동작이 나르는 성질과 까닭)는 이 「까닭」 줄에서 찾는다: 까닭이 맞으면 Y(그림 근거 없이 배경지식으로만 붙인 까닭은 Y 로 두되 note 에 「배경지식」), 까닭을 안 적었거나(「까닭 모름」 포함) 틀리면 P. 1단계에서 맞힌 것을 2단계에서 「모름」으로 거뒀으면 거둔 쪽으로 친다.
- cued (Y/P/N): 3단계에서 그 행의 개념을 **그 행의 물건**에 제대로 이었는가. P = 물건은 맞는데 고리가 엉뚱하다, 또는 다른 물건에 이었다. N = 못 찾음·틀림.
- note: 한 줄 — 특히 N·P 인 까닭(안 보임 / 너무 작음 / 다른 것으로 읽힘 / 이름이 안 섬 / 약속표 덕 / 이름 목록이 흘림).

채점 2 — 판 전체, 학생마다:
- 판 표제어 1순위가 이 판의 단원 줄기(「{trunk}」)를 세우는가(Y/P/N) — 1단계 · 2단계 각각(판 정답 「{topic_full}」 · 아래 채점 메모).
{zone_part}- 사실 복원율 — 틀 행을 뺀 사실 행에서: cold=Y · warm=Y · cued=Y 비율 (P 는 따로 센다).
{pass_line}

채점 메모(이 덱의 다른 통합판들과 같은 자 — warm 의 ★ 판정은 위 warm 줄을 따른다):
{memo_txt}
{anchor_part}
결과를 Write 하라(이미 있는 같은 이름 파일은 앞 세션 것이니 읽지 말고 덮어써라):
1) {ROOT}/tools/blind/out/{a.pid}.json — 학생 A 의 표준 꼴(cold = 1단계 기준, cued = 3단계 기준):
{{"pid":"{a.pid}","reader":"A","batch":"{a.batch}","rows":[{{"n":1,"seen":"Y","cold":"N","warm":"Y","cued":"Y","note":"…"}}, …{n}행],"panel_note":"한 줄"}}
2) {ROOT}/tools/blind/out/{a.pid}.B.json — 학생 B 같은 꼴("reader":"B").
3) {ROOT}/tools/blind/out/{a.pid}.통합판독.json —
{{"batch":"{a.batch}","A":{{"판1_s1":"…","판1_s1_맞음":"Y/P/N","판1_s2":"…","판1_s2_맞음":"Y/P/N","구역_s1":"k/z","구역_s2":"k/z","복원":{{"cold":"x/m","warm":"x/m","cued":"x/m","P":{{"cold":k,"warm":k,"cued":k}}}},"warm_90":"Y/N(참고)","통과_cued":"Y/N"}},"B":{{…같은 꼴}},"두사람다_못한행":[n…],"고칠자리":["행 n — 무엇을 어떻게(그림 고침 / 글 고침)"],"까닭_효과":"한두 줄 — 지어낸 까닭 · 배경지식만으로 댄 까닭 · 이름 고리 ★ 를 물건 풀이 줄에서 세운 행"{anchor_json},"판정":{{"판표제어":"Y/N","구역":"Y/N","warm":"Y/N","통과":"Y/N"}},"총평":"세 줄"}}
{anchor_out}마지막 답으로는 아래 요약만 돌려라:
A: 판1 s1 <Y/P/N> s2 <Y/P/N> · 구역 s1 k/z s2 k/z · 복원 cold x/m warm x/m cued x/m
B: (같은 꼴){anchor_sum}
판정: 통과 Y/N
둘 다 못한 행: …
까닭 효과: …
고칠 자리: …"""

for X, other in (('A', 'B'), ('B', 'A')):
    open(os.path.join(W, f'prompt_stage1_{X}.txt'), 'w', encoding='utf-8').write(s1(X, other))
    open(os.path.join(W, f'prompt_stage2_{X}.txt'), 'w', encoding='utf-8').write(s2(X, other))
    open(os.path.join(W, f'prompt_stage3_{X}.txt'), 'w', encoding='utf-8').write(s3(X))
open(os.path.join(W, 'prompt_grader.txt'), 'w', encoding='utf-8').write(grader)
print('준비 끝:', W, '· 행', n, '· 그림', (w, h))
