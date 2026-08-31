import type { Metadata } from "next";
import { DocsLayout, PageIntro, StatusBadge } from "../ui/docs-layout";

export const metadata: Metadata = { title: "Foundations" };

const colors = [
  ["primary/normal", "#459FF7"], ["text/normal", "#0A0A0A"], ["text/neutral", "#525252"],
  ["text/alternative", "#A3A3A3"], ["text/assistive", "#D4D4D4"], ["text/inverse", "#FFFFFF"],
  ["background/normal", "#FDFDFD"], ["background/assistive", "#F5F5F5"], ["line/normal", "#D4D4D4"],
];
const types = [
  ["title/M/bold", "20 / 28", "700"], ["body/L/bold", "16 / 24", "700"],
  ["body/L/medium", "16 / 24", "500"], ["body/M/medium", "14 / 22", "500"],
  ["body/M/regular", "14 / 22", "400"], ["label/M/regular", "14 / 18", "400"],
  ["caption/S/regular", "12 / 16", "400"], ["label/S/regular", "12 / 16", "400"],
];

export default function FoundationsPage() {
  return (
    <DocsLayout toc={[{ href: "#color", label: "Color" },{ href: "#typography", label: "Typography" },{ href: "#spacing", label: "Spacing & radius" },{ href: "#icons", label: "Icons" },{ href: "#gaps", label: "보강 필요" }]}>
      <PageIntro eyebrow="FOUNDATIONS" title="Foundations" description="색상, 타이포그래피, 간격과 형태의 공통 기준입니다. 의미 중심의 토큰을 사용해 화면과 컴포넌트가 같은 시각 언어를 공유합니다." />

      <section className="doc-section" id="color"><div className="doc-section-head"><div><h2>Color</h2><p>색상값 대신 배경, 텍스트, 선과 주요 행동처럼 UI 역할을 나타내는 semantic token을 사용합니다.</p></div></div><div className="color-grid">{colors.map(([name, value]) => <div className="color-token" key={name}><div style={{ background: value }} /><strong>{name}</strong><code>{value}</code></div>)}</div></section>

      <section className="doc-section" id="typography"><div className="doc-section-head"><div><h2>Typography</h2><p>기본 서체는 Apple SD Gothic Neo입니다. 제목, 본문, 라벨과 캡션의 크기·굵기·행간을 역할별로 구분합니다.</p></div></div><div className="type-table"><div className="table-row table-head"><span>Token</span><span>Size / line</span><span>Weight</span><span>Preview</span></div>{types.map(([name, size, weight]) => <div className="table-row" key={name}><code>{name}</code><span>{size}</span><span>{weight}</span><strong style={{ fontSize: `${Math.max(14, Number(size.split(" ")[0]))}px`, fontWeight: Number(weight) }}>모임 경험을 기록합니다</strong></div>)}</div></section>

      <section className="doc-section" id="spacing"><div className="doc-section-head"><div><h2>Spacing & radius</h2><p>간격은 2·4·8·16·24·28px 단계를 사용합니다. 관련성이 높은 요소에는 작은 간격을, 섹션과 행동 그룹에는 큰 간격을 적용합니다.</p></div></div><div className="token-columns"><div><h3>Spacing</h3>{[2,4,8,16,24,28].map((value) => <div className="measure-row" key={value}><code>spacing/{value}</code><span style={{ width: `${value * 3}px` }} /> <b>{value}px</b></div>)}</div><div><h3>Radius & effect</h3><div className="radius-samples"><div><i className="radius-6" /><code>radius/6</code></div><div><i className="radius-8" /><code>radius/8</code></div><div><i className="radius-full" /><code>radius/full</code></div></div><p className="token-note"><code>shadow/title</code><br />0 3px 6.8px 4px · #0000000A</p></div></div></section>

      <section className="doc-section" id="icons"><div className="doc-section-head"><div><h2>Icons</h2><p>아이콘은 24px 기본 크기로 사용합니다. 의미는 형태로 구분하고, 색상은 icon semantic token으로 상태와 위계를 표현합니다.</p></div></div><div className="icon-grid">{[["Profile","profile.svg"],["Menu vertical","menu-vertical.svg"],["Thumb up","thumb-up.svg"],["Lock","lock.svg"],["Add photo","add-photo.svg"]].map(([name, file]) => <div key={name}><img src={`/assets/${file}`} alt="" /><span>{name}</span><code>24px</code></div>)}</div></section>

      <section className="doc-section gap-section" id="gaps"><div className="doc-section-head"><div><h2>보강이 필요한 부분</h2><p>일관된 사용과 웹 확장을 위해 아래 기준을 추가로 정의해야 합니다.</p></div><StatusBadge kind="pending">정의 필요</StatusBadge></div><ul className="gap-list"><li><strong>Typography</strong><span>Apple SD Gothic Neo와 Pretendard의 혼용을 정리하고, 대체 서체와 예외 조건을 명시합니다.</span></li><li><strong>Color modes</strong><span>라이트·다크 모드에서 같은 의미를 유지하도록 semantic token의 색상 대응표를 정의합니다.</span></li><li><strong>Web interaction</strong><span>마우스와 키보드 사용을 위한 hover·focus-visible·pressed 상태를 추가합니다.</span></li><li><strong>Accessibility</strong><span>색상 대비, 최소 터치 영역, 텍스트 확대와 motion 감소 기준을 정의합니다.</span></li></ul></section>
    </DocsLayout>
  );
}
