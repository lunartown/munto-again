# Research — 문토 모임 생태계

문토를 중심으로 오프라인 모임 플랫폼의 참여 경험, 운영자 노동, 신뢰·안전 구조와 모임의
지속 가능성을 조사하는 프로젝트다.

초기에는 `소개팅형 모임 증가가 취미 사용자 이탈을 만든다`는 가설에서 출발했지만,
리뷰와 인터뷰에서 소개팅 자체보다 **참여 전 운영 조건의 예측 가능성, 문제 행동 관리,
플랫폼의 보호 범위**가 더 중심적인 구조로 나타났다. Sprint 1에서는 `참여 전 운영 약속의
불투명성 + 문제 발생 후 보호 흐름의 불명확성`을 핵심 문제로 선정했다.

## 지금 먼저 볼 문서

1. [프로젝트 계획](docs/project/research_plan.md)
2. [타임라인](docs/project/timeline.md)
3. [통합 조사 결과](docs/findings/research_findings.md)
4. [Sprint 1 인사이트 요약](docs/findings/sprint1_insight_summary.md)
5. [인터뷰 가이드](docs/methods/interview_guide.md)
6. [인터뷰 인덱스](docs/interviews/README.md)
7. [인터뷰 어피니티 카드](data/synthesis/interview_affinity_cards.md)

## 리서치 모듈 구조

```text
research/
├── README.md
├── docs/
│   ├── project/       # 현재 계획, 일정, 의사결정 기준
│   ├── methods/       # 인터뷰 가이드, 코딩북, 수집 방법
│   ├── interviews/    # 익명화된 인터뷰별 요약
│   └── findings/      # 검증을 거친 분석 보고서
├── data/
│   ├── listings/      # 문토 모집글: raw / processed / validation
│   ├── reviews/       # 앱스토어별 raw / samples / interim / processed / outputs
│   ├── interviews/    # 인터뷰 세션 메타데이터
│   ├── metadata/      # 출처 목록
│   └── synthesis/     # 통합 발화 카드와 어피니티 클러스터
└── scripts/
    ├── collection/    # 외부 원자료 수집
    ├── analysis/      # 코딩·집계·보고서 생성
    └── validation/    # 스키마·표본·코딩 검증
```

## 데이터 단계 규칙

| 단계 | 의미 | 수정 원칙 |
|---|---|---|
| `raw` | 외부에서 수집한 최소화된 원자료 | 원칙적으로 덮어쓰지 않고 수집일 기록 |
| `samples` | 특정 분석 목적의 고정 표본 | 표집 규칙과 함께 보존 |
| `interim` | 재생성 가능한 AI 1차·중간 산출물 | 최종 근거로 직접 인용하지 않음 |
| `processed` | 검토·코딩이 끝난 분석용 데이터 | 변경 시 검증 기록 필요 |
| `outputs` | 표·요약 같은 집계 결과 | 스크립트로 재생성 가능해야 함 |
| `docs/findings` | 사람이 읽는 최종 해석 | 사실·해석·가설·한계를 분리 |

새 파일은 파일명을 늘리기 전에 기존 단계의 파일을 갱신한다. 인터뷰만 참여자 ID별로
한 파일씩 추가한다. 실명, 연락처, 프로필과 정확한 모임명 등 식별 정보는 저장하지 않는다.

## 주요 실행 명령

워크스페이스 루트에서 `cd coursework/case-study/research` 후 실행한다.

```bash
# 문토 모집글 수집·코딩
python3 scripts/collection/collect_munto.py --count 200
python3 scripts/analysis/code_munto.py

# Google Play 리뷰 수집·분석
python3 scripts/collection/collect_google_play_review_history.py
python3 scripts/analysis/analyze_google_play_review_history.py

# 정성 데이터 스키마 검증
python3 scripts/validation/validate_qual_data.py
```

공개 API와 비공식 스토어 엔드포인트는 변경될 수 있다. 기존 원자료가 있으면 분석 재현을
위해 우선 사용하고, 새로 수집할 때는 기존 파일의 수집일과 범위를 먼저 확인한다.

## 현재 데이터 현황

- 문토 모집글 200건 및 A/B/C 코딩
- Google Play 공개 텍스트 리뷰 1,200건 시계열 분석
- Google Play·App Store 검토 리뷰 89건, 발화 카드 135장
- (중간 산출물: Google Play 93장, App Store 42장 — 최종 교차분석에 통합)
- 익명화 인터뷰 7건: 주최자, 참여자, 참여자 겸 운영자 사례
- 인터뷰 근거 카드 35장, AI 1차 군집과 사람의 수동 재분류 6개
- Fishbone·5 Whys, 핵심 문제 정의와 Sprint 2 초기 가설

현재 단계와 다음 작업은 [타임라인](docs/project/timeline.md)을 단일 기준으로 사용한다.
