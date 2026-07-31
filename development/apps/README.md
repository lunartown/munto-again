# Apps

사용자에게 직접 배포되는 실행 단위를 둔다.

예: `development/apps/web`, `development/apps/mobile`, `development/apps/admin`.

기술 스택과 배포 단위가 결정되기 전에는 빈 애플리케이션을 만들지 않는다. 각 앱은 자체
실행·테스트 명령과 환경변수 예시를 제공하고, 공용 로직은 실제 재사용이 확인된 뒤
`packages`로 이동한다.
