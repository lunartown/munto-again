#!/usr/bin/env python3
"""소모임 커뮤니티 후기 대량 수집기.

사이트별 어댑터: 검색 → 글 URL 목록 → 본문/댓글 파싱 → 관련성 필터 → JSONL 적재.
- 결과: data/records.jsonl (1줄 1글, url 기준 중복 제거, 재실행 시 이어붙임)
- 검색 미리보기는 저장하지 않고, 원문을 직접 가져올 수 있는 사이트만 지원.

사용:
    python scraper.py --sites dogdrip,nate,dcinside --pages 3
    python scraper.py --stats
"""
import argparse, csv, json, os, re, time, sys
import requests, urllib.parse as up
from bs4 import BeautifulSoup

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
OUT = os.path.join(DATA, "records.jsonl")
CSV_OUT = os.path.join(DATA, "records.csv")
UA = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/126.0 Safari/537.36",
    "Accept-Language": "ko-KR,ko;q=0.9",
}
DELAY = 0.5          # 요청 간 대기(초) — 사이트 부담/차단 방지
TIMEOUT = 15
DEFAULT_QUERIES = ["소모임"]

# 관련성: '소모임/동호회' 포함 + 아래 신호어가 1개 이상. 수집 후 사람이 직접 걸러내는 전제.
SIGNAL = ["동호회","정모","모임장","가입","성비","나갔","나가","후기","친목","어플","앱",
          "멤버","활동","벙","번개","취미","여미새","남미새","탈퇴","복불복","당근"]
NOISE_TITLE = ["밀레이","법무장관","용혜인","공소취소","대통령","트럼프","개각","장관 지명"]


def is_relevant(title, body):
    text = f"{title}\n{body}"
    if "소모임" not in text and "동호회" not in text:
        return False, 0
    if any(n in title for n in NOISE_TITLE):
        return False, 0
    score = sum(1 for k in SIGNAL if k in text)
    return score >= 1, score  # 문턱 낮춤: 노이즈는 수집 후 직접 읽고 필터


def sess():
    s = requests.Session(); s.headers.update(UA); return s


def clean(el):
    if not el:
        return ""
    return re.sub(r"\n{3,}", "\n\n", el.get_text("\n", strip=True)).strip()


DATE_RE = re.compile(r"(20\d{2})[.\-/](\d{1,2})[.\-/](\d{1,2})(?:\s+(\d{1,2}):(\d{2})(?::(\d{2}))?)?")


def normalize_date(value):
    """사이트별 날짜 표기를 시간 정밀도를 보존한 ISO 유사 형식으로 통일한다."""
    match = DATE_RE.search(value or "")
    if not match:
        return ""
    year, month, day, hour, minute, second = match.groups()
    result = f"{year}-{int(month):02d}-{int(day):02d}"
    if hour is not None:
        result += f" {int(hour):02d}:{minute}"
    if second is not None:
        result += f":{second}"
    return result


def first_date(soup, selectors):
    """선택자에 걸린 요소 중 실제 날짜 문자열이 있는 첫 값을 반환한다."""
    for selector in selectors:
        for element in soup.select(selector):
            date = normalize_date(element.get("title") or element.get_text(" ", strip=True))
            if date:
                return date
    return ""


# ---------- adapters ----------
def dogdrip_search(s, page, query):
    url = (f"https://www.dogdrip.net/index.php?mid=dogdrip"
           f"&search_target=title_content&search_keyword={up.quote(query)}&page={page}")
    r = s.get(url, timeout=TIMEOUT); soup = BeautifulSoup(r.text, "lxml")
    ids = set()
    for a in soup.select("a[href]"):
        m = re.search(r"/(\d{6,})(?:\?|$)", a["href"])
        if m:
            ids.add(m.group(1))
    return [f"https://www.dogdrip.net/{i}" for i in ids]


def dogdrip_post(s, url):
    r = s.get(url, timeout=TIMEOUT); soup = BeautifulSoup(r.text, "lxml")
    title = (soup.title.get_text(strip=True) if soup.title else "").split(" - DogDrip")[0]
    bodies = soup.select(".xe_content")
    comments = [clean(c) for c in soup.select(".comment .xe_content")]
    body = clean(bodies[0]) if bodies else ""
    date = first_date(soup, [".article-head .text-muted", ".date", ".ed_time", "time"])
    return dict(title=title, body=body, comments=[c for c in comments if c], date=date)


def dcinside_search(s, page, query):
    url = f"https://search.dcinside.com/post/p/{page}/q/{up.quote(query)}"
    r = s.get(url, timeout=TIMEOUT); soup = BeautifulSoup(r.text, "lxml")
    return list({a["href"] for a in soup.select("a[href]") if "board/view" in a["href"]})


