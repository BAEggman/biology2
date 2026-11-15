#!/usr/bin/env python3
# reserve_A17.py — 17장 덧붙임(L10a +정거장 둘 · GTP 칩 · 2026-11-15 · Opus 5.5)의 예약.
import json
P = '/tmp/b2/tools/hooks.json'
txt = open(P, encoding='utf-8').read(); d = json.loads(txt)
assert json.dumps(d, ensure_ascii=False, indent=1) == txt
R = d['_심볼예약']
B = '[2026-11-15 17장 덧붙임 L10a]'
new = {
 '겨자색 중산모에서 레일 위를 따라 정거장 아래 상자(기단)까지 이어진 점선 화살 + 그 기단 바로 앞 레일 위에서 팔짱 끼고 쭈그려 한 다리를 찬 코사크 춤꾼(넓적한 회색 털모자 · 탄띠 단 남색 웃옷 · 붉은 허리띠)':
   f'진핵 번역 개시 — 작은 소단위체가 5′ 캡에 붙어 AUG 까지 훑음(스캐닝) · 코작 서열에서 멈춤 · 개시 아미노산 Met 전용 {B} — L10a s13(옛 s10p01b 위 칸). 코사크 = 코작(【모자】 줄의 약속 — 「다른 이름에 모자를 쓰면 충돌한다」). ⚠ 큰 검은 털모자 + 붉은 제복은 「영국 근위병」으로 읽혔다(일치 검사 1회) → 넓적한 회색 파파하 · 남색 웃옷(KC).',
 '모자 없는 짧은 두 줄 레일 토막 + 빛살 뻗는 금빛 둥근 판에 위에서 곧장 떨어져 앉은 작은 보라 상자(점선 없음) + 상자 위 구슬에 붙어 솟은 작은 포크':
   f'원핵 번역 개시 — 작은 소단위체가 샤인-달가노 서열에 곧장 결합(훑지 않음) · 개시 아미노산 fMet 전용 {B} — L10a s14(옛 s10p01b 아래 칸). 빛나는 판 = 샤인(shine) · 포크 = 포르밀(【네 갈퀴 포크】) · 구슬 = 메티오닌. 모자 없음 = 캡 없는 세균 mRNA.',
}
for k, v in new.items():
    assert k not in R, k
    R[k] = v
def add(key, note):
    v = R[key]; assert isinstance(v, str), key
    R[key] = v + ' ' + note
add('짙은 회색 네모 칩', f'★ {B} 금 간 칩 = 쓴 GTP(쪼개진 동전 = 쓴 ATP 와 같은 말버릇) — L10a 정거장 앞 바닥에 왼쪽(개시) 하나 · 가운데(신장 — 코돈 인식 · 자리옮김) 둘 · 오른쪽(종결 뒤 해리) 둘(PIL `L10a_pil.py` · 수를 세어 그림). 펩타이드 결합 자리(s8)에는 칩이 없다.') if '짙은 회색 네모 칩' in R else None
key = next(k for k in R if k.startswith('네 갈퀴 포크'))
add(key, f'★ {B} L10a s14 — 세균 쪽 작은 보라 상자 위 구슬(메티오닌)에 붙어 솟은 작은 포크 = fMet.')
out = json.dumps(d, ensure_ascii=False, indent=1)
assert json.loads(out) == d
open(P, 'w', encoding='utf-8').write(out)
print('예약', len(R))
