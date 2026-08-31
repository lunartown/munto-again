import Link from "next/link";
import { SiteShell } from "./ui/site-shell";
import { GatheringCard, Textbox, Toggle } from "./ui/system-components";

const figmaComponents =
  "https://www.figma.com/design/jMx6ZzITwZJAeaiVee9xsG/%EC%B5%9C%EB%AA%85%ED%95%98%EB%8B%98?node-id=617-578&p=f";
const figmaPrototype =
  "https://www.figma.com/design/jMx6ZzITwZJAeaiVee9xsG/%EC%B5%9C%EB%AA%85%ED%95%98%EB%8B%98?node-id=551-6737&p=f";

export default function Home() {
  return (
    <SiteShell>
      <main>
        <section className="hero" aria-labelledby="hero-title">
          <div className="hero-copy">
            <p className="eyebrow">SOMOIM DESIGN SYSTEM · DRAFT 01</p>
            <h1 id="hero-title">모임 경험을<br />설명 가능한 UI로</h1>
            <p className="hero-description">
              소모임 후기 경험에 실제로 사용된 토큰과 컴포넌트를 먼저 정리합니다.
              완성된 라이브러리를 선언하기보다, 확인된 것과 보강할 것을 함께 보여주는
              작업형 문서입니다.
            </p>
            <div className="hero-actions">
              <Link className="button button-primary" href="/foundations">Foundations 보기</Link>
              <Link className="button button-secondary" href="/components">Components 보기</Link>
            </div>
          </div>

          <div className="hero-stage" aria-label="디자인 시스템 컴포넌트 미리보기">
            <div className="stage-card stage-card-main">
              <div className="stage-heading">
                <span>참여한 정기모임</span>
                <span className="stage-toggle">공개 <Toggle initialState /></span>
              </div>
              <GatheringCard variant="minimal" />
              <div className="stage-field">
                <span>모임 후기</span>
                <Textbox compact />
              </div>
            </div>
            <div className="stage-orbit orbit-one" />
            <div className="stage-orbit orbit-two" />
          </div>
        </section>

        <section className="section-block" aria-labelledby="scope-title">
          <div className="section-heading-row">
            <div><p className="eyebrow">CURRENT SCOPE</p><h2 id="scope-title">지금 문서가 다루는 범위</h2></div>
            <p className="section-summary">Figma의 자산 페이지와 후기 프로토타입에서 직접 확인된 항목만 1차 범위로 잡았습니다.</p>
          </div>
          <div className="scope-grid">
            <article className="scope-card accent-blue">
              <span className="scope-index">01</span><h3>Foundations</h3>
              <p>색상, 타이포그래피, 간격, 반경, 그림자와 아이콘의 현재 정의를 확인합니다.</p>
              <Link href="/foundations">토큰 살펴보기 →</Link>
            </article>
            <article className="scope-card accent-coral">
              <span className="scope-index">02</span><h3>Core components</h3>
              <p>후기 흐름에서 반복되고 상태가 확인된 세 컴포넌트를 우선 문서화합니다.</p>
              <Link href="/components">컴포넌트 살펴보기 →</Link>
            </article>
            <article className="scope-card accent-green">
              <span className="scope-index">03</span><h3>Next coverage</h3>
              <p>화면에는 있지만 정의가 덜 된 항목과 웹 전환 시 필요한 상태를 구분합니다.</p>
              <Link href="/roadmap">보강 계획 보기 →</Link>
            </article>
          </div>
        </section>

        <section className="section-block source-section" aria-labelledby="source-title">
          <div><p className="eyebrow">SOURCE MAP</p><h2 id="source-title">두 원본을 연결해 문서화합니다</h2></div>
          <div className="source-list">
            <a href={figmaComponents} target="_blank" rel="noreferrer"><span className="source-type">Library</span><strong>Components · Variables · Styles</strong><span>Figma node 617:578 ↗</span></a>
            <a href={figmaPrototype} target="_blank" rel="noreferrer"><span className="source-type">Usage</span><strong>Review flow prototype</strong><span>Figma node 551:6737 ↗</span></a>
          </div>
        </section>

        <section className="section-block status-section" aria-labelledby="status-title">
          <div><p className="eyebrow">DOCUMENT STATUS</p><h2 id="status-title">완성도도 정보입니다</h2></div>
          <div className="status-grid">
            <div><span className="status-dot verified" /><strong>확인됨</strong><p>Figma 원본과 프로토타입에서 직접 확인</p></div>
            <div><span className="status-dot chosen" /><strong>문서화 선택</strong><p>현재 범위를 만들기 위해 우선순위를 정함</p></div>
            <div><span className="status-dot pending" /><strong>보강 필요</strong><p>상태, 규칙 또는 접근성 정의가 아직 부족함</p></div>
          </div>
        </section>
      </main>
    </SiteShell>
  );
}
