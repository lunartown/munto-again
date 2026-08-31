# 소모임 커뮤니티 후기 수집기

소모임(및 취미 모임) 관련 커뮤니티 글을 대량으로 모아 JSONL로 적재하는 스크래퍼.
목적: 앱스토어 리뷰(앱 기능 불만)엔 없는, **감정·경험이 담긴 실제 모임 후기**를 확보.

## 왜 이 방식인가
- 앱스토어 리뷰: 대량이지만 "채팅 왜 없앴냐/알림/결제" 등 앱 기능 불만 위주라 모임 경험 신호가 약함 → 목적에 부적합.
- 사이트 내부 검색: "소모임"이 흔한 부분문자열("공소취소모임" 등)이라 정치 노이즈가 많음 → 관련성 필터로 컷.
- 펨코: 통합검색 연속 요청이 `430`으로 제한되어 네이버 View 검색의 공개 미리보기를 저장함.
- 더쿠: 공개 전역검색이 없어 네이버 View 검색으로 URL만 발견하고, 원문은 더쿠에서 직접 수집함.
- 다음카페: 전체 카페글 검색은 공개되지만 원문은 카페별 회원 등급 제한이 많아 검색 미리보기를 저장함.

## 사이트 어댑터
| 사이트 | 검색 | 본문 | 댓글 |
|---|---|---|---|
| dogdrip(개드립) | `index.php?mid=dogdrip&search_target=title_content` | `.xe_content`(첫 요소) | `.comment .xe_content` ✅ |
| nate(네이트판) | `pann.nate.com/search/talk` → 본문은 `m.pann` | `.view-wrap` | AJAX라 미수집 |
| dcinside | `search.dcinside.com/post/p/{page}/q/` | `.write_div` | AJAX라 미수집 |
| fmkorea(펨코) | 네이버 View에서 URL 발견 | 검색결과 미리보기 | 미수집 |
| theqoo(더쿠) | 네이버 View에서 URL 발견 | `.rd_body .xe_content` | 동적 댓글 미수집 |
| daum(다음카페) | `top.cafe.daum.net` 카페글 검색 | 검색결과 미리보기 | 미수집 |

## 사용
```bash
python -m venv venv && source venv/bin/activate
pip install requests beautifulsoup4 lxml

python scraper.py --sites dogdrip,nate,dcinside --pages 8   # 수집(이어붙임)
python scraper.py --sites fmkorea,theqoo,daum --pages 3 \
  --queries "소모임 어플,소모임 앱,소모임 후기"
python scraper.py --stats                                   # 누적 현황
```

## 출력
`data/records.jsonl` — 1줄 1글. 기본 필드: `site, url, title, body, comments[], date, score, query`.
- `url` 기준 중복 제거(재실행 시 이어붙임).
- `score`: 관련성 신호어 매칭 수(높을수록 모임 후기일 확률↑). 후처리 필터에 활용.
- `source_kind`: `full_post` 또는 `search_preview`. 펨코·다음카페 미리보기는 원문과 구분해 사용.

## 2026-08-31 수집 결과

- 원본: `data/records.jsonl` 4,767건, 4.85MB
- 사이트별: 다음카페 4,326 / 네이트판 303 / 더쿠 53 / 펨코 49 / 개드립 20 / 디시인사이드 16
- 자료 층위: 검색 미리보기 4,375 / 더쿠 원문 53 / 기존 수집 339
- 검증: JSON 파싱 오류 0건, URL 중복 0건, 빈 제목 0건
- 사용한 검색어: 소모임 어플·앱·후기·정모·가입·탈퇴·모임장·동호회·활동·운영·추천·다녀온

사이트별 검색 방식과 본문 길이가 다르고 확률 표본이 아니므로, 전체 4,767건을 합쳐 불만 비율이나 사용자 비율을 계산하지 않는다. 대량 후보군에서 경험담을 찾아 원문을 확인하는 용도로 사용한다.

## 한계 / 다음
- 관련성 필터는 키워드 기반이라 잔여 노이즈(동호회 일반 썰 등) 있음 → `score`로 2차 필터.
- 네이트판 본문은 머리말/꼬리말 제거가 휴리스틱이라 일부 지저분할 수 있음.
- 다음카페 `search_preview`는 검색엔진이 공개한 일부 본문이므로 원문 전체로 해석하지 않음.
- 펨코 `search_preview`도 검색엔진이 공개한 일부 본문이며, 원문 접근 제한이 풀린 뒤 별도 보강이 필요함.
- 더쿠 URL 발견량은 네이버 검색 색인 범위에 제한됨.
