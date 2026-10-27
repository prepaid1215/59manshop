#!/usr/bin/env python3
"""Review paragraph rhythm across the complete 59man.shop static site.

Split overly long explanatory <p> paragraphs only at *top-level, finished*
sentence boundaries. Keep visible text (including whitespace), links, facts,
images, headings, canonical URLs, and the rest of HTML byte-for-byte identical.
All content HTML pages are examined, including noindex and secondary guides;
non-article navigation, product tables, footnotes, and tool UI are untouched.
"""
from __future__ import annotations
import argparse
import html
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parent.parent
ARTICLE = re.compile(r'<article\b[^>]*>[\s\S]*?</article>', re.I)
PARA = re.compile(r'(<p(?:\s[^>]*)?>)([\s\S]*?)(</p>)', re.I)
TOKEN = re.compile(r'<[^>]*>|[^<]+', re.S)
TAG = re.compile(r'^<\s*(/?)\s*([a-z][\w:-]*)', re.I)
SENT = re.compile(r'[.!?。！？](?:["”’\')\]]+)?\s+(?=[가-힣A-Za-z0-9“"\'(\[])')
VOID = {'br', 'img', 'hr', 'meta', 'link', 'input', 'source', 'wbr', 'area'}
MAX_CHARS = 108
TARGET_CHARS = 76
MIN_CHARS = 28
SKIP_CLASSES = ('step-', 'reader-toc', 'gc-', 'sm-ai-caption', 'hero-', 'member-')

def visible(s: str) -> str:
    return html.unescape(re.sub(r'<[^>]*>', '', s, flags=re.S))

def meaningful(s: str) -> int:
    return len(re.sub(r'\s+', '', visible(s)))

def safe_breaks(inner: str) -> list[int]:
    """Choose sentence endings outside strong/span/a and other inline markup."""
    result = []
    nesting = []
    for match in TOKEN.finditer(inner):
        token = match.group()
        if token.startswith('<'):
            parsed = TAG.match(token)
            if parsed:
                close, name = parsed.groups()
                name = name.lower()
                if close:
                    if nesting and nesting[-1] == name:
                        nesting.pop()
                    elif name in nesting:
                        nesting = nesting[:nesting.index(name)]
                elif name not in VOID and not token.rstrip().endswith('/>') and not token.startswith('<!'):
                    nesting.append(name)
            continue
        if nesting:
            continue
        for found in SENT.finditer(token):
            pos = match.start() + found.end()
            if not inner[pos:].strip():
                continue
            result.append(pos)
    return result

def reflow(open_p: str, inner: str, close_p: str) -> tuple[str, int]:
    if meaningful(inner) <= MAX_CHARS:
        return open_p + inner + close_p, 0
    if any(cls in open_p for cls in SKIP_CLASSES) or re.search(r'\b(?:id|contenteditable|role)\s*=', open_p):
        return open_p + inner + close_p, 0
    points = safe_breaks(inner)
    start = 0
    chunks = []
    while meaningful(inner[start:]) > MAX_CHARS:
        candidates = []
        for end in points:
            if end <= start:
                continue
            size = meaningful(inner[start:end])
            remain = meaningful(inner[end:])
            if MIN_CHARS <= size <= MAX_CHARS and remain >= MIN_CHARS:
                candidates.append((abs(size-TARGET_CHARS), -size, end))
        if not candidates:
            break
        end = min(candidates)[2]
        chunks.append(inner[start:end])
        start = end
    if not chunks:
        return open_p + inner + close_p, 0
    chunks.append(inner[start:])
    # Never alter even a single character of textual content.
    if ''.join(chunks) != inner:
        raise AssertionError('split lost text')
    output = open_p + chunks[0] + close_p
    for chunk in chunks[1:]:
        output += '<p class="reader-breath">' + chunk + '</p>'
    if visible(inner) != ''.join(visible(c) for c in chunks):
        raise AssertionError('visible text mismatch')
    return output, len(chunks)-1

def transform_article(article: str) -> tuple[str, int]:
    count = [0]
    def sub(match: re.Match) -> str:
        revised, added = reflow(*match.groups())
        count[0] += added
        return revised
    changed = PARA.sub(sub, article)
    if visible(article) != visible(changed):
        raise AssertionError('article visible text changed')
    if re.findall(r'href="([^"]+)"', article) != re.findall(r'href="([^"]+)"', changed):
        raise AssertionError('article href changed')
    if re.findall(r'<h[1-6]\b[^>]*>[\s\S]*?</h[1-6]>', article, re.I) != re.findall(r'<h[1-6]\b[^>]*>[\s\S]*?</h[1-6]>', changed, re.I):
        raise AssertionError('headings changed')
    return changed, count[0]

def run(write: bool) -> int:
    paths = sorted(p for p in ROOT.rglob('index.html') if '.git' not in p.parts)
    audited = modified = added = initial_long = remaining_long = 0
    details = []
    for path in paths:
        rel = path.relative_to(ROOT).as_posix()
        source = path.read_text('utf-8')
        match = ARTICLE.search(source)
        if not match:
            details.append({'path':rel,'article':False,'added':0})
            continue
        audited += 1
        art = match.group()
        old_p = [m.group(2) for m in PARA.finditer(art)]
        initial_long += sum(meaningful(s)>MAX_CHARS for s in old_p)
        fresh,n = transform_article(art)
        new_p = [m.group(2) for m in PARA.finditer(fresh)]
        remaining_long += sum(meaningful(s)>MAX_CHARS for s in new_p)
        final = source[:match.start()] + fresh + source[match.end():]
        if final != source:
            modified += 1
            if write:
                path.write_text(final,encoding='utf-8')
        added += n
        details.append({'path':rel,'paragraphs':len(old_p),'long_before':sum(meaningful(s)>MAX_CHARS for s in old_p),'long_after':sum(meaningful(s)>MAX_CHARS for s in new_p),'added':n})
    summary={'mode':'write' if write else 'audit','html_pages':len(paths),'articles_audited':audited,'article_files_changed':modified,'paragraphs_inserted':added,'long_paragraphs_before':initial_long,'long_paragraphs_after':remaining_long,'per_page':details}
    print(json.dumps(summary,ensure_ascii=False,indent=2))
    # If a paragraph can't be safely split, report but don't force broken grammar.
    return 0

if __name__ == '__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--write',action='store_true')
    options=p.parse_args()
    sys.exit(run(options.write))
