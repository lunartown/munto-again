# 소모임 커뮤니티 후기 수집기

소모임(및 취미 모임) 관련 커뮤니티 글을 대량으로 모아 JSONL로 적재하는 스크래퍼.
목적: 앱스토어 리뷰(앱 기능 불만)엔 없는, **감정·경험이 담긴 실제 모임 후기**를 확보.

## 왜 이 방식인가
- 앱스토어 리뷰: 대량이지만 "채팅 왜 없앴냐/알림/결제" 등 앱 기능 불만 위주라 모임 경험 신호가 약함 → 목적에 부적합.
- 사이트 내부 검색: "소모임"이 흔한 부분문자열("공소취소모임" 등)이라 정치 노이즈가 많음 → 관련성 필터로 컷.
- fmkorea 등 안티봇 사이트: Python 직접 요청은 403/빈본문 → **브라우저 경유 폴백**이 필요(현재 스크래퍼엔 미포함).

## 사이트 어댑터
| 사이트 | 검색 | 본문 | 댓글 |
|---|---|---|---|
| dogdrip(개드립) | `index.php?mid=dogdrip&search_target=title_content` | `.xe_content`(첫 요소) | `.comment .xe_content` ✅ |
| nate(네이트판) | `pann.nate.com/search/talk` → 본문은 `m.pann` | `.view-wrap` | AJAX라 미수집 |
| dcinside | `search.dcinside.com/post/p/{page}/q/` | `.write_div` | AJAX라 미수집 |

## 사용
```bash
python -m venv venv && source venv/bin/activate
pip install requests beautifulsoup4 lxml

python scraper.py --sites dogdrip,nate,dcinside --pages 8   # 수집(이어붙임)
python scraper.py --stats                                   # 누적 현황
```

## 출력
`data/records.jsonl` — 1줄 1글. 필드: `site, url, title, body, comments[], date, score, query`.
- `url` 기준 중복 제거(재실행 시 이어붙임).
- `score`: 관련성 신호어 매칭 수(높을수록 모임 후기일 확률↑). 후처리 필터에 활용.

## 한계 / 다음
- 관련성 필터는 키워드 기반이라 잔여 노이즈(동호회 일반 썰 등) 있음 → `score`로 2차 필터.
- 네이트판 본문은 머리말/꼬리말 제거가 휴리스틱이라 일부 지저분할 수 있음.
- theqoo·fmkorea·다음카페 추가 시 브라우저 폴백 어댑터 필요.
