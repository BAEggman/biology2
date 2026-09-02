# -*- coding: utf-8 -*-
"""도해 판의 svg 를 png 로 뽑는다 — 눈으로 열어 판정하기 위한 도구."""
import sys, io, re, os
import cairosvg

def dump(pid, width=1320):
    s = io.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'sketchy.html'), encoding='utf-8').read()
    i = s.find("{id:'%s'" % pid)
    assert i > 0, pid
    import sys as _s; _s.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from rowlib import close_brace
    seg = s[i:close_brace(s, i) + 1]
    m = re.search(r"svg:`", seg)
    if not m:
        print('svg 없음:', pid); return None, []
    a = m.end(); b = seg.find('`', a)
    svg = seg[a:b]
    p = '/tmp/%s.svg' % pid
    io.open(p, 'w', encoding='utf-8').write(svg)
    png = '/tmp/%s.png' % pid
    cairosvg.svg2png(url=p, write_to=png, output_width=width, background_color='#fdf8ef')
    texts = [re.sub(r'<[^>]+>', '', t) for t in re.findall(r'<text\b[^>]*>([\s\S]*?)</text>', svg)]
    return png, texts

if __name__ == '__main__':
    for pid in sys.argv[1:]:
        png, texts = dump(pid)
        print('==', pid, '→', png, '· text', len(texts))
        print(' | '.join(texts))
