#!/usr/bin/env python3
# reserve_L07f.py — 새 과 L07f(갑상선 공장의 뒤뜰 — 고장 난 날들)
import json
P = '/tmp/b2/tools/hooks.json'
txt = open(P, encoding='utf-8').read(); d = json.loads(txt)
assert json.dumps(d, ensure_ascii=False, indent=1) == txt
R = d['_심볼예약']
T = '[2026-11-11 새 과 L07f]'
new = {
 '햇볕에도 목도리에 하품하는 통통한 사람 / 땀에 젖어 부채질하는 깡마른 사람': f'갑상샘기능저하(무기력 · 체중 ↑ · 추위) / 항진(대사 ↑ · 체중 ↓ · 더위) 전용 {T} — L07f s2.',
 '크레용 낙서뿐인 키 작은 아기': f'크레틴병(영유아 갑상샘기능저하 → 발달 장애) 전용 {T} — L07f s3. 크레용 = 크레틴.',
 '묘비 뒤 유령이 가짜 나비 판으로 누르는 초인종 스위치 + 시커먼 굴뚝 연기': f'그레이브스병(TSH 수용체 자가항체 → 계속 자극 · T3 · T4 ↑ · TSH ↓) 전용 {T} — L07f s5. 묘비 = grave. 나비 판 = TSH(L07b · L07e 의 그 판).',
 '빈 덤프트럭 + 나비 판 전령 떼에 풍선처럼 부푼 헛간': f'갑상샘종(요오드 부족 → 음성 피드백 풀림 → TSH 과다 → 비대) 전용 {T} — L07f s6.',
 '자갈 둘뿐인 바구니 + 갈퀴처럼 굳어 떠는 손': f'저칼슘혈증 → 테타니(강직성 경련) 전용 {T} — L07f s7.',
 '넘친 자갈이 빨간 머리 성냥개비와 엉겨 굳은 흰 껍데기가 막은 관': f'고칼슘혈증 → 인산칼슘 침전 → 조직 · 기관 손상 전용 {T} — L07f s8. 성냥개비 = 인산(【불 안 붙은 빨간 머리 성냥개비】).',
}
for k, v in new.items():
    assert k not in R, k
    R[k] = v
def add(key, note):
    v = R[key]; assert isinstance(v, str), key
    R[key] = v + ' ' + note
add('장난감 병정(작은 나무 인형 병사)', f'★ {T} L07f s4 망치로 제 공장(갑상선) 벽돌을 빼내는 병정 = 자가면역 파괴(하시모토병).')
add('자갈', f'★ {T} L07f s7 자갈 둘뿐인 바구니(저칼슘 → 테타니) · s8 넘친 자갈 + 성냥개비의 흰 껍데기(고칼슘 → 인산칼슘 침전).')
add('불 안 붙은 빨간 머리 성냥개비', f'★ {T} L07f s8 넘친 자갈과 엉겨 관을 막은 흰 껍데기 = 인산칼슘 침전.')
open(P, 'w', encoding='utf-8').write(json.dumps(d, ensure_ascii=False, indent=1))
print('예약', len(R))
