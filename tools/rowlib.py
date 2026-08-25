# -*- coding: utf-8 -*-
"""사실표 행을 다루는 공통 도구. s 는 sketchy.html 전체 문자열."""
import re

def close_brace(t, i):
    open_c = t[i]; close_c = '}' if open_c == '{' else ']'
    d = 0; q = None; esc = False
    for k in range(i, len(t)):
        c = t[k]
        if q:
            if esc: esc = False
            elif c == '\\': esc = True
            elif c == q: q = None
            continue
        if c in '"\'`': q = c; continue
        if c == open_c: d += 1
        elif c == close_c:
            d -= 1
            if d == 0: return k
    raise Exception('닫는 괄호를 못 찾았다 at %d' % i)

def panel_span(s, pid):
    h = "{id:'" + pid + "'"
    i = s.index(h)
    return i, close_brace(s, i)

def _rows(blk):
    """(ob, fe, inner, pos) — f:[ 의 여는 대괄호 위치, 닫는 위치, 안쪽 문자열, 최상위 행 구간들"""
    fi = blk.index('f:['); ob = fi + 2; fe = close_brace(blk, ob)
    inner = blk[ob + 1:fe]
    pos = []; d = 0; q = None; esc = False; st = None
    for k, c in enumerate(inner):
        if q:
            if esc: esc = False
            elif c == '\\': esc = True
            elif c == q: q = None
            continue
        if c in '"\'`': q = c; continue
        if c == '[':
            if d == 0: st = k
            d += 1
        elif c == ']':
            d -= 1
            if d == 0: pos.append((st, k))
    return ob, fe, inner, pos

def get_rows(s, pid):
    i, e = panel_span(s, pid); blk = s[i:e + 1]
    ob, fe, inner, pos = _rows(blk)
    return [inner[a:b + 1] for a, b in pos]

def _q(t):
    """행 문자열에 넣을 따옴표 문자열을 만든다 — 큰따옴표를 쓰되 안에 있으면 이스케이프."""
    return '"' + t.replace('\\', '\\\\').replace('"', '\\"') + '"'

def append_row(s, pid, prop, fact, cards):
    """판 끝에 행 하나를 붙인다."""
    i, e = panel_span(s, pid); blk = s[i:e + 1]
    ob, fe, inner, pos = _rows(blk)
    row = '[' + _q(prop) + ',' + _q(fact)
    if cards: row += ',[' + ','.join(_q(c) for c in cards) + ']'
    row += ']'
    new_inner = (inner.rstrip() + ',' + row) if inner.strip() else row
    return s[:i] + blk[:ob + 1] + new_inner + blk[fe:] + s[e + 1:]

def edit_row(s, pid, n, fn=None, prop=None, fact=None):
    """n 번째 행의 카드 목록을 fn 으로 바꾸거나 / 소품·사실 글을 바꾼다."""
    i, e = panel_span(s, pid); blk = s[i:e + 1]
    ob, fe, inner, pos = _rows(blk)
    assert n < len(pos), (pid, n, len(pos))
    a, b = pos[n]; row = inner[a:b + 1]
    m = re.search(r',\s*\[([^\]]*)\]\s*\]$', row)
    old = [x.strip().strip('"').strip("'") for x in (m.group(1).split(',') if m else []) if x.strip()]
    new = fn(list(old)) if fn else old
    body = row[:m.start()] if m else row[:-1]
    if prop is not None or fact is not None:
        # body = [ "소품","사실"   — 앞의 두 토막을 다시 쓴다
        parts = _split_top(body[1:])
        if prop is not None: parts[0] = _q(prop)
        if fact is not None: parts[1] = _q(fact)
        body = '[' + ','.join(parts)
    nr = body + ((',[' + ','.join(_q(c) for c in new) + ']]') if new else ']')
    if nr == row: return s, False, new
    s2 = s[:i] + blk[:ob + 1] + inner[:a] + nr + inner[b + 1:] + blk[fe:] + s[e + 1:]
    return s2, True, new

def _split_top(t):
    """대괄호를 벗긴 행 안쪽을 최상위 쉼표로 자른다."""
    out = []; d = 0; q = None; esc = False; st = 0
    for k, c in enumerate(t):
        if q:
            if esc: esc = False
            elif c == '\\': esc = True
            elif c == q: q = None
            continue
        if c in '"\'`': q = c; continue
        if c in '[{': d += 1
        elif c in ']}': d -= 1
        elif c == ',' and d == 0:
            out.append(t[st:k]); st = k + 1
    out.append(t[st:])
    return out
