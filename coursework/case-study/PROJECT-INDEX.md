# Munto Redesign — Project Index

이 파일은 프로젝트 전체 파일 구조와 각 폴더의 정본 역할을 한눈에 확인하기 위한 인덱스다.
내용을 복사해 여러 곳에서 관리하지 않고, 원본 위치·상태·다음 사용처를 연결한다.

## 현재 단계

`Sprint 1 리서치`는 근거 수집·정성/정량 분석·어피니티·Fishbone·5 Whys까지 진행했다.
현재는 `Sprint 1.5 Current-State Audit`로 문토의 실제 화면·진입점·콘텐츠 유형별 상태를
확인 중이다. Sprint 2의 기능이나 UI는 아직 승인하지 않는다.

## 폴더 구조

```text
coursework/
├── case-study/
│   ├── SPRINT1-MASTER-ARCHIVE.md   # Sprint 1 전체 결정·근거·보류·산출물 기록
│   ├── PROJECT-INDEX.md            # 이 프로젝트 구조 인덱스
│   ├── research/                   # 원자료, 방법론, 분석, 인사이트
│   │   ├── data/                   # CSV와 캡처: 원문·코딩·검증·합성
│   │   ├── docs/                   # 계획·방법·인터뷰·결과
│   │   └── scripts/                # 수집·분석·검증 재현 코드
│   ├── design/                     # Figma 명세와 향후 UX/UI 산출물
│   │   ├── flows/                  # Current-State·Target-State 플로우
│   │   ├── prototypes/             # 검증용 프로토타입 메모
│   │   ├── system/                 # 디자인 토큰·컴포넌트
│   │   └── figma-index.md          # Figma 페이지 레지스트리
│   └── product/                    # 제품 가설·로드맵·요구사항
└── missions/
    ├── mission-01-research/       # 미션 원문과 실행 체크리스트
    ├── mission-02-ux-definition/  # 시나리오·JTBD·IA·와이어프레임
    ├── mission-03-ui-design/      # 상세 UI
    ├── mission-04-design-system/  # 디자인 시스템
    ├── mission-05-responsive-prototype/
    ├── mission-06-portfolio-positioning/
    ├── mission-07-portfolio-story/
    ├── mission-08-portfolio-draft/
    ├── mission-09-portfolio-refinement/
    ├── mission-10-portfolio-final/
    └── submission-registry.md     # 제출물 링크의 단일 정본
```

## 저장 규칙

| 자료 | 저장 위치 | 삭제·복사 규칙 |
|---|---|---|
| 인터뷰 원문·사용자 표현 | `research/docs/interviews` | 표현을 순화하지 않고 원문 유지 |
| 리뷰·모집글 원자료 | `research/data/reviews`, `research/data/listings` | 원자료와 코딩 결과를 분리 |
| AI 결과 | `research/data`의 AI/검증 파일 | 사람 검증 전 결론으로 사용하지 않음 |
| 어피니티·Fishbone | FigJam 원본 + `research/data/synthesis` | Figma에는 보존용 사본만 둠 |
| 현재 화면 | `research/data/current_state/screenshots` | 캡처 번호를 문서·플로우와 일치시킴 |
| 제출 문서 | Notion | 원문 데이터와 다른 요약은 근거 링크를 남김 |
| 미래 기능 | `product/requirements` | 핵심 문제 승인 전 기능 파일을 확정하지 않음 |

## 작업 순서

1. 원문을 수집하고 ID를 부여한다.
2. 코딩북·분류 기준을 고정한 뒤 AI 1차 분석을 실행한다.
3. 사람이 원문을 대조해 수정·제외·재분류한다.
4. 결과를 어피니티와 근거 매트릭스로 연결한다.
5. Fishbone·5 Whys로 원인과 결과를 분리한다.
6. 현재 화면과 플로우에 리서치 근거를 매핑한다.
7. 핵심 문제와 대표 시나리오를 승인한 뒤에만 아이디에이션·기능·UI로 넘어간다.

## 참고 링크

- [Sprint 1 Master Archive](SPRINT1-MASTER-ARCHIVE.md)
- [Research README](research/README.md)
- [Current-State Audit](research/docs/project/sprint1_5_current_state_audit.md)
- [전체 산출물 정리 작업 로그](research/docs/project/archive-worklog-2026-08-03.md)
- [Sprint 1 의사결정 로그](research/docs/project/decision-log.md)
- [Design README](design/README.md)
- [Figma Index](design/figma-index.md)
- [Mission Control](../missions/README.md)
- [Submission Registry](../missions/submission-registry.md)
