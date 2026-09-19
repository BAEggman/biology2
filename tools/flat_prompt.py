#!/usr/bin/env python3
import sys
t=open(sys.argv[1],encoding='utf-8').read()
body=t.split('-'*70,1)[1].lstrip('-').strip()
print(' '.join(l.strip() for l in body.splitlines() if l.strip()))
