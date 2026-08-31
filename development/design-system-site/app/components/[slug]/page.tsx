import type { Metadata } from "next";
import { notFound } from "next/navigation";
import { DocsLayout, StatusBadge } from "../../ui/docs-layout";
import { GatheringVariantDemo, ReviewStateDemo, TextboxStateDemo } from "../../ui/system-components";

const docs = {
  "participated-gathering-card": {
    name: "Participated Gathering Card", category: "CONTENT COMPONENT", description: "후기의 근거가 되는 정기모임 정보를 연결합니다. 공개 여부와 노출 맥락에 따라 카드·미니멀·목록 형태로 전환됩니다.",
    node: "624:3053", demo: <GatheringVariantDemo />,
    anatomy: [["1", "Context label", "참여한 정기모임이라는 정보 역할"],["2", "Title", "정기모임명, 한 줄 말줄임"],["3", "Metadata", "일시 · 지역 · 참석 인원"],["4", "Cover", "Default 카드에서만 보이는 대표 이미지"]],
    variants: ["Card Default / Public", "Card Default / Private", "Card Default / Private - My Page", "Card Minimal / Public", "Card Minimal / Private", "List Item / Public", "List Item / Private"],
    usage: ["후기 작성 화면에서 사용자가 선택한 정기모임을 확인할 때", "후기 항목 안에서 실제 참여 경험의 맥락을 연결할 때", "목록에서는 이미지와 정보 위계를 유지하되 카드 배경을 제거할 때"],
    gaps: ["Private 상태에서 정보가 가려지는 정책적 조건", "긴 모임명·지역명 조합의 말줄임 기준", "웹 환경의 hover·focus·pressed 상태"],
  },
  textbox: {
    name: "Textbox", category: "INPUT COMPONENT", description: "후기 또는 신고 내용을 입력하는 장문 필드입니다. 입력면과 글자 수 카운터를 하나의 상태 단위로 관리합니다.",
    node: "665:5551", demo: <TextboxStateDemo />,
    anatomy: [["1", "Input surface", "200px 높이의 장문 입력 영역"],["2", "Placeholder / value", "입력 전 안내 또는 입력값"],["3", "Count caption", "현재 글자 수 / 최대 500자"],["4", "Border state", "기본·포커스·비활성 상태 전달"]],
    variants: ["Default", "Focused", "Filled", "Disabled"],
    usage: ["라벨은 Textbox 바깥 섹션에서 제공하고 입력 목적을 먼저 설명합니다.", "글자 수는 오른쪽 아래에 항상 노출하여 제한을 예측할 수 있게 합니다.", "비활성 상태는 배경과 텍스트를 함께 낮춰 편집 불가를 전달합니다."],
    gaps: ["오류·성공 상태 및 도움말 문구", "키보드 focus-visible과 모바일 포커스의 구분", "500자 초과 시 차단 또는 오류 처리 방식"],
  },
  "review-item": {
    name: "Review Item", category: "CONTENT COMPONENT", description: "익명 작성자 정보, 후기 내용, 참여 모임, 도움 반응과 관리 메뉴를 하나의 읽기 단위로 묶습니다.",
    node: "669:5687", demo: <ReviewStateDemo />,
    anatomy: [["1", "Author row", "프로필·익명 이름·작성 시각·메뉴"],["2", "Review content", "후기 본문과 더보기"],["3", "Gathering context", "참여한 정기모임 카드"],["4", "Helpful action", "도움 반응과 누적 수"],["5", "Reported state", "신고 누적 시 축약된 대체 내용"]],
    variants: ["Type / Default", "Type / Reported"],
    usage: ["Review List의 슬롯 안에서 Divider와 반복합니다.", "참여 모임 정보는 후기의 사실성 맥락을 제공할 때 포함합니다.", "Reported 상태는 본문 대신 검토 상태와 펼치기 행동을 표시합니다."],
    gaps: ["본문이 잘리는 정확한 줄 수와 더보기 전환", "도움 반응의 selected 상태와 중복 입력 규칙", "신고 누적 기준·펼치기 권한·복원 상태"],
  },
} as const;

type Slug = keyof typeof docs;

export function generateStaticParams() { return Object.keys(docs).map((slug) => ({ slug })); }

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }): Promise<Metadata> {
  const { slug } = await params;
  const doc = docs[slug as Slug];
  return { title: doc?.name ?? "Component" };
}

export default async function ComponentDetail({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const doc = docs[slug as Slug];
  if (!doc) notFound();
  return (
    <DocsLayout toc={[{ href: "#overview", label: "Overview" },{ href: "#anatomy", label: "Anatomy" },{ href: "#variants", label: "Variants & states" },{ href: "#usage", label: "Usage" },{ href: "#gaps", label: "보강 필요" }]}>
      <header className="component-hero" id="overview"><p className="eyebrow">{doc.category}</p><h1>{doc.name}</h1><p>{doc.description}</p><div className="component-meta"><StatusBadge kind="verified">Figma node {doc.node}</StatusBadge><StatusBadge kind="chosen">1차 문서화</StatusBadge></div></header>
      <section className="component-canvas"><span className="canvas-label">INTERACTIVE PREVIEW</span>{doc.demo}</section>
      <section className="doc-section" id="anatomy"><div className="doc-section-head"><div><h2>Anatomy</h2><p>컴포넌트가 전달하는 정보 역할을 기준으로 구분합니다.</p></div></div><div className="anatomy-list">{doc.anatomy.map(([number, name, detail]) => <div key={number}><span>{number}</span><strong>{name}</strong><p>{detail}</p></div>)}</div></section>
      <section className="doc-section" id="variants"><div className="doc-section-head"><div><h2>Variants & states</h2><p>현재 Figma component property에서 확인된 조합입니다.</p></div><StatusBadge kind="verified">Figma 확인</StatusBadge></div><div className="variant-list">{doc.variants.map((variant) => <code key={variant}>{variant}</code>)}</div></section>
      <section className="doc-section" id="usage"><div className="doc-section-head"><div><h2>Usage</h2><p>현재 프로토타입의 사용 맥락과 컴포넌트 구조에서 도출한 1차 가이드입니다.</p></div><StatusBadge kind="chosen">문서화 선택</StatusBadge></div><ol className="usage-rules">{doc.usage.map((item, index) => <li key={item}><span>{String(index + 1).padStart(2, "0")}</span><p>{item}</p></li>)}</ol></section>
      <section className="doc-section gap-section" id="gaps"><div className="doc-section-head"><div><h2>앞으로 보강할 부분</h2><p>현재 Figma에서 확인되지 않았거나 제품 정책과 함께 정해야 하는 항목입니다.</p></div><StatusBadge kind="pending">미확인</StatusBadge></div><ul className="gap-list compact">{doc.gaps.map((item) => <li key={item}><span>{item}</span></li>)}</ul></section>
    </DocsLayout>
  );
}
