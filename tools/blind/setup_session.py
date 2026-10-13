#!/usr/bin/env python3
"""setup_session.py — 그릴 때마다 블라인드 1세션(세션_절차.md)의 준비물을 만든다. 2026-10-13
  python3 tools/blind/setup_session.py <pid> <batch> <작업폴더> [--topic "판 표제어 정답"] [--zones "구역=표제어; …"] [--unified]
  → 작업폴더/<pid>.png · 약속표.md · A/ B/ grader/ · labels.txt(섞은 개념 이름)
    prompt_stage1_A.txt · prompt_stage1_B.txt · prompt_stage2_A.txt · prompt_stage2_B.txt · prompt_stage3_A.txt · prompt_stage3_B.txt · prompt_grader.txt
  판독자는 /tmp/b2 를 열면 안 되므로 그림과 약속표를 작업폴더에 복사해 준다(같은 것을 본다).
  채점 정답표는 tools/blind/brief/<batch>_truth.md — 먼저 node tools/blind/make_brief.js <번호> 를 돌려 둔다."""
import sys, os, json, random, shutil, argparse

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
ap = argparse.ArgumentParser()
ap.add_argument('pid'); ap.add_argument('batch'); ap.add_argument('work')
ap.add_argument('--topic', default=''); ap.add_argument('--zones', default='')
ap.add_argument('--unified', action='store_true', help='단원 통합판이라고 알려 준다(b73 과 같은 조건)')
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
규칙은 그대로다 — 그림 · 당신의 조각 · 약속표.md 말고는 아무것도 열지 마라({other}/, grader/, labels.txt, prompt_*.txt, {ROOT} 금지).
[기록] 작업 폴더 {X}/ 에 stage2.md 로 Write(한국어, 2,500자 안팎, 표제어 후보는 **굵게**, 1단계와 달라진 곳은 「↻」 표시). 나에게는 1단계와 같은 형식만 돌려라."""

def s3(X):
    return f"""[3단계 — 이름 주고 되찾기] 아래는 이 판이 가르치려는 개념의 이름 목록이다(순서는 섞었다). 같은 그림을 다시 보고, 개념마다 그림의 어느 물건(또는 사람 · 동작 · 배치)이 그것을 나르는지 가리켜라. 잇는 고리(소리 / 모양 / 글자 / 뜻 / 자리 / 개수)도 한 마디. 어느 물건도 그 개념을 나르지 못하면 「못 찾음」이라고 솔직히 적어라 — 억지로 끼워 맞추지 마라. 개념 하나에 물건이 둘 이상이면 다 적고, 물건 하나가 개념 둘을 나르면 그것도 적어라.
{lab}
규칙은 그대로다(그림 · 당신의 조각 · 약속표.md 만).
[기록] 작업 폴더 {X}/ 에 stage3.json 으로 Write:
{{"pid":"{a.pid}","map":[{{"concept":"개념 이름(준 그대로)","obj":"그림의 물건 또는 못 찾음","link":"소리/모양/글자/뜻/자리/개수 + 한 마디","sure":"높음/중간/낮음"}}]}}
나에게는 「3단계 끝 — 못 찾음 <k>개」만 돌려라."""

n = len(m['rows'])
zone_part = (f"""- 구역 표제어: {a.zones} — 몇이 맞았나(1단계 · 2단계).
""" if a.zones else '')
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
- warm (Y/P/N): 2단계(약속표를 본 뒤) 짐작이 그 행의 개념과 맞는가.
- cued (Y/P/N): 3단계에서 그 행의 개념을 **그 행의 물건**에 제대로 이었는가. P = 물건은 맞는데 고리가 엉뚱하다, 또는 다른 물건에 이었다. N = 못 찾음·틀림.
- note: 한 줄 — 특히 N·P 인 까닭(안 보임 / 너무 작음 / 다른 것으로 읽힘 / 이름이 안 섬 / 약속표 덕 / 이름 목록이 흘림).

채점 2 — 판 전체, 학생마다:
- 판 표제어 1순위가 「{a.topic or m['unit'] + ' — ' + m['title']}」로 맞는가(Y/P/N) — 1단계 · 2단계 각각.
{zone_part}- 사실 복원율 — 틀 행을 뺀 사실 행에서: cold=Y · warm=Y · cued=Y 비율 (P 는 따로 센다).
- 통과 기준: 판 표제어 1순위 맞음 · (구역이 있으면) 구역 표제어 전부 · 사실 warm ≥ 90% — cued 기준도 함께 보고하라.

결과를 세 파일로 Write 하라:
1) {ROOT}/tools/blind/out/{a.pid}.json — 학생 A 의 표준 꼴(cold = 1단계 기준, cued = 3단계 기준):
{{"pid":"{a.pid}","reader":"A","batch":"{a.batch}","rows":[{{"n":1,"seen":"Y","cold":"N","warm":"Y","cued":"Y","note":"…"}}, …{n}행],"panel_note":"한 줄"}}
2) {ROOT}/tools/blind/out/{a.pid}.B.json — 학생 B 같은 꼴("reader":"B").
3) {ROOT}/tools/blind/out/{a.pid}.통합판독.json —
{{"batch":"{a.batch}","A":{{"판1_s1":"…","판1_s1_맞음":"Y/P/N","판1_s2":"…","판1_s2_맞음":"Y/P/N","구역_s1":"k/z","구역_s2":"k/z","복원":{{"cold":"x/m","warm":"x/m","cued":"x/m","P":{{"cold":k,"warm":k,"cued":k}}}},"통과_warm":"Y/N","통과_cued":"Y/N"}},"B":{{…같은 꼴}},"두사람다_못한행":[n…],"고칠자리":["행 n — 무엇을 어떻게(그림 고침 / 글 고침)"],"총평":"세 줄"}}
마지막 답으로는 아래 요약만 돌려라:
A: 판1 s1 <Y/P/N> s2 <Y/P/N> · 구역 s1 k/z s2 k/z · 복원 cold x/m warm x/m cued x/m
B: (같은 꼴)
둘 다 못한 행: …
고칠 자리: …"""

for X, other in (('A', 'B'), ('B', 'A')):
    open(os.path.join(W, f'prompt_stage1_{X}.txt'), 'w', encoding='utf-8').write(s1(X, other))
    open(os.path.join(W, f'prompt_stage2_{X}.txt'), 'w', encoding='utf-8').write(s2(X, other))
    open(os.path.join(W, f'prompt_stage3_{X}.txt'), 'w', encoding='utf-8').write(s3(X))
open(os.path.join(W, 'prompt_grader.txt'), 'w', encoding='utf-8').write(grader)
print('준비 끝:', W, '· 행', n, '· 그림', (w, h))
