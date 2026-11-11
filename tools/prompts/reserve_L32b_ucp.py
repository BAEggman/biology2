#!/usr/bin/env python3
# reserve_L32b_ucp.py — 40·41 덧붙임 L32b +1(UCP · 갈색지방)
import json
P = '/tmp/b2/tools/hooks.json'
txt = open(P, encoding='utf-8').read(); d = json.loads(txt)
assert json.dumps(d, ensure_ascii=False, indent=1) == txt
R = d['_심볼예약']
T = '[2026-11-11 40·41 덧붙임 L32b]'
new = {
 '담장에 단정히 박아 넣은 네모난 놋쇠 붙박이 환기구': f'UCP(짝풀림 단백질 · 몸이 제 막에 단 H⁺ 통로 → ATP 대신 열) 전용 {T} — L32b s11. 도깨비 드릴 구멍(DNP · 밖에서 온 약 · 테두리가 벌겋게 단다)과 가른다: 붙박이 판 · 테두리 멀쩡 · 물은 가늘게. ⚠ 다른 판의 환기구 · 통풍구를 놋쇠 판으로 그리지 마라.',
 '갈색 뜨개 담요에 싸여 주황빛 김 속에서 떨지 않고 웃는 아기': f'갈색지방(미토콘드리아 · UCP 많음 · 비떨림 열 발생 · 신생아 · 겨울잠) 전용 {T} — L32b s11. 북극곰 예약(【북극곰】 쌍극세포) 때문에 곰을 쓰지 않았다. ⚠ L46f#5 요람의 갓난아기(미숙아 · 서팩턴트) · L46g 기저귀 아기(HbF) · L51a 횃불 아기(hCG) · L07f 크레용 아기(크레틴)와 가른다 — 이쪽은 갈색 뜨개 담요와 주황빛 김이 표지다.',
}
for k, v in new.items():
    assert k not in R, k
    R[k] = v
def add(key, note):
    v = R[key]; assert isinstance(v, str), key
    R[key] = v + ' ' + note
add('북극곰', f'★ {T} 계획 G1 의 「갈색 털 곰(갈색지방)」은 곰 대신 【갈색 뜨개 담요 아기】로 그렸다(L32b s11).')
open(P, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=1))
print('예약', len(R))
