#!/usr/bin/env python3
"""소모임 커뮤니티 후기 대량 수집기.

사이트별 어댑터: 검색 → 글 URL 목록 → 본문/댓글 파싱 → 관련성 필터 → JSONL 적재.
- 결과: data/records.jsonl (1줄 1글, url 기준 중복 제거, 재실행 시 이어붙임)
- fmkorea 등 안티봇(403/빈본문) 사이트는 browser 폴백 대상이라 여기서 제외.

사용:
    python scraper.py --sites dogdrip,nate,dcinside --pages 3
    python scraper.py --stats
"""
import argparse, json, os, re, time, sys
import requests, urllib.parse as up
from bs4 import BeautifulSoup

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")
OUT = os.path.join(DATA, "records.jsonl")
UA = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/126.0 Safari/537.36",
    "Accept-Language": "ko-KR,ko;q=0.9",
}
DELAY = 0.7          # 요청 간 대기(초) — 사이트 부담/차단 방지
TIMEOUT = 15
QUERY = "소모임"

# 관련성: '소모임' 포함 + 아래 신호어가 2개 이상. 정치/뉴스 노이즈는 신호어가 거의 없어 걸러짐.
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
    return score >= 2, score


def sess():
    s = requests.Session(); s.headers.update(UA); return s


def clean(el):
    if not el:
        return ""
    return re.sub(r"\n{3,}", "\n\n", el.get_text("\n", strip=True)).strip()


# ---------- adapters ----------
def dogdrip_search(s, page):
    url = (f"https://www.dogdrip.net/index.php?mid=dogdrip"
           f"&search_target=title_content&search_keyword={up.quote(QUERY)}&page={page}")
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
    date = ""
    d = soup.select_one(".date, .ed_time, time")
    if d: date = d.get_text(strip=True)
    return dict(title=title, body=body, comments=[c for c in comments if c], date=date)


def dcinside_search(s, page):
    url = f"https://search.dcinside.com/post/p/{page}/q/{up.quote(QUERY)}"
    r = s.get(url, timeout=TIMEOUT); soup = BeautifulSoup(r.text, "lxml")
    return list({a["href"] for a in soup.select("a[href]") if "board/view" in a["href"]})


def dcinside_post(s, url):
    r = s.get(url, timeout=TIMEOUT); soup = BeautifulSoup(r.text, "lxml")
    title = ""
    t = soup.select_one(".title_subject, .title_headtext, .gallview_head .title")
    if t: title = t.get_text(strip=True)
    if not title and soup.title: title = soup.title.get_text(strip=True).split(" - ")[0]
    body = clean(soup.select_one(".write_div"))
    date = ""
    d = soup.select_one(".gall_date")
    if d: date = d.get("title") or d.get_text(strip=True)
    return dict(title=title, body=body, comments=[], date=date)  # dc 댓글은 AJAX라 스킵


def nate_search(s, page):
    url = f"https://pann.nate.com/search/talk?q={up.quote(QUERY)}&page={page}"
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
    return dict(title=title, body=body, comments=[], date="")


ADAPTERS = {
    "dogdrip":  (dogdrip_search, dogdrip_post),
    "dcinside": (dcinside_search, dcinside_post),
    "nate":     (nate_search, nate_post),
}


def load_seen():
    seen = set()
    if os.path.exists(OUT):
        for line in open(OUT, encoding="utf-8"):
            try: seen.add(json.loads(line)["url"])
            except Exception: pass
    return seen


def run(sites, pages):
    os.makedirs(DATA, exist_ok=True)
    seen = load_seen()
    s = sess()
    added = {}
    with open(OUT, "a", encoding="utf-8") as f:
        for site in sites:
            search, post = ADAPTERS[site]
            added[site] = 0
            urls = []
            for p in range(1, pages + 1):
                try:
                    urls += search(s, p)
                except Exception as e:
                    print(f"[{site}] search p{p} ERR {e}", file=sys.stderr)
                time.sleep(DELAY)
            urls = [u for u in dict.fromkeys(urls) if u not in seen]
            print(f"[{site}] 후보 {len(urls)}건 파싱…")
            for u in urls:
                try:
                    rec = post(s, u)
                except Exception as e:
                    print(f"[{site}] post ERR {u[:50]} {e}", file=sys.stderr); continue
                time.sleep(DELAY)
                ok, score = is_relevant(rec.get("title",""), rec.get("body",""))
                if not ok or len(rec.get("body","")) < 20:
                    continue
                rec.update(site=site, url=u, score=score, query=QUERY)
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


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--sites", default="dogdrip,nate,dcinside")
    ap.add_argument("--pages", type=int, default=2)
    ap.add_argument("--stats", action="store_true")
    a = ap.parse_args()
    if a.stats:
        stats()
    else:
        run([x for x in a.sites.split(",") if x in ADAPTERS], a.pages)
