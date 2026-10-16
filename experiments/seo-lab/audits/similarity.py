#!/usr/bin/env python3
"""지역 페이지 표본의 쌍별 본문 유사도 측정 (오프라인, 네트워크 요청 없음).

같은 방법을 59man.shop 미리보기와 경쟁사 저장 HTML에 똑같이 적용하기 위한 도구다.

입력
  --pages DIR      HTML 파일이 있는 폴더(하위 폴더 포함)
  --names TSV      (선택) "파일 상대경로<TAB>지역명" 목록. 없으면 경로의 '/{지역명}-선불폰/'에서 추출
  --n 20 --seed 20261016   무작위 표본 크기와 고정 시드

측정 방법 (모두 결과 JSON에 기록)
  1. 텍스트 추출: <script>, <style>, <header>, <footer>, <nav>, <aside> 제거 후 태그 제거
  2. 구역 분리: title / h1 / 본문(main 또는 body)
  3. 지역명 제거: 각 문서의 지역명을 '@'로 치환 (시도·시군구 이름은 --strip 으로 추가 가능)
  4. 정규화: 공백 전부 제거
  5. 유사도: 문자 6-gram 집합의 Jaccard, 표본 내 모든 쌍
  6. 두 가지 값을 함께 보고
     - raw: 본문 전체
     - boilerplate_removed: 표본 문서의 80% 이상에 똑같이 나오는 문장을 제거한 뒤
"""
import argparse, glob, html, itertools, json, os, random, re, statistics, sys

DROP = re.compile(r"<(script|style|header|footer|nav|aside)\b.*?</\1>", re.S | re.I)
SENT = re.compile(r"(?<=[.!?。])\s+|\n+")


def text(fragment):
    t = re.sub(r"<[^>]+>", " ", fragment)
    return re.sub(r"\s+", " ", html.unescape(t)).strip()


def extract(raw):
    title = re.search(r"<title[^>]*>(.*?)</title>", raw, re.S | re.I)
    h1 = re.search(r"<h1[^>]*>(.*?)</h1>", raw, re.S | re.I)
    body = re.search(r"<main\b.*?</main>", raw, re.S | re.I) or re.search(r"<body\b.*?</body>", raw, re.S | re.I)
    b = DROP.sub(" ", body.group(0) if body else raw)
    b = re.sub(r"<h1[^>]*>.*?</h1>", " ", b, flags=re.S | re.I)  # H1은 따로 측정
    return {"title": text(title.group(1)) if title else "", "h1": text(h1.group(1)) if h1 else "", "body": text(b)}


def shingles(s, n=6):
    s = re.sub(r"\s", "", s)
    return {s[i:i + n] for i in range(max(0, len(s) - n + 1))}


def jaccard(a, b):
    if not a or not b:
        return None  # 한쪽이라도 비어 있으면 측정 불가 (0으로 표시하지 않음)
    return len(a & b) / len(a | b)


def summary(vals):
    skipped = sum(v is None for v in vals)
    vals = [v for v in vals if v is not None]
    if not vals:
        return {"mean": None, "note": "측정 불가: 비교할 텍스트가 없음", "pairs": 0, "skipped_pairs": skipped}
    return {"skipped_pairs": skipped, "mean": round(statistics.mean(vals), 3), "median": round(statistics.median(vals), 3),
            "min": round(min(vals), 3), "max": round(max(vals), 3), "pairs": len(vals)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pages", required=True)
    ap.add_argument("--names")
    ap.add_argument("--n", type=int, default=20)
    ap.add_argument("--seed", type=int, default=20261016)
    ap.add_argument("--strip", nargs="*", default=[], help="추가로 제거할 단어(시도명 등)")
    ap.add_argument("--exclude", default="hub", help="경로에 이 문자열이 있으면 제외")
    ap.add_argument("--out")
    a = ap.parse_args()

    root = os.path.abspath(a.pages)
    files = sorted(os.path.relpath(f, root) for f in glob.glob(os.path.join(root, "**", "*.html"), recursive=True))
    if a.exclude:
        files = [f for f in files if a.exclude not in f]
    names = {}
    if a.names:
        for line in open(a.names, encoding="utf-8"):
            if "\t" in line:
                k, v = line.rstrip("\n").split("\t", 1)
                names[k] = v
    else:
        for f in files:
            m = re.search(r"([^/\\]+)-선불폰[/\\]", f.replace("\\", "/") + "/")
            if m:
                names[f] = m.group(1)
    files = [f for f in files if f in names]
    if len(files) < 2:
        sys.exit("측정 가능한 문서가 2개 미만입니다 (지역명 매핑 확인)")
    rnd = random.Random(a.seed)
    sample = sorted(rnd.sample(files, min(a.n, len(files))))

    docs = {}
    for f in sample:
        d = extract(open(os.path.join(root, f), encoding="utf-8", errors="replace").read())
        for w in [names[f]] + a.strip:
            if w:
                d = {k: v.replace(w, "@") for k, v in d.items()}
        docs[f] = d

    # 표본의 80% 이상에서 동일하게 등장하는 문장 = 구조 공통 문장
    sent_sets = {f: {s.strip() for s in SENT.split(d["body"]) if len(s.strip()) >= 8} for f, d in docs.items()}
    counts = {}
    for ss in sent_sets.values():
        for s in ss:
            counts[s] = counts.get(s, 0) + 1
    threshold = max(2, int(0.8 * len(sample) + 0.999))
    boiler = {s for s, c in counts.items() if c >= threshold}

    def strip_boiler(body):
        return " ".join(s for s in SENT.split(body) if s.strip() not in boiler)

    res = {}
    for part in ["title", "h1", "body"]:
        sh = {f: shingles(d[part]) for f, d in docs.items()}
        res[part] = summary([jaccard(sh[x], sh[y]) for x, y in itertools.combinations(sample, 2)])
    shb = {f: shingles(strip_boiler(d["body"])) for f, d in docs.items()}
    res["body_boilerplate_removed"] = summary([jaccard(shb[x], shb[y]) for x, y in itertools.combinations(sample, 2)])

    lens = [len(re.sub(r"\s", "", d["body"])) for d in docs.values()]
    lens_b = [len(re.sub(r"\s", "", strip_boiler(d["body"]))) for d in docs.values()]
    report = {
        "method": {"shingle": "char 6-gram, whitespace removed", "metric": "Jaccard, all pairs",
                   "name_replacement": "region name -> '@'", "extra_strip": a.strip,
                   "boilerplate_rule": f"sentence (>=8 chars) identical in >= {threshold}/{len(sample)} sampled docs",
                   "excluded_tags": "script, style, header, footer, nav, aside; h1 measured separately"},
        "input": {"pages_dir": a.pages, "files_found": len(files), "seed": a.seed, "n": len(sample)},
        "sample": [{"file": f, "name": names[f]} for f in sample],
        "similarity": res,
        "body_chars": {"raw_mean": round(statistics.mean(lens)), "boilerplate_removed_mean": round(statistics.mean(lens_b))},
        "boilerplate_sentences": len(boiler),
        "docs_with_no_unique_body": sum(1 for x in lens_b if x == 0),
    }
    out = json.dumps(report, ensure_ascii=False, indent=2)
    if a.out:
        open(a.out, "w", encoding="utf-8").write(out + "\n")
    print(out)


if __name__ == "__main__":
    main()