def dcinside_post(s, url):
    r = s.get(url, timeout=TIMEOUT); soup = BeautifulSoup(r.text, "lxml")
    title = ""
    t = soup.select_one(".title_subject, .title_headtext, .gallview_head .title")
    if t: title = t.get_text(strip=True)
    if not title and soup.title: title = soup.title.get_text(strip=True).split(" - ")[0]
    body = clean(soup.select_one(".write_div"))
    date = first_date(soup, [".gall_date"])
    return dict(title=title, body=body, comments=[], date=date)  # dc 댓글은 AJAX라 스킵


def nate_search(s, page, query):
    url = f"https://pann.nate.com/search/talk?q={up.quote(query)}&page={page}"
    r = s.get(url, timeout=TIMEOUT); soup = BeautifulSoup(r.text, "lxml")
    ids = {m.group(1) for a in soup.select("a[href]")
           if (m := re.search(r"/talk/(\d+)", a.get("href", "")))}
    return [f"https://m.pann.nate.com/talk/{i}" for i in ids]  # 모바일=서버렌더


def og(soup, prop):
    m = soup.find("meta", property=f"og:{prop}")
    return (m.get("content") if m else "") or ""


def nate_post(s, url):
    r = s.get(url, timeout=TIMEOUT); soup = BeautifulSoup(r.text, "lxml")
    title = og(soup, "title").split(" | 네이트")[0].strip()
    if not title and soup.title:
        title = soup.title.get_text(strip=True).split(" |")[0]
    body = ""
    wrap = soup.select_one(".view-wrap")
    if wrap:
        txt = wrap.get_text("\n", strip=True)
        # 앞의 제목/날짜 머리말과 뒤의 '태그/베스트' 꼬리말 잘라내기
        txt = re.split(r"\n태그\n|\n베스트\n", txt)[0]
        if title and title in txt:
            txt = txt.split(title, 1)[-1]
        txt = re.sub(r"^[\s\S]{0,40}?\d{4}\.\d{2}\.\d{2}[^\n]*\n", "", txt, count=1)
        body = re.sub(r"\n{3,}", "\n\n", txt).strip()
    if len(body) < 20:
        body = og(soup, "description").split(":", 1)[-1].strip()
    date = first_date(soup, [".pann-title .sub .num", ".pann-title .writer .num"])
    return dict(title=title, body=body, comments=[], date=date)


def theqoo_search(s, page, query):
    # 더쿠에는 공개 전역검색이 없어 네이버 View 검색을 URL 발견용으로만 사용한다.
    if page != 1:
        return []
    discovery_query = f'site:theqoo.net/review "{query}"'
    url = ("https://search.naver.com/search.naver?where=view&query=" +
           up.quote(discovery_query))
    r = s.get(url, timeout=TIMEOUT); r.raise_for_status()
    ids = re.findall(r"https?://theqoo\.net/review/(\d+)", r.text)
    return [f"https://theqoo.net/review/{x}" for x in dict.fromkeys(ids)]


def theqoo_post(s, url):
    r = s.get(url, timeout=TIMEOUT); r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")
    title = og(soup, "title").replace("더쿠 - ", "").strip()
    if not title and soup.title:
        title = soup.title.get_text(strip=True).replace("더쿠 - ", "")
    body = clean(soup.select_one(".rd_body .xe_content") or
                 soup.select_one(".xe_content") or
                 soup.select_one(".rd_body"))
    comments = [clean(x) for x in soup.select(".fdb_lst .xe_content")]
    return dict(title=title, body=body,
                comments=[x for x in comments if x],
                date=first_date(soup, [".rd_hd .side", ".date", ".regdate", "time"]),
                source_kind="full_post")


ADAPTERS = {
    "dogdrip":  (dogdrip_search, dogdrip_post),
    "dcinside": (dcinside_search, dcinside_post),
    "nate":     (nate_search, nate_post),
    "theqoo":   (theqoo_search, theqoo_post),
}


def load_seen():
    seen = set()
    if os.path.exists(OUT):
        for line in open(OUT, encoding="utf-8"):
            try: seen.add(json.loads(line)["url"])
            except Exception: pass
    return seen


