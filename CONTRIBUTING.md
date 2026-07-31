# 작업 규칙

## 파일 배치

- 미션 체크리스트와 제출 링크는 `coursework/missions`
- 관찰과 원자료는 `coursework/case-study/research`
- 해결 범위와 요구사항은 `coursework/case-study/product`
- 사용자 흐름과 시각 명세는 `coursework/case-study/design`
- 포트폴리오 콘텐츠는 `coursework/portfolio`
- 실행 코드는 `development/apps`, `development/services`, `development/packages`
- 배포와 환경은 `development/infra`
- 장기 기술 의사결정은 `development/docs`

## 변경 완료 조건

1. 정본 파일 하나만 수정하고 중복 문서를 만들지 않는다.
2. 원자료를 변경하지 않으며 파생 결과는 재현 가능하게 만든다.
3. 개인정보와 비밀값이 포함되지 않았는지 확인한다.
4. `make check`를 통과한다.
5. 사용자 행동이나 정책을 바꾸면 제품 요구사항과 측정 기준을 함께 갱신한다.
6. 구조·데이터 계약처럼 되돌리기 어려운 결정은 기록을 남긴다.

## 이름 규칙

- 폴더와 코드: 소문자 `kebab-case` 또는 선택한 언어 생태계 표준
- 인터뷰: 익명 ID와 역할, 예: `H02_host.md`
- 제품 요구사항: `PRD-0001-short-title.md`
- 실험: `EXP-0001-short-title.md`
- 의사결정: `ADR-0002-short-title.md` 또는 `DR-0001-short-title.md`
