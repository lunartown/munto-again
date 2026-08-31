import type { Metadata } from "next";
import { DocsLayout, PageIntro } from "../ui/docs-layout";

export const metadata: Metadata = { title: "Roadmap" };

const phases = [
  { number: "01", title: "Foundations & core", status: "운영 중", items: ["Semantic color와 typography 적용", "후기 핵심 컴포넌트의 anatomy·variant·usage 제공", "작성·조회·관리 흐름의 컴포넌트 조합 정의"] },
  { number: "02", title: "State completeness", status: "확장 예정", items: ["오류·성공·empty 상태 추가", "긴 제목과 장문 후기의 overflow 규칙", "입력 제한과 신고 상태의 피드백 정의"] },
  { number: "03", title: "Web accessibility", status: "확장 예정", items: ["Hover·focus-visible·keyboard 상태", "반응형 breakpoint와 콘텐츠 재배치", "색상 대비·터치 영역·텍스트 확대 검증"] },
  { number: "04", title: "System operations", status: "확장 조건", items: ["컴포넌트 명명과 변경 제안 방식", "디자인과 코드의 버전 연결", "사용 빈도와 중복 패턴을 기준으로 자산 정리"] },
];

export default function RoadmapPage() {
  return (
    <DocsLayout toc={[{ href: "#principle", label: "확장 원칙" },{ href: "#phases", label: "단계별 계획" },{ href: "#not-now", label: "확장 조건" }]}>
      <PageIntro eyebrow="ROADMAP" title="Design system growth plan" description="제품 영역이 넓어질수록 필요한 상태, 접근성 기준과 운영 규칙을 단계적으로 확장합니다." />
      <section className="doc-section" id="principle"><div className="doc-section-head"><div><h2>확장 원칙</h2><p>새 자산을 추가할 때 제품 적용 가능성과 상태의 완결성을 함께 검토합니다.</p></div></div><div className="principle-grid"><div><span>01</span><strong>Product first</strong><p>제품 흐름을 구성하거나 여러 화면에서 반복되는 패턴을 컴포넌트로 관리합니다.</p></div><div><span>02</span><strong>State complete</strong><p>기본 형태뿐 아니라 상호작용, 오류와 예외 상태까지 함께 정의합니다.</p></div><div><span>03</span><strong>One language</strong><p>같은 의미는 디자인과 코드에서 동일한 이름과 semantic token을 사용합니다.</p></div></div></section>
      <section className="doc-section" id="phases"><div className="doc-section-head"><div><h2>단계별 계획</h2><p>기초 스타일과 핵심 컴포넌트에서 시작해 웹 접근성과 운영 체계로 확장합니다.</p></div></div><div className="roadmap-list">{phases.map((phase, index) => <article key={phase.number}><span>{phase.number}</span><div><div className="roadmap-title"><h3>{phase.title}</h3><em className={index === 0 ? "now" : ""}>{phase.status}</em></div><ul>{phase.items.map((item) => <li key={item}>{item}</li>)}</ul></div></article>)}</div></section>
      <section className="doc-section not-now" id="not-now"><div><p className="eyebrow">EXPANSION TRIGGERS</p><h2>도구를 확장하는 시점</h2></div><p>컴포넌트 탐색이 어려워지면 검색을, 코드 패키지가 제공되면 코드 예시를, 플랫폼별 구조가 달라지면 Web·iOS·Android 가이드를 추가합니다.</p></section>
    </DocsLayout>
  );
}