def run(sites, pages, queries):
    os.makedirs(DATA, exist_ok=True)
    seen = load_seen()
    s = sess()
    added = {}
    with open(OUT, "a", encoding="utf-8") as f:
        for site in sites:
            search, post = ADAPTERS[site]
            added[site] = 0
            urls = []
            url_queries = {}
            for query in queries:
                for p in range(1, pages + 1):
                    try:
                        found = search(s, p, query)
                        urls += found
                        for u in found:
                            url_queries.setdefault(u, query)
                    except Exception as e:
                        print(f"[{site}] search {query!r} p{p} ERR {e}", file=sys.stderr)
                    time.sleep(DELAY)
            urls = [u for u in dict.fromkeys(urls) if u not in seen]
            print(f"[{site}] 후보 {len(urls)}건 파싱…")
            for u in urls:
                try:
                    rec = post(s, u)
                except Exception as e:
                    print(f"[{site}] post ERR {u[:50]} {e}", file=sys.stderr); continue
                if rec.get("source_kind") != "search_preview":
                    time.sleep(DELAY)
                ok, score = is_relevant(rec.get("title",""), rec.get("body",""))
                if not ok or len(rec.get("body","")) < 20:
                    continue
                rec.update(site=site, url=u, score=score,
                           query=url_queries.get(u, ""))
                f.write(json.dumps(rec, ensure_ascii=False) + "\n"); f.flush()
                seen.add(u); added[site] += 1
    total = sum(added.values())
    print("\n=== 수집 결과 ===")
    for site, n in added.items():
        print(f"  {site:9} +{n}")
    print(f"  합계 +{total}  (누적 {len(seen)})  → {OUT}")


def stats():
    if not os.path.exists(OUT):
        print("아직 수집 없음"); return
    by = {}
    n = 0
    for line in open(OUT, encoding="utf-8"):
        n += 1; r = json.loads(line); by[r["site"]] = by.get(r["site"], 0) + 1
    print(f"누적 {n}건")
    for k, v in sorted(by.items()): print(f"  {k:9} {v}")


def refresh_dates():
    """날짜가 비어 있는 저장 레코드만 원문에서 다시 읽어 보충한다."""
    rows = [json.loads(line) for line in open(OUT, encoding="utf-8") if line.strip()]
    s = sess()
    updated = 0
    failed = []
    for row in rows:
        current = normalize_date(str(row.get("date", "")))
        if current:
            row["date"] = current
            continue
        adapter = ADAPTERS.get(row.get("site"))
        if not adapter:
            failed.append(row["url"])
            continue
        try:
            date = adapter[1](s, row["url"]).get("date", "")
        except Exception as exc:
            print(f"[date] ERR {row['url']} {exc}", file=sys.stderr)
            failed.append(row["url"])
            continue
        if date:
            row["date"] = normalize_date(date)
            updated += 1
        else:
            failed.append(row["url"])
        time.sleep(DELAY)
    temp = OUT + ".tmp"
    with open(temp, "w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    os.replace(temp, OUT)
    print(f"날짜 보충 {updated}건, 미확보 {len(failed)}건")
    for url in failed:
        print(f"  {url}")


def export_csv():
    """현재 JSONL 정본을 Excel 호환 UTF-8 CSV로 내보낸다."""
    rows = [json.loads(line) for line in open(OUT, encoding="utf-8") if line.strip()]
    fields = ["site", "date", "title", "body", "comments", "comment_count",
              "url", "score", "query", "source_kind", "access", "retrieved_at"]
    with open(CSV_OUT, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            comments = row.get("comments") or []
            writer.writerow({
                "site": row.get("site", ""),
                "date": normalize_date(str(row.get("date", ""))),
                "title": row.get("title", ""),
                "body": row.get("body", ""),
                "comments": "\n\n---\n\n".join(comments),
                "comment_count": len(comments),
                "url": row.get("url", ""),
                "score": row.get("score", ""),
                "query": row.get("query", ""),
                "source_kind": row.get("source_kind", ""),
                "access": row.get("access", ""),
                "retrieved_at": row.get("retrieved_at", ""),
            })
    print(f"CSV {len(rows)}건 → {CSV_OUT}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--sites", default="dogdrip,nate,dcinside")
    ap.add_argument("--pages", type=int, default=2)
    ap.add_argument("--queries", default=",".join(DEFAULT_QUERIES),
                    help="쉼표로 구분한 검색어")
    ap.add_argument("--stats", action="store_true")
    ap.add_argument("--refresh-dates", action="store_true")
    ap.add_argument("--export-csv", action="store_true")
    a = ap.parse_args()
    if a.refresh_dates:
        refresh_dates()
    elif a.export_csv:
        export_csv()
    elif a.stats:
        stats()
    else:
        run([x for x in a.sites.split(",") if x in ADAPTERS], a.pages,
            [x.strip() for x in a.queries.split(",") if x.strip()])
