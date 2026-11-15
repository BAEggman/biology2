#!/usr/bin/env python3
# gen_sync.py <ID> [<ID> …] [--check] — gen_<ID>.py 의 `L = {…}`(와 `BOX = {…}`)를 지금의 lessons/<ID>.json 으로 다시 쓴다(2026-11-15 · Opus 5.5).
#  왜: 지시서 §4.4 「gen 파일이 있는 과는 그 파일을 고치고 --write」 — 그런데 감사 패치 · 덧붙임이 JSON 을 바로 고친 과가 있었다
#      (L07f · L08a · L08b · L14b · L16d · L48d — L16d · L08a s13 은 차례 3 덧붙임). 그대로 두면 다음 `gen --write` 가 그 고침을 되돌린다.
#  하는 일: ast 로 `L = …` · `BOX = …` 대입문의 자리를 찾아, JSON 의 값으로 바꿔 쓴다(머리 주석 · 검사 · main 은 그대로).
#   · BOX 가 있는 꼴(대부분): L 의 stops 에서 box 를 빼고 BOX 에 sid 별로.  · BOX 가 없는 꼴(L46e 등): box 를 stops 안에 그대로.
#  확인: 다시 읽은 gen 의 L(+BOX)이 JSON 과 같아야 한다(다르면 쓰지 않음). --check = 다른지만 알린다.
import ast, io, json, sys, contextlib, importlib.util

ROOT = '/tmp/b2'


def pv(v):
    if v is None: return 'None'
    if v is True: return 'True'
    if v is False: return 'False'
    return json.dumps(v, ensure_ascii=False)


def fmt_L(J, with_box):
    head = [k for k in J if k != 'stops']
    out = ['L = {']
    for k in head:
        out.append(f' {pv(k)}: {pv(J[k])},')
    out.append(' "stops": [')
    for s in J['stops']:
        keys = [k for k in s if with_box or k != 'box']
        for i, k in enumerate(keys):
            pre = '  {' if i == 0 else '   '
            end = '},' if i == len(keys) - 1 else ','
            out.append(f'{pre}{pv(k)}: {pv(s[k])}{end}')
    out.append(' ]}')
    return '\n'.join(out)


def fmt_BOX(J):
    out = ['BOX = {']
    for s in J['stops']:
        out.append(f" {pv(s['sid'])}: {pv(s.get('box'))},")
    out.append('}')
    return '\n'.join(out)


def load_gen(path):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        spec = importlib.util.spec_from_file_location('g', path); m = importlib.util.module_from_spec(spec)
        argv = sys.argv; sys.argv = [path]
        try: spec.loader.exec_module(m)
        finally: sys.argv = argv
    L = json.loads(json.dumps(m.L, ensure_ascii=False))
    if hasattr(m, 'BOX'):
        for s in L['stops']: s['box'] = m.BOX.get(s['sid'])
    return L


def spans(text):
    t = ast.parse(text); sp = {}
    for n in t.body:
        if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name) and n.targets[0].id in ('L', 'BOX'):
            sp[n.targets[0].id] = (n.lineno - 1, n.end_lineno)
    return sp


def same(a, b):
    return json.dumps(a, ensure_ascii=False, sort_keys=True) == json.dumps(b, ensure_ascii=False, sort_keys=True)


def sync(lid, check):
    gp = f'{ROOT}/tools/prompts/gen_{lid}.py'; jp = f'{ROOT}/lessons/{lid}.json'
    J = json.load(open(jp, encoding='utf-8'))
    before = load_gen(gp)
    if same(before, J): print(lid, '같음'); return 0
    if check: print(lid, '다름'); return 1
    text = open(gp, encoding='utf-8').read(); sp = spans(text); lines = text.split('\n')
    has_box = 'BOX' in sp
    rep = {sp['L']: fmt_L(J, not has_box)}
    if has_box: rep[sp['BOX']] = fmt_BOX(J)
    for (a, b), new in sorted(rep.items(), key=lambda x: -x[0][0]):
        lines[a:b] = new.split('\n')
    new_text = '\n'.join(lines)
    tmp = gp[:-3] + '_sync_tmp.py'
    open(tmp, 'w', encoding='utf-8').write(new_text)
    try:
        after = load_gen(tmp)
    finally:
        import os; os.remove(tmp)
    if not same(after, J): print('✕', lid, '다시 읽은 값이 JSON 과 다르다 — 쓰지 않음'); return 1
    open(gp, 'w', encoding='utf-8').write(new_text); print(lid, '맞춤')
    return 0


if __name__ == '__main__':
    check = '--check' in sys.argv
    bad = sum(sync(a, check) for a in sys.argv[1:] if not a.startswith('--'))
    if bad: raise SystemExit(f'✕ {bad}')
