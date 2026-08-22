# -*- coding: utf-8 -*-
"""바늘 만들 때 쓰는 원문 소품 목록 — 태그와 따옴표를 그대로 보여 준다.
   쓰기: python3 tools/pcprops.py s04p05 s03p01 …"""
import re, sys, os
SK = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'sketchy.html')
s = open(SK, encoding='utf-8').read()
for pid in sys.argv[1:]:
    i = s.index("{id:'%s'" % pid); fi = s.index('f:[', i)
    d = 0; j = i
    while True:
        if s[j] == '{': d += 1
        elif s[j] == '}':
            d -= 1
            if d == 0: break
        j += 1
    print('══', pid)
    for m in re.finditer(r'\[(["\'])((?:[^"\'\\]|\\.)*?)\1', s[fi:j]):
        t = m.group(2)
        if re.match(r'^[A-Z]\d?[A-Z0-9]*-', t): continue
        print('   %s%s%s' % (m.group(1), t[:64], m.group(1)))
