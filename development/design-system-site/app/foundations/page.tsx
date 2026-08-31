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
      <PageIntro eyebrow="FOUNDATIONS" title="Foundations" description="후기 프로토타입과 핵심 컴포넌트에 연결된 변수만 우선 수집했습니다. 전체 팔레트를 새로 만들지 않고, 현재 쓰이는 의미 토큰을 문서화합니다." />

      <section className="doc-section" id="color"><div className="doc-section-head"><div><h2>Color</h2><p>원시 색상보다 UI 역할이 드러나는 semantic token을 기준으로 표시합니다.</p></div><StatusBadge kind="verified">Figma 확인</StatusBadge></div><div className="color-grid">{colors.map(([name, value]) => <div className="color-token" key={name}><div style={{ background: value }} /><strong>{name}</strong><code>{value}</code></div>)}</div></section>

      <section className="doc-section" id="typography"><div className="doc-section-head"><div><h2>Typography</h2><p>Primary family는 Apple SD Gothic Neo로 연결되어 있습니다.</p></div><StatusBadge kind="verified">Figma 확인</StatusBadge></div><div className="type-table"><div className="table-row table-head"><span>Token</span><span>Size / line</span><span>Weight</span><span>Preview</span></div>{types.map(([name, size, weight]) => <div className="table-row" key={name}><code>{name}</code><span>{size}</span><span>{weight}</span><strong style={{ fontSize: `${Math.max(14, Number(size.split(" ")[0]))}px`, fontWeight: Number(weight) }}>모임 경험을 기록합니다</strong></div>)}</div></section>

      <section className="doc-section" id="spacing"><div className="doc-section-head"><div><h2>Spacing & radius</h2><p>현재 화면에서 확인된 단계만 보여줍니다.</p></div><StatusBadge kind="verified">Figma 확인</StatusBadge></div><div className="token-columns"><div><h3>Spacing</h3>{[2,4,8,16,24,28].map((value) => <div className="measure-row" key={value}><code>spacing/{value}</code><span style={{ width: `${value * 3}px` }} /> <b>{value}px</b></div>)}</div><div><h3>Radius & effect</h3><div className="radius-samples"><div><i className="radius-6" /><code>radius/6</code></div><div><i className="radius-8" /><code>radius/8</code></div><div><i className="radius-full" /><code>radius/full</code></div></div><p className="token-note"><code>shadow/title</code><br />0 3px 6.8px 4px · #0000000A</p></div></div></section>

      <section className="doc-section" id="icons"><div className="doc-section-head"><div><h2>Icons</h2><p>컴포넌트 페이지에서 Profile, Menu, Arrow, Share, Lock 등 18개 아이콘이 확인됩니다.</p></div><StatusBadge kind="chosen">일부 표시</StatusBadge></div><div className="icon-grid">{[["Profile","profile.svg"],["Menu vertical","menu-vertical.svg"],["Thumb up","thumb-up.svg"],["Lock","lock.svg"],["Add photo","add-photo.svg"]].map(([name, file]) => <div key={name}><img src={`/assets/${file}`} alt="" /><span>{name}</span><code>24px</code></div>)}</div></section>

      <section className="doc-section gap-section" id="gaps"><div className="doc-section-head"><div><h2>현재 보강이 필요한 부분</h2><p>미확인 내용을 규칙으로 확정하지 않고 다음 확인 대상으로 남깁니다.</p></div><StatusBadge kind="pending">보강 필요</StatusBadge></div><ul className="gap-list"><li><strong>Typography</strong><span>Primary family는 Apple SD Gothic Neo지만 일부 레이어에 Pretendard가 직접 지정되어 있어 의도된 예외인지 확인이 필요합니다.</span></li><li><strong>Color modes</strong><span>현재 확인된 것은 기본 모드입니다. 다크 모드용 semantic mapping은 아직 Figma 근거가 없습니다.</span></li><li><strong>Web interaction</strong><span>모바일 중심 자산이라 hover·keyboard focus 토큰과 상태 정의가 비어 있습니다.</span></li><li><strong>Accessibility</strong><span>색상 대비, 최소 터치 영역, motion 기준은 별도 검증이 필요합니다.</span></li></ul></section>
    </DocsLayout>
  );
}
