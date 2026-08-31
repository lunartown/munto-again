"use client";

import { useEffect, useState } from "react";

export function ThemeToggle() {
  const [dark, setDark] = useState(false);
  useEffect(() => { document.documentElement.dataset.theme = dark ? "dark" : "light"; }, [dark]);
  return <button className="theme-toggle" type="button" aria-label={dark ? "라이트 모드로 전환" : "다크 모드로 전환"} onClick={() => setDark((value) => !value)}><span aria-hidden="true">{dark ? "☀" : "◐"}</span></button>;
}

export function Toggle({ initialState = true }: { initialState?: boolean }) {
  const [on, setOn] = useState(initialState);
  return <button type="button" className="toggle-control" aria-pressed={on} aria-label={on ? "공개 설정 끄기" : "공개 설정 켜기"} onClick={() => setOn((value) => !value)}><img src={on ? "/assets/toggle-true.svg" : "/assets/toggle-false.svg"} alt="" /></button>;
}

type GatheringVariant = "default" | "minimal" | "list" | "private";

export function GatheringCard({ variant = "default" }: { variant?: GatheringVariant }) {
  if (variant === "private") return <div className="gathering-card gathering-private"><img src="/assets/lock.svg" alt="" /><span>참여한 정기모임 비공개</span></div>;
  return (
    <div className={`gathering-card gathering-${variant}`}>
      {variant === "list" && <img className="gathering-list-image" src="/assets/gathering-cover.png" alt="" />}
      <div className="gathering-content">
        {variant === "default" && <span className="gathering-label">참여한 정기모임</span>}
        <strong>🔥 9월지정독서[그저 하루치의 낙담]</strong>
        <span className="gathering-meta">8월 7일 오후 7:00 · 강남구 · 8명 참석</span>
      </div>
      {variant === "default" && <img className="gathering-cover" src="/assets/gathering-cover.png" alt="독서 모임 표지" />}
    </div>
  );
}

export type TextboxState = "default" | "focused" | "filled" | "disabled";

export function Textbox({ state = "default", compact = false }: { state?: TextboxState; compact?: boolean }) {
  const filled = state === "filled" || state === "focused";
  return <div className={`textbox-demo textbox-${state} ${compact ? "textbox-compact" : ""}`}><div className="textbox-surface">{filled ? "첫 참석이었는데 진행 방식이 친절해서 편하게 참여할 수 있었어요." : "모임에 참여한 경험을 솔직하게 작성해주세요."}</div><span>{filled ? "35" : "0"}/500</span></div>;
}

export function ReviewItem({ reported = false }: { reported?: boolean }) {
  return (
    <article className="review-item">
      <header><div className="review-profile"><img src="/assets/profile.svg" alt="" /><strong>강렬한 토끼</strong></div><div className="review-time"><span>8월 9일 오후 6:48{!reported && "(수정됨)"}</span><img src="/assets/menu-vertical.svg" alt="더보기" /></div></header>
      {reported ? <p className="reported-copy">신고 누적으로 검토 중인 후기입니다. <u>펼치기</u></p> : <><p>첫 참석이었는데 분위기가 편해서 좋았습니다. 같은 책을 읽고도 이야기하는 지점이 달라 두 시간이 짧게 느껴졌어요.</p><GatheringCard /><button className="helpful-button" type="button"><img src="/assets/thumb-up.svg" alt="" /> 도움이 됐어요 10</button></>}
    </article>
  );
}

export function TextboxStateDemo() {
  const states: { id: TextboxState; label: string }[] = [{ id: "default", label: "Default" },{ id: "focused", label: "Focused" },{ id: "filled", label: "Filled" },{ id: "disabled", label: "Disabled" }];
  const [state, setState] = useState<TextboxState>("default");
  return <div className="interactive-preview"><div className="segmented-control" role="group" aria-label="Textbox 상태">{states.map((item) => <button type="button" key={item.id} className={state === item.id ? "active" : ""} onClick={() => setState(item.id)}>{item.label}</button>)}</div><Textbox state={state} /></div>;
}

export function GatheringVariantDemo() {
  const variants: { id: GatheringVariant; label: string }[] = [{ id: "default", label: "Card Default" },{ id: "minimal", label: "Card Minimal" },{ id: "list", label: "List Item" },{ id: "private", label: "Private" }];
  const [variant, setVariant] = useState<GatheringVariant>("default");
  return <div className="interactive-preview"><div className="segmented-control" role="group" aria-label="카드 변형">{variants.map((item) => <button type="button" key={item.id} className={variant === item.id ? "active" : ""} onClick={() => setVariant(item.id)}>{item.label}</button>)}</div><GatheringCard variant={variant} /></div>;
}

export function ReviewStateDemo() {
  const [reported, setReported] = useState(false);
  return <div className="interactive-preview"><div className="segmented-control" role="group" aria-label="후기 상태"><button type="button" className={!reported ? "active" : ""} onClick={() => setReported(false)}>Default</button><button type="button" className={reported ? "active" : ""} onClick={() => setReported(true)}>Reported</button></div><ReviewItem reported={reported} /></div>;
}
