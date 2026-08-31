import type { Metadata } from "next";
import Link from "next/link";
import { DocsLayout, PageIntro, StatusBadge } from "../ui/docs-layout";
import { GatheringCard, ReviewItem, Textbox } from "../ui/system-components";

export const metadata: Metadata = { title: "Components" };

const supporting = ["Review List", "Sort Button", "View All Button", "FAB", "Bottom Sheet", "Bottom Sheet Item", "Detail Menu", "Alert", "Toast", "Title Bar", "Toggle", "Radio Button", "Add Photo Button"];

export default function ComponentsPage() {
  return (
    <DocsLayout toc={[{ href: "#core", label: "Core components" },{ href: "#supporting", label: "Supporting inventory" },{ href: "#usage", label: "Usage map" }]}>
      <PageIntro eyebrow="COMPONENTS" title="Components" description="개수보다 실제 화면에서의 반복과 상태 정의를 우선합니다. 현재는 후기 작성·조회 흐름을 설명하는 세 컴포넌트를 핵심 문서 대상으로 선정했습니다." />
      <section className="doc-section" id="core"><div className="doc-section-head"><div><h2>Core components</h2><p>상세 문서에서는 anatomy, variants, states, usage와 보강 지점을 함께 봅니다.</p></div><StatusBadge kind="chosen">1차 범위</StatusBadge></div><div className="component-index-grid">
        <Link href="/components/participated-gathering-card" className="component-index-card"><div className="component-preview"><GatheringCard variant="minimal" /></div><span className="component-category">CONTENT</span><h3>Participated Gathering Card</h3><p>후기가 어떤 정기모임 경험을 근거로 하는지 연결합니다.</p><b>7 variants · Prototype reused</b></Link>
        <Link href="/components/textbox" className="component-index-card"><div className="component-preview"><Textbox compact /></div><span className="component-category">INPUT</span><h3>Textbox</h3><p>후기 및 신고 내용을 입력하고 글자 수 상태를 전달합니다.</p><b>4 states · Prototype reused</b></Link>
        <Link href="/components/review-item" className="component-index-card"><div className="component-preview component-preview-review"><ReviewItem reported /></div><span className="component-category">CONTENT</span><h3>Review Item</h3><p>작성자, 경험 내용, 연결 모임과 도움 반응을 묶어 보여줍니다.</p><b>2 types · List composition</b></Link>
      </div></section>
      <section className="doc-section" id="supporting"><div className="doc-section-head"><div><h2>Supporting inventory</h2><p>Figma 컴포넌트로 존재하고 프로토타입에 쓰였지만, 상세 규칙은 아직 덜 확인된 항목입니다.</p></div><StatusBadge kind="pending">차기 문서화</StatusBadge></div><div className="inventory-grid">{supporting.map((item, index) => <div key={item}><span>{String(index + 1).padStart(2, "0")}</span><strong>{item}</strong><em>{["Toggle", "Title Bar", "Add Photo Button", "Review List"].includes(item) ? "실사용 확인" : "자산 확인"}</em></div>)}</div></section>
      <section className="doc-section" id="usage"><div className="doc-section-head"><div><h2>Usage map</h2><p>컴포넌트가 개별 자산에서 끝나지 않고 실제 후기 흐름에서 어떻게 조합되는지 보여줍니다.</p></div><StatusBadge kind="verified">Prototype 확인</StatusBadge></div><div className="usage-flow"><div><span>01</span><strong>정기모임 선택</strong><p>Participated Gathering Card · Divider · Title Bar</p></div><i>→</i><div><span>02</span><strong>후기 작성</strong><p>Toggle · Textbox · Tip Pill · Add Photo Button</p></div><i>→</i><div><span>03</span><strong>후기 조회</strong><p>Review List · Review Item · Sort Button · FAB</p></div><i>→</i><div><span>04</span><strong>관리·신고</strong><p>Detail Menu · Radio List · Alert · Toast</p></div></div></section>
    </DocsLayout>
  );
}
