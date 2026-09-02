# 소모임 커뮤니티 후기 수집기

소모임(및 취미 모임) 관련 커뮤니티 글을 대량으로 모아 JSONL로 적재하는 스크래퍼.
목적: 앱스토어 리뷰(앱 기능 불만)엔 없는, **감정·경험이 담긴 실제 모임 후기**를 확보.

## 왜 이 방식인가
- 앱스토어 리뷰: 대량이지만 "채팅 왜 없앴냐/알림/결제" 등 앱 기능 불만 위주라 모임 경험 신호가 약함 → 목적에 부적합.
- 사이트 내부 검색: "소모임"이 흔한 부분문자열("공소취소모임" 등)이라 정치 노이즈가 많음 → 관련성 필터로 컷.
- 펨코: 네이버 View는 URL 발견에만 사용하고, 발견한 49개 URL을 Chrome에서 직접 열어 원문을 수집함.
- 더쿠: 공개 전역검색이 없어 네이버 View 검색으로 URL만 발견하고, 원문은 더쿠에서 직접 수집함.
- 다음카페: 과거 검색 결과는 URL 발견에만 사용하고, 모바일 원문이 공개된 글만 직접 수집함.

## 사이트 어댑터
| 사이트 | 검색 | 본문 | 댓글 |
|---|---|---|---|
| dogdrip(개드립) | `index.php?mid=dogdrip&search_target=title_content` | `.xe_content`(첫 요소) | `.comment .xe_content` ✅ |
| nate(네이트판) | `pann.nate.com/search/talk` → 본문은 `m.pann` | `.view-wrap` | AJAX라 미수집 |
| dcinside | `search.dcinside.com/post/p/{page}/q/` | `.write_div` | AJAX라 미수집 |
| theqoo(더쿠) | 네이버 View에서 URL 발견 | `.rd_body .xe_content` | 동적 댓글 미수집 |
| daum(다음카페) | 과거 검색 후보 URL | 모바일 페이지 `#article` | 미수집 |

펨코는 Python 어댑터에 포함하지 않는다. URL 발견 후 Chrome에서 원문을 직접 확인하고, 전수 판정을 통과한 글만 `data/records.jsonl`에 통합했다.

## 사용
```bash
python -m venv venv && source venv/bin/activate
pip install requests beautifulsoup4 lxml

python scraper.py --sites dogdrip,nate,dcinside --pages 8   # 수집(이어붙임)
python scraper.py --sites theqoo --pages 3 \
  --queries "소모임 어플,소모임 앱,소모임 후기"
python scraper.py --refresh-dates                           # 빈 날짜를 원문에서 다시 수집
python scraper.py --export-csv                             # Excel 호환 CSV 생성
python scraper.py --stats                                   # 누적 현황

python recover_daum_posts.py                               # 공개 다음카페 원문 수집
python curate_daum_posts.py                                # 전수 판정 결과 통합

# 소모임 서울 웹 공개 모임 목록만 SQLite에 수집 (상세 페이지 미요청)
python collect_group_list.py
```

## 출력
`data/records.jsonl` — 1줄 1글. 기본 필드: `site, url, title, body, comments[], date, score, query`.
- `url` 기준 중복 제거(재실행 시 이어붙임).
- `score`: 관련성 신호어 매칭 수(높을수록 모임 후기일 확률↑). 후처리 필터에 활용.
- 본 데이터에는 검색 미리보기를 넣지 않는다.

`data/records.csv` — JSONL 정본을 스프레드시트에서 읽기 쉽게 변환한 UTF-8 BOM CSV.
- 열: `site, date, title, body, comments, comment_count, url, score, query, source_kind, access, retrieved_at`
- 여러 댓글은 `---` 구분선으로 합치고, 본문과 댓글의 줄바꿈은 CSV 인용 필드 안에 보존한다.
- `date`는 `YYYY-MM-DD HH:MM`을 기본으로 하며 원문이 날짜만 제공하거나 초까지 제공하면 해당 정밀도를 보존한다.

`data/somoim-groups.sqlite3` — 소모임 웹 공개 모임 목록 스냅샷.
- `collection_runs`: 수집 조건·시각·완료 상태·건수
- `groups`: `gid` 기준 최신 목록 요약. 목록 API의 약 50자 소개만 저장하며 상세 페이지는 요청하지 않음
- `group_listings`: 수집 실행별 페이지와 노출 순서
- `gid`가 있으므로 필요할 때만 `https://www.somoim.co.kr/{gid}`에서 상세를 확인할 수 있음

## 2026-08-31 전수 판정 결과

- 기존 원문 후보 439건을 개별 판정해 87건을 남긴 뒤, 다음카페 원문 124건을 추가로 전수 판정해 9건을 편입함
- 최종 원문 96건: 펨코 35 / 네이트판 26 / 더쿠 24 / 다음카페 9 / 개드립 1 / 디시인사이드 1
- 포함: 앱에서 모임을 탐색·가입·참여·탈퇴·운영한 경험, 앱을 실제 선택하거나 포기한 판단
- 제외: 일반 동호회·학교·교회 소모임, 모집·공지·홍보, 다른 서비스 경험, 소모임 앱이 주변적으로만 언급된 글, 앱인지 확인할 수 없는 글
- 검증: JSON 파싱 오류 0건, URL 중복 0건, 빈 본문 0건, 빈 날짜 0건
- 사용한 검색어: 소모임 어플·앱·후기·정모·가입·탈퇴·모임장·동호회·활동·운영·추천·다녀온

다음카페는 정확한 서비스 표현이 있던 검색 후보 531개 URL을 직접 요청했다. 공개 원문 124건을 확보했고, 회원 전용 393건·운영자 전용 13건·본문 미제공 1건은 코퍼스에서 제외했다. 공개 원문 124건의 판정과 사유는 `data/daum-app-review.csv`에 기록했으며, 동일 본문 재게시 4건은 가장 이른 공개 원문 1건만 유지했다.

사이트별 검색 방식이 다르고 확률 표본이 아니므로, 96건을 합쳐 사용자 전체의 불만 비율이나 사용자 비율을 계산하지 않는다. 감정·경험의 유형을 살피는 정성 코퍼스로 사용한다.

## 한계 / 다음
- 포함 여부는 소모임 앱·플랫폼 관련성이 원문에서 확인되는지를 기준으로 판정했으며, 일반 동호회 경험을 소모임 앱 경험으로 추정하지 않음.
- `data/daum-full-posts.jsonl`은 공개 원문 124건의 수집 원본이며, 최종 코퍼스 편입 여부와는 다름.
- `data/daum-unavailable.jsonl`은 접근 실패 감사 기록으로, 검색 미리보기 본문은 저장하지 않고 코퍼스에도 포함하지 않음.
- 네이트판 본문은 머리말/꼬리말 제거가 휴리스틱이라 일부 지저분할 수 있음.
- 더쿠 URL 발견량은 네이버 검색 색인 범위에 제한됨.
