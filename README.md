# Munto Again

오프라인 모임 경험을 주제로 **리서치부터 UX·UI, 디자인 시스템, 반응형 프로토타입과
최종 포트폴리오까지 미션 1~10을 완수하기 위한 통합 워크스페이스**다. 필요하면 이후
실제 제품 개발까지 확장한다.

현재는 Sprint 1을 마치고 Sprint 1.5 현행 플로우 분석을 시작하는 단계다. 과정 관련 자료는 모두 `coursework` 안에서 관리하고,
실제 제품 개발을 선택할 때만 `development`를 사용한다.

## 최우선 작업 흐름

```text
미션 1  사용자 리서치·어피니티·핵심 문제
  ↓
Sprint 1.5  문토 Current-State Audit·리뉴얼 범위
  ↓
미션 2  시나리오·JTBD·기능·IA·와이어프레임
  ↓
미션 3  상세 UI
  ↓
미션 4  소규모 디자인 시스템
  ↓
미션 5  반응형·인터랙티브 프로토타입
  ↓
미션 6~10  포지셔닝·스토리·슬라이드·피드백·최종 포트폴리오
```

앞 단계의 산출물이 다음 단계의 입력이 된다. 같은 내용을 여러 폴더에 복사하지 않고
정본 문서에 링크한다.

## 워크스페이스 구조

```text
munto-again/
├── coursework/               # 현재 주 작업 영역
│   ├── missions/             # 미션 1~10 체크리스트·제출 링크
│   ├── case-study/
│   │   ├── research/         # 미션 1 근거·인터뷰·분석
│   │   ├── product/          # 미션 2 문제·JTBD·기능
│   │   └── design/           # 미션 2~5 Figma 명세
│   └── portfolio/            # 미션 6~10 콘텐츠
└── development/              # 선택적으로 실제 개발할 때 사용
    ├── apps/
    ├── services/
    ├── packages/
    ├── infra/
    └── docs/
```

루트에서는 `coursework`와 `development`만 선택하면 된다. 과정 안의 세부 단계와 개발
구조는 각각의 상위 폴더 안에서만 확장한다.

## 현재 단일 기준 문서

- 전체 미션 지도: [coursework/missions/README.md](coursework/missions/README.md)
- 제출물 레지스트리: [coursework/missions/submission-registry.md](coursework/missions/submission-registry.md)
- 리서치 현황: [coursework/case-study/research/docs/project/timeline.md](coursework/case-study/research/docs/project/timeline.md)
- Sprint 1.5 계획: [coursework/case-study/research/docs/project/sprint1_5_current_state_audit.md](coursework/case-study/research/docs/project/sprint1_5_current_state_audit.md)
- 경쟁 가설: [coursework/case-study/research/docs/project/research_plan.md](coursework/case-study/research/docs/project/research_plan.md)
- 제품 브리프: [coursework/case-study/product/product-brief.md](coursework/case-study/product/product-brief.md)
- 제품 로드맵: [coursework/case-study/product/roadmap.md](coursework/case-study/product/roadmap.md)
- 저장소 구조 결정: [ADR-0001](development/docs/architecture/ADR-0001-workspace-structure.md)

## 검증 명령

```bash
make check
```

현재 `check`는 리서치 데이터 스키마와 필수 경로를 검증한다. 앱이나 서비스가 추가되면
각 영역의 테스트를 같은 명령에 연결한다.

분석 산출물을 원자료에서 다시 만들려면 다음을 실행한다.

```bash
make research-rebuild
```

## 새 작업을 시작할 때

1. `coursework/missions/mission-XX-*/README.md`에서 완료 조건을 확인한다.
2. 근거나 인터뷰는 `coursework/case-study/research`에 기록한다.
3. 문제·JTBD·기능은 `coursework/case-study/product`에 기록한다.
4. Figma 관련 명세는 `coursework/case-study/design`에 기록한다.
5. 미션 6~10 콘텐츠는 `coursework/portfolio`에 기록한다.
6. 제출 링크는 `coursework/missions/submission-registry.md`에만 기록한다.
7. 실제 개발을 시작할 때만 `development`를 사용한다.

빈 앱·서비스를 미리 만들지 않는다. 문제 정의와 기술 선택이 승인된 시점에 필요한 실행
단위만 추가한다.
