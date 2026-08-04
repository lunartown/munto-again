# 프로젝트 작업 기록

기준일: 2026-08-04
상태 표기: `완료` · `진행 중` · `예정` · `보류`

## 전체 진행 상황

| 단계 | 작업 | 상태 | 산출물·완료 조건 |
|---|---|---|---|
| 1. 탐색 | 초기 문제와 리서치 질문 설정 | 완료 | 소개팅화·취미 사용자 이탈 가설 |
| 2. 공급 분석 | 문토 모집글 200건 수집·A/B/C 코딩 | 완료 | 카테고리별 공급 구성과 C 비율 |
| 3. 리뷰 분석 | Google Play 1,200건 시계열 및 App Store 비교 | 완료 | 저평점·주제 변화·반례·한계 |
| 4. 인터뷰 | H01·U01·HU01·U02·HU02·U03·U04 정리 | 완료 | 탐색 인터뷰 7건과 목표 3유형 확보 |
| 5. 원인 합성 | 인터뷰 간 공통점·차이·반례 비교 | 완료 | 수동 어피니티 6개와 결과 분리 |
| 6. 핵심 문제 선정 | Fishbone·5 Whys·선정 기준 적용 | 범위 수정 중 | 클럽 가입 전 목적·방식·규칙·최근 활동 비교의 어려움 |
| 6. Sprint 02 Current-State Audit | 문토 현재 플로우·화면·정보 구조 분석 | 진행 중 | 화면 39장·탐색/참여 플로우 1차·근거 매핑, 미확인 상태 보강 |
| 7. 기획 | 해결 가설과 서비스 구조 설계 | 예정 | 컨셉 3개, Sprint 2 우선 시나리오 |
| 8. 검증 | 컨셉 인터뷰 또는 사용성 테스트 | 예정 | 주요 위험과 수정안 |
| 9. 최종 정리 | 리서치·문제 정의·기획 보고서 | 예정 | 근거와 한계가 연결된 최종 문서 |

## 작업 기록

### 2026-07-30 — 정량·정성 기반 구축

- 문토 공개 모집글 200건 수집
- A/B/C 모임 목적 코딩과 카테고리 분석
- Google Play 공개 텍스트 리뷰 1,200건 확보
- App Store 비교 표본 확보
- 리뷰 발화 카드와 어피니티 후보 작성

### 2026-07-31 — 문제 재정의와 인터뷰 시작

- 소개팅 자체를 문제로 단정하지 않도록 초기 가설 수정
- H01 전문 주최자 인터뷰 요약
- U01 취미 참여자 인터뷰 요약
- HU01 참여자 겸 운영자 인터뷰 요약
- U02 친구 관계 목적 참여자 인터뷰 요약
- HU02 그림·언어교환 참여자 겸 운영자 인터뷰 요약
- 운영 노동·활동 구조·신뢰와 안전을 경쟁 가설로 정리
- 프로젝트 폴더를 `docs / data / scripts` 구조로 개편
- 당시 인터뷰 카드 31장을 경험 조건 6개와 행동 결과로 수동 재분류
- Fishbone·5 Whys와 핵심 문제 선정
- 운영 포맷·안전 대응·운영 분담의 초기 가설 3개 작성

### 2026-08-01 — 추가 인터뷰와 어피니티 동기화

- U03 취미·자기계발 모임 참여자 인터뷰 요약
- U04 영어 학습 모임 참여자 인터뷰 요약
- 원문 근거 카드 4장을 추가해 인터뷰 카드 총 35장으로 갱신
- FigJam의 원문 근거, AI 1차 군집, 직접 재분류, 최종 v2에 동일 근거 반영
- 기존 핵심 문제와 결론은 유지하고 탐색 실패·개인 적합성 근거를 보강

### 2026-08-02~03 — Current-State와 전체 산출물 통합

- 홈·검색·카테고리·큐레이션·찜·소셜링·클럽·챌린지 화면을 캡처하고 CS 번호를 부여
- 소셜링·클럽·챌린지의 참여 상태를 분리해 Current-State Flow를 재작성
- 현재 플로우와 Sprint 1 인터뷰·리뷰·모집글 근거를 매핑
- Figma 디자인 파일에 Master Archive, Research, Affinity, Current-State, Evidence, Problem Definition, Source Inventory 페이지를 배치
- Notion·FigJam·로컬 자료의 정본 역할과 전체 폴더 구조를 `PROJECT-INDEX.md`와 의사결정 로그로 고정

### 2026-08-04 — 저장소·문서 구조 개편

- `coursework/missions` 삭제
- `coursework/portfolio` 삭제
- 기존 리서치 전체를 `archive/research`로 이동
- 기존 디자인 문서·다이어그램 전체를 `archive/design`으로 이동
- Sprint 기록과 제품 정의를 `sprints/sprint-01`, `sprints/sprint-02`로 이동
- 루트에 `research`, `design`, `sprints` 폴더 생성
- 날짜별 작업 기록을 루트 `worklog.md`로 이동
- `PROJECT-INDEX.md`를 새 폴더 구조 기준으로 재작성
- `AGENTS.md`와 `CLAUDE.md` 생성
- Sprint 01의 `SPRINT1-MASTER-ARCHIVE`, `decision-log`, `research-plan`을 `sprints/sprint-01/sprint-01.md`로 통합
- 통합 후 중복된 Sprint 01 문서 삭제
- Sprint 02의 `SPRINT1.5-MASTER-ARCHIVE`와 `current-state-audit`를 `sprints/sprint-02/sprint-02.md`로 통합
- Sprint 02 내부의 `Sprint 1.5` 명칭을 `Sprint 02`로 정리

### 2026-08-04 — Sprint 02 재시작

- Sprint 02 기존 산출물을 처음부터 다시 진행하기로 결정
- `sprints/sprint-02/product/roadmap.md` 삭제
- `sprints/sprint-02/product/target-user-selection-matrix.md` 삭제
- `sprints/sprint-02/sprint-02.md` 기존 내용(Current-State Audit 통합본) 비움

## 현재 상태

- Sprint 01: 작업 완료
- Sprint 02: 재시작 — 기존 산출물 정리, 신규 작업 시작 전
- 저장소 구조: 기존 작업 아카이브 이동 완료, 새 작업 영역 생성 완료

## 다음 작업

1. Sprint 02 목표·범위 재정의
2. Sprint 02 신규 작업 계획 수립
