#!/usr/bin/env python3
"""모든 HTML의 공통 CSS/JS 캐시 버전을 통일한다. 사용법: python scripts/bump_css.py 20261025-hub1"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ver = sys.argv[1]
n = 0
for p in ROOT.rglob('*.html'):
    if '.git' in p.parts:
        continue
    s = p.read_text(encoding='utf-8')
    t = re.sub(r'((?:hub|v4-1-final)\.css|(?:site|guide)\.js)\?v=[\w-]+', lambda m:m.group(1) + '?v=' + ver, s)
    if t != s:
        p.write_text(t, encoding='utf-8', newline='')
        n += 1
print('bumped', n, '->', ver)
