import type { Metadata } from "next";
import Link from "next/link";
import { DocsLayout, PageIntro } from "../ui/docs-layout";
import { GatheringCard, ReviewItem, Textbox } from "../ui/system-components";

export const metadata: Metadata = { title: "Components" };

const supporting = [
  ["Review List", "Content"], ["Sort Button", "Action"], ["View All Button", "Action"],
  ["FAB", "Action"], ["Bottom Sheet", "Presentation"], ["Bottom Sheet Item", "Selection"],
  ["Detail Menu", "Presentation"], ["Alert", "Feedback"], ["Toast", "Feedback"],
  ["Title Bar", "Navigation"], ["Toggle", "Selection"], ["Radio Button", "Selection"],
  ["Add Photo Button", "Input"],
];

export default function ComponentsPage() {
  return (
    <DocsLayout toc={[{ href: "#core", label: "Core components" },{ href: "#supporting", label: "Supporting inventory" },{ href: "#usage", label: "Usage map" }]}>
      <PageIntro eyebrow="COMPONENTS" title="Components" description="후기 작성과 조회에 필요한 정보를 일관된 구조와 상태로 제공합니다. 각 컴포넌트는 역할, 구성 요소, 변형과 사용 원칙을 함께 정의합니다." />
      <section className="doc-section" id="core"><div className="doc-section-head"><div><h2>Core components</h2><p>후기 경험의 맥락을 연결하고 입력과 조회를 지원하는 핵심 컴포넌트입니다.</p></div></div><div className="component-index-grid">
        <Link href="/components/participated-gathering-card" className="component-index-card"><div className="component-preview"><GatheringCard variant="minimal" /></div><span className="component-category">CONTENT</span><h3>Participated Gathering Card</h3><p>후기가 어떤 정기모임 경험을 바탕으로 작성됐는지 연결합니다.</p><b>7 variants · 작성·조회</b></Link>
        <Link href="/components/textbox" className="component-index-card"><div className="component-preview"><Textbox compact /></div><span className="component-category">INPUT</span><h3>Textbox</h3><p>후기 및 신고 내용을 입력하고 글자 수 상태를 전달합니다.</p><b>4 states · 후기·신고</b></Link>
        <Link href="/components/review-item" className="component-index-card"><div className="component-preview component-preview-review"><ReviewItem reported /></div><span className="component-category">CONTENT</span><h3>Review Item</h3><p>작성자, 경험 내용, 연결 모임과 도움 반응을 묶어 보여줍니다.</p><b>2 types · List composition</b></Link>
      </div></section>
      <section className="doc-section" id="supporting"><div className="doc-section-head"><div><h2>Supporting components</h2><p>탐색, 선택, 입력과 피드백을 보조하는 컴포넌트입니다.</p></div></div><div className="inventory-grid">{supporting.map(([item, category], index) => <div key={item}><span>{String(index + 1).padStart(2, "0")}</span><strong>{item}</strong><em>{category}</em></div>)}</div></section>
      <section className="doc-section" id="usage"><div className="doc-section-head"><div><h2>Usage map</h2><p>후기 흐름의 각 단계에서 컴포넌트가 어떻게 조합되는지 보여줍니다.</p></div></div><div className="usage-flow"><div><span>01</span><strong>정기모임 선택</strong><p>Participated Gathering Card · Divider · Title Bar</p></div><i>→</i><div><span>02</span><strong>후기 작성</strong><p>Toggle · Textbox · Tip Pill · Add Photo Button</p></div><i>→</i><div><span>03</span><strong>후기 조회</strong><p>Review List · Review Item · Sort Button · FAB</p></div><i>→</i><div><span>04</span><strong>관리·신고</strong><p>Detail Menu · Radio List · Alert · Toast</p></div></div></section>
    </DocsLayout>
  );
}
