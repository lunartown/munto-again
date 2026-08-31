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
            <p className="eyebrow">SOMOIM DESIGN SYSTEM</p>
            <h1 id="hero-title">모임 경험을<br />설명 가능한 UI로</h1>
            <p className="hero-description">
              탐색부터 후기 작성과 조회까지, 소모임의 경험을 일관된 시각 언어와
              재사용 가능한 컴포넌트로 연결합니다.
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
            <div><p className="eyebrow">SYSTEM OVERVIEW</p><h2 id="scope-title">디자인 시스템의 구성</h2></div>
            <p className="section-summary">기초 스타일이 공통 기준을 만들고, 컴포넌트와 사용 가이드가 제품 화면에서 같은 경험을 이어갑니다.</p>
          </div>
          <div className="scope-grid">
            <article className="scope-card accent-blue">
              <span className="scope-index">01</span><h3>Foundations</h3>
              <p>색상, 타이포그래피, 간격, 반경, 그림자와 아이콘의 공통 기준을 제공합니다.</p>
              <Link href="/foundations">토큰 살펴보기 →</Link>
            </article>
            <article className="scope-card accent-coral">
              <span className="scope-index">02</span><h3>Core components</h3>
              <p>후기 작성과 조회 전반에서 재사용되는 UI의 구조와 상태를 설명합니다.</p>
              <Link href="/components">컴포넌트 살펴보기 →</Link>
            </article>
            <article className="scope-card accent-green">
              <span className="scope-index">03</span><h3>Growth plan</h3>
              <p>접근성, 웹 인터랙션과 운영 규칙까지 확장하는 순서를 제시합니다.</p>
              <Link href="/roadmap">확장 계획 보기 →</Link>
            </article>
          </div>
        </section>

        <section className="section-block source-section" aria-labelledby="source-title">
          <div><p className="eyebrow">DESIGN SOURCE</p><h2 id="source-title">디자인과 제품 화면을 함께 봅니다</h2></div>
          <div className="source-list">
            <a href={figmaComponents} target="_blank" rel="noreferrer"><span className="source-type">Library</span><strong>Components · Variables · Styles</strong><span>컴포넌트 라이브러리 열기 ↗</span></a>
            <a href={figmaPrototype} target="_blank" rel="noreferrer"><span className="source-type">Screens</span><strong>Review experience flow</strong><span>후기 화면 열기 ↗</span></a>
          </div>
        </section>

        <section className="section-block status-section" aria-labelledby="status-title">
          <div><p className="eyebrow">SYSTEM PRINCIPLES</p><h2 id="status-title">일관된 경험을 만드는 기준</h2></div>
          <div className="status-grid">
            <div><span className="status-dot verified" /><strong>일관성</strong><p>같은 의미는 같은 토큰과 컴포넌트로 표현합니다.</p></div>
            <div><span className="status-dot chosen" /><strong>맥락</strong><p>모임 정보와 사용자 행동의 관계가 화면에서 이어지게 합니다.</p></div>
            <div><span className="status-dot pending" /><strong>접근성</strong><p>상태는 색상뿐 아니라 형태와 텍스트로도 전달합니다.</p></div>
          </div>
        </section>
      </main>
    </SiteShell>
  );
}
