import type { Metadata } from "next";
import { DocsLayout, PageIntro, StatusBadge } from "../ui/docs-layout";

export const metadata: Metadata = { title: "Roadmap" };

const phases = [
  { number: "01", title: "현재 자산 정리", status: "진행 중", items: ["Semantic color와 typography 연결", "실사용 핵심 컴포넌트 3개 문서화", "자산과 프로토타입 사용처 매핑"] },
  { number: "02", title: "상태와 규칙 보강", status: "다음", items: ["Supporting component 우선순위 확정", "오류·성공·empty 상태 확인", "긴 콘텐츠와 edge case 검증"] },
  { number: "03", title: "웹 사용성 확장", status: "이후", items: ["Hover·focus-visible·keyboard 상태", "반응형 문서와 breakpoint", "접근성 대비·터치 영역 검증"] },
  { number: "04", title: "운영 가능한 시스템", status: "조건부", items: ["명명 규칙과 contribution 방식", "Figma와 코드 변경 이력 연결", "실제 제품 적용 후 사용량 기반 정리"] },
];

export default function RoadmapPage() {
  return (
    <DocsLayout toc={[{ href: "#principle", label: "보강 원칙" },{ href: "#phases", label: "단계별 계획" },{ href: "#not-now", label: "지금 하지 않는 것" }]}>
      <PageIntro eyebrow="ROADMAP" title="Build what the product proves" description="컴포넌트 수를 채우는 대신 실제 화면에서 반복되는 패턴과 제품 정책이 필요한 빈칸을 구분해 확장합니다." />
      <section className="doc-section" id="principle"><div className="doc-section-head"><div><h2>보강 원칙</h2><p>현재 사이트를 완성품처럼 포장하지 않고 다음 판단이 쉬운 구조로 유지합니다.</p></div><StatusBadge kind="chosen">운영 기준</StatusBadge></div><div className="principle-grid"><div><span>01</span><strong>Usage first</strong><p>실제 화면에 두 번 이상 쓰이거나 핵심 흐름을 설명하는 요소부터 승격합니다.</p></div><div><span>02</span><strong>Evidence labeled</strong><p>Figma에서 확인된 값, 문서화 선택, 미확인 정책을 서로 다른 상태로 표시합니다.</p></div><div><span>03</span><strong>State before count</strong><p>새 컴포넌트를 늘리기 전에 기존 컴포넌트의 상태와 예외를 먼저 채웁니다.</p></div></div></section>
      <section className="doc-section" id="phases"><div className="doc-section-head"><div><h2>단계별 계획</h2><p>앞 단계의 확인 결과가 다음 단계의 범위를 바꿀 수 있습니다.</p></div></div><div className="roadmap-list">{phases.map((phase, index) => <article key={phase.number}><span>{phase.number}</span><div><div className="roadmap-title"><h3>{phase.title}</h3><em className={index === 0 ? "now" : ""}>{phase.status}</em></div><ul>{phase.items.map((item) => <li key={item}>{item}</li>)}</ul></div></article>)}</div></section>
      <section className="doc-section not-now" id="not-now"><div><p className="eyebrow">NOT NOW</p><h2>지금 만들지 않는 것</h2></div><p>전체 아이콘 카탈로그, 코드 복사, 검색, Storybook 연동, 다중 플랫폼 탭은 현재 문서의 핵심 질문에 답하지 않습니다. 컴포넌트 수와 사용자가 늘어 필요성이 확인될 때 추가합니다.</p></section>
    </DocsLayout>
  );
}
