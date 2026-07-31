# Mission Control

교육 과정의 미션 1~10을 요구사항, 선행 조건, 작업 원본과 제출 링크로 연결하는 인덱스다.
실제 분석과 디자인 원본을 이 폴더에 복사하지 않고 각 미션 README에서 정본으로 연결한다.

각 미션 폴더는 두 문서를 가진다.

- `brief-verbatim.md`: 사용자가 제공한 미션 원문 전체 보존본
- `README.md`: 원문을 실제 작업 순서와 완료 조건으로 바꾼 실행용 요약

요약에 없는 표현이나 세부 조건은 원문이 우선한다.

## 전체 미션 지도

| 미션 | 목표 | 제출 형태 | 선행 조건 | 상태 |
|---:|---|---|---|---|
| 미션 | 실행용 요약 | 원문 | 제출 형태 | 선행 조건 | 상태 |
|---:|---|---|---|---|---|
| 1 | [리서치](mission-01-research/README.md) | [원문](mission-01-research/brief-verbatim.md) | Notion 2종 | 없음 | 진행 중 |
| 2 | [UX 정의](mission-02-ux-definition/README.md) | [원문](mission-02-ux-definition/brief-verbatim.md) | 문서 + Figma | 핵심 문제 승인 | 대기 |
| 3 | [상세 UI](mission-03-ui-design/README.md) | [원문](mission-03-ui-design/brief-verbatim.md) | Figma | 와이어프레임 승인 | 대기 |
| 4 | [디자인 시스템](mission-04-design-system/README.md) | [원문](mission-04-design-system/brief-verbatim.md) | Figma | 상세 UI | 대기 |
| 5 | [반응형 프로토타입](mission-05-responsive-prototype/README.md) | [원문](mission-05-responsive-prototype/brief-verbatim.md) | Figma | UI·컴포넌트 | 대기 |
| 6 | [포트폴리오 포지셔닝](mission-06-portfolio-positioning/README.md) | [원문](mission-06-portfolio-positioning/brief-verbatim.md) | Notion | 프로젝트 방향 | 대기 |
| 7 | [디자인 스토리](mission-07-portfolio-story/README.md) | [원문](mission-07-portfolio-story/brief-verbatim.md) | Notion | 프로젝트 선정 | 대기 |
| 8 | [슬라이드 초안](mission-08-portfolio-draft/README.md) | [원문](mission-08-portfolio-draft/brief-verbatim.md) | Figma | 스토리 구성안 | 대기 |
| 9 | [문제 해결 고도화](mission-09-portfolio-refinement/README.md) | [원문](mission-09-portfolio-refinement/brief-verbatim.md) | Figma | 슬라이드 초안 | 대기 |
| 10 | [최종 피드백](mission-10-portfolio-final/README.md) | [원문](mission-10-portfolio-final/brief-verbatim.md) | Figma | 완성 초안 | 대기 |

## 관리 원칙

- `missions`: 제출 관점의 체크리스트와 링크
- `research`: 미션 1의 근거와 분석 정본
- `product`: 미션 2의 문제·JTBD·기능 정본
- `design`: 미션 2~5의 Figma 명세와 링크 정본
- `portfolio`: 미션 6~10의 콘텐츠 정본
- `apps / services`: 과정 이후 실제 구현을 선택할 때 사용

미션 상태는 `대기 → 진행 중 → 검토 필요 → 제출 가능 → 제출 완료`로 관리한다.
파일이 존재한다고 완료로 표시하지 않고, 해당 미션 README의 완료 조건을 모두 통과해야 한다.

## 현재 중요한 사실

미션 1은 데이터 수집은 충분하지만 아직 완료되지 않았다. 인터뷰 5건을 기존 리뷰 카드와
통합해 어피니티를 다시 만들고, 경쟁 가설 중 핵심 문제 하나를 선택한 뒤 Notion 보고서와
요약본을 작성해야 한다. 이 결정 전에는 미션 2의 핵심 기능을 확정하지 않는다.
