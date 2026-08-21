# -*- coding: utf-8 -*-
"""tools/_<pid>.svg 를 sketchy.html 의 인라인 사본에 그대로 밀어 넣는다.

도해를 고칠 때마다 두 군데를 같이 고쳐야 하는데, 한쪽만 고치면 배포본이 어긋난다.
파일 쪽을 원본으로 삼고 이 스크립트로 맞춘다.   사용: python3 tools/sync_svg.py d01p03 [d05p01 …]
"""
import os, sys
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SK = os.path.join(ROOT, 'sketchy.html')

def sync(pid):
    src = open(os.path.join(ROOT, 'tools', '_%s.svg' % pid), encoding='utf-8').read().strip()
    assert src.startswith('<svg'), pid + ' 가 <svg 로 시작하지 않는다'
    assert '`' not in src, pid + ' 안에 백틱이 있다 — 템플릿 리터럴이 깨진다'
    k = open(SK, encoding='utf-8').read()
    i = k.index("{id:'%s'" % pid)
    a = k.index('svg:`', i) + 5
    b = k.index('`', a)
    old = k[a:b]
    assert old.lstrip().startswith('<svg'), pid + ' 의 svg 자리를 잘못 잡았다'
    open(SK, 'w', encoding='utf-8').write(k[:a] + src + k[b:])
    print('  %s  %d → %d자%s' % (pid, len(old), len(src), '' if old.strip() != src else ' (변경 없음)'))

if __name__ == '__main__':
    pids = sys.argv[1:] or [f[1:-4] for f in os.listdir(os.path.join(ROOT, 'tools'))
                            if f.startswith('_d') and f.endswith('.svg')]
    print('sketchy.html 인라인 사본 맞추기')
    for p in sorted(pids): sync(p)
