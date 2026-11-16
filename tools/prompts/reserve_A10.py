#!/usr/bin/env python3
# reserve_A10.py — 10장 덧붙임(L31a s12 · L31b s19 · L31c s8 · 2026-11-16 · Opus 5.5)의 예약.
import json
P = '/tmp/b2/tools/hooks.json'
txt = open(P, encoding='utf-8').read(); d = json.loads(txt)
assert json.dumps(d, ensure_ascii=False, indent=1) == txt
R = d['_심볼예약']
B = '[2026-11-16 10장 덧붙임]'
new = {
 '붉은 커튼 문 옆 벽의 세로 그림 안내판 — 붉은 정육면체 · 흰 공 → 화살 → 잿빛 연기 · 파란 물방울 · 금빛 동전 / 액자 셋(초록 당구대 · 레몬 · 벽돌 담장의 펌프집)':
   f'세포호흡 한 줄(유기 연료 산화 → ATP · 노폐물 CO₂ + 물 · 이화 경로) · 세 단계(해당 = L31a 당구장 · TCA = L31b 레몬 공장 · 전자전달계 = L32a 펌프집 담장) 전용 {B} — L31a s12. 글자 없는 그림 판(독자가 「글자 없음」을 확인).',
 '가위 노인의 앞치마 위 가죽 허리띠에 매단 다섯 — 짧은 파란 넥타이 · 빨간 립스틱 · 파란 짐표 · 초록 네모 통 · 속이 빈 파란 둥근 양동이':
   f'피루브산 탈수소효소 복합체(PDH · 다효소)의 보조인자 다섯 = TPP · 리포산 · CoA · FAD · NAD⁺ 전용 {B} — L31b s19. 넥타이 = 티아민(L12d s5 와 같은 말버릇) · 립스틱 = 립(리포산) · 짐표 = CoA(L31b 꾸러미의 그 짐표) · 네모 통 = FAD · 둥근 통 = NAD⁺(빈 것 · `L31b_pil.py` 로 속을 어둡게).',
 '열린 뒷문 문턱으로 드는 바깥 바람(흰 물결 선 · 작은 흰 방울)에 X 눈으로 쓰러진 창백한 손님 + 곁의 노란 비옷 · 이마에 선글라스 · 붉은 블록 한 아름의 손님':
   f'절대 혐기성(O₂ 에 못 삶 · 발효 · 무기호흡만) ↔ 조건부 혐기성(호흡 · 발효 둘 다 · 발효 땐 당을 더 씀) · 무기호흡(ETC 를 씀 · 최종 수용체가 O₂ 아님) 전용 {B} — L31c s8. 흰 방울 = O₂(L32a s12).',
}
for k, v in new.items():
    assert k not in R, k
    R[k] = v
out = json.dumps(d, ensure_ascii=False, indent=1)
assert json.loads(out) == d
open(P, 'w', encoding='utf-8').write(out)
print('예약', len(R))
