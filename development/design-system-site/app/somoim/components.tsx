"use client";

// Figma 파일의 Components 페이지에 있는 컴포넌트를 그대로 옮긴 것.
// 배리언트 이름은 Figma 속성명을 따름 (Title Align, Style, Visibility, State, Type 등).

import { useState } from "react";
import type { Gathering, Meeting, Review } from "./data";
import {
  ArrowBackward,
  ArrowDown,
  Cross,
  Heart,
  Lock,
  MenuVertical,
  Report,
  Share,
  ThumbUp,
} from "./icons";

/* ── Status Bar ───────────────────────────── */
export function StatusBar({ time = "3:31" }: { time?: string }) {
  return (
    <div className="sm-status">
      <span>{time}</span>
      <span className="sm-status-right">
        <svg width="18" height="12" viewBox="0 0 18 12" fill="none" aria-hidden>
          <rect x="0" y="7" width="3" height="5" rx="1" fill="currentColor" />
          <rect x="5" y="5" width="3" height="7" rx="1" fill="currentColor" />
          <rect x="10" y="2" width="3" height="10" rx="1" fill="currentColor" />
          <rect x="15" y="0" width="3" height="12" rx="1" fill="currentColor" opacity="0.35" />
        </svg>
        <svg width="16" height="12" viewBox="0 0 16 12" fill="none" aria-hidden>
          <path d="M8 10.5l-.01.01M2 5.5a9 9 0 0112 0M4.5 8a5.5 5.5 0 017 0" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" />
        </svg>
        <svg width="24" height="12" viewBox="0 0 24 12" fill="none" aria-hidden>
          <rect x="0.5" y="0.5" width="20" height="11" rx="3" stroke="currentColor" opacity="0.5" />
          <rect x="2" y="2" width="17" height="8" rx="2" fill="currentColor" />
          <rect x="22" y="4" width="2" height="4" rx="1" fill="currentColor" opacity="0.5" />
        </svg>
      </span>
    </div>
  );
}

/* ── Icon Container (Type=Default|Text, State=Default|Disabled) ── */
export function IconContainer({
  children,
  onClick,
  type = "default",
  state = "default",
  tone,
  label,
}: {
  children: React.ReactNode;
  onClick?: () => void;
  type?: "default" | "text";
  state?: "default" | "disabled";
  tone?: "filled";
  label: string;
}) {
  return (
    <button
      type="button"
      className="sm-icon-btn"
      data-type={type}
      data-state={state}
      data-tone={tone}
      onClick={onClick}
      disabled={state === "disabled"}
      aria-label={label}
    >
      {children}
    </button>
  );
}

/* ── Title Bar (Title Align=Left|Center) ──── */
export function TitleBar({
  title,
  align = "center",
  onBack,
  actions,
  titleClassName = "sm-body-l-medium",
}: {
  title: string;
  align?: "left" | "center";
  onBack?: () => void;
  actions?: React.ReactNode;
  titleClassName?: string;
}) {
  return (
    <div className="sm-titlebar" data-align={align}>
      {onBack && (
        <IconContainer onClick={onBack} label="뒤로가기">
          <ArrowBackward />
        </IconContainer>
      )}
      <div className={`sm-titlebar-title ${titleClassName}`}>{title}</div>
      <div className="sm-titlebar-actions">{actions}</div>
    </div>
  );
}

/* ── Tabs ─────────────────────────────────── */
export function Tabs({ items, active = 0 }: { items: string[]; active?: number }) {
  return (
    <div className="sm-tabs">
      {items.map((it, i) => (
        <button key={it} type="button" className="sm-tab sm-body-m-medium" data-active={i === active}>
          {it}
          <i />
        </button>
      ))}
    </div>
  );
}

/* ── Chip / Badge ─────────────────────────── */
export function Chip({ children }: { children: React.ReactNode }) {
  return <span className="sm-chip sm-label-s-regular">{children}</span>;
}

export function Badge({ children }: { children: React.ReactNode }) {
  return <span className="sm-badge sm-label-s-medium">{children}</span>;
}

/* ── Button Medium (Style=Default|Inverse) ── */
export function Button({
  children,
  onClick,
  styleVariant = "default",
  full = false,
  disabled = false,
}: {
  children: React.ReactNode;
  onClick?: () => void;
  styleVariant?: "default" | "inverse" | "assistive";
  full?: boolean;
  disabled?: boolean;
}) {
  return (
    <button
      type="button"
      className="sm-btn sm-label-l-medium"
      data-style={styleVariant}
      data-full={full}
      onClick={onClick}
      disabled={disabled}
    >
      {children}
    </button>
  );
}

/* ── 모임 목록 카드 ────────────────────────── */
export function GatheringCard({ gathering, onClick }: { gathering: Gathering; onClick: () => void }) {
  return (
    <button type="button" className="sm-card" onClick={onClick}>
      <img className="sm-card-thumb" src={gathering.thumb} alt="" />
      <span className="sm-card-body">
        <span className="sm-card-title sm-body-l-medium">{gathering.name}</span>
        <span className="sm-card-desc sm-body-m-regular">{gathering.desc}</span>
        <span className="sm-card-meta sm-label-s-regular">
          {gathering.category} · {gathering.region} · 멤버 {gathering.members} <em>{gathering.recent}</em>
        </span>
      </span>
    </button>
  );
}

/* ── 정기모임 카드 ─────────────────────────── */
export function MeetingCard({ meeting, thumb }: { meeting: Meeting; thumb: string }) {
  const [liked, setLiked] = useState(false);
  return (
    <div className="sm-meeting">
      <div className="sm-meeting-head">
        <Badge>{meeting.badge}</Badge>
        <span className="sm-body-l-bold">{meeting.name}</span>
      </div>
      <div className="sm-meeting-mid">
        <dl className="sm-meeting-detail sm-label-s-regular">
          <div className="sm-meeting-row">
            <dt>일시</dt>
            <dd>{meeting.when}</dd>
          </div>
          <div className="sm-meeting-row">
            <dt>위치</dt>
            <dd>{meeting.where}</dd>
          </div>
          <div className="sm-meeting-row">
            <dt>비용</dt>
            <dd>{meeting.cost}</dd>
          </div>
          <div className="sm-meeting-row">
            <dt />
            <dd>{meeting.attend}</dd>
          </div>
        </dl>
        <img className="sm-meeting-thumb" src={thumb} alt="" />
      </div>
      <div className="sm-meeting-actions">
        <IconContainer onClick={() => setLiked((v) => !v)} label="찜하기">
          <Heart selected={liked} />
        </IconContainer>
        <IconContainer label="공유하기">
          <Share />
        </IconContainer>
        <Button styleVariant="inverse" full>
          {meeting.cta}
        </Button>
      </div>
    </div>
  );
}

/* ── Participated Gathering Card (Visibility=Public|Private) ── */
export function ParticipatedGatheringCard({ review, thumb }: { review: Review; thumb: string }) {
  if (review.visibility === "private") {
    return (
      <div className="sm-meetcard" data-visibility="private">
        <Lock size={20} />
        <span className="sm-meetcard-body sm-label-s-regular">참여한 정기모임 비공개</span>
      </div>
    );
  }
  return (
    <div className="sm-meetcard" data-visibility="public">
      <div className="sm-meetcard-body">
        <span className="sm-meetcard-label sm-label-s-regular">참여한 정기모임</span>
        <span className="sm-meetcard-name sm-body-m-medium">{review.meetingName}</span>
        <span className="sm-meetcard-meta sm-label-s-regular">
          {review.meetingWhen} · {review.meetingWhere} · {review.meetingCount}
        </span>
      </div>
      <img src={thumb} alt="" />
    </div>
  );
}

/* ── Review Item (Type=Default|Reported) ──── */
export function ReviewItem({
  review,
  thumb,
  index,
  type = "default",
  onMenu,
}: {
  review: Review;
  thumb: string;
  index: number;
  type?: "default" | "reported";
  onMenu?: () => void;
}) {
  const [expanded, setExpanded] = useState(false);
  const [helpful, setHelpful] = useState(false);
  const long = review.body.length > 90;

  if (type === "reported") {
    return (
      <div className="sm-review" data-type="reported">
        <span className="sm-body-m-regular sm-reported-note">신고 접수로 검토 중인 후기입니다</span>
      </div>
    );
  }

  return (
    <div className="sm-review" data-type="default">
      <div className="sm-review-top">
        <img src={`/somoim/avatar_${(index % 3) + 1}.png`} alt="" />
        <span className="sm-review-author sm-body-m-medium">{review.author}</span>
        <span className="sm-review-date sm-label-s-regular">{review.date}</span>
        <IconContainer onClick={onMenu} label="후기 메뉴">
          <MenuVertical size={20} />
        </IconContainer>
      </div>
      <p className="sm-review-body sm-body-m-regular">
        {long && !expanded ? `${review.body.slice(0, 90)}…` : review.body}
      </p>
      {long && !expanded && (
        <button type="button" className="sm-review-more sm-body-m-regular" onClick={() => setExpanded(true)}>
          더보기
        </button>
      )}
      <ParticipatedGatheringCard review={review} thumb={thumb} />
      <button type="button" className="sm-helpful sm-label-m-regular" data-on={helpful} onClick={() => setHelpful((v) => !v)}>
        <ThumbUp size={20} filled={helpful} />
        도움이 됐어요 {review.helpful + (helpful ? 1 : 0)}
      </button>
    </div>
  );
}

/* ── 익명 후기 헤더 + 목록 ─────────────────── */
export function ReviewListHeader({
  count,
  trailing,
}: {
  count: number;
  trailing?: React.ReactNode;
}) {
  return (
    <div className="sm-review-head">
      <span className="sm-review-count sm-title-s-medium">
        <b>익명 후기</b>
        <span className="sm-body-l-regular">({count})</span>
      </span>
      {trailing}
    </div>
  );
}

export function SortButton({ value, onClick }: { value: string; onClick: () => void }) {
  return (
    <button type="button" className="sm-icon-btn sm-body-m-regular" data-type="text" onClick={onClick}>
      {value}
      <ArrowDown size={20} />
    </button>
  );
}

export function ViewAllButton({ onClick }: { onClick: () => void }) {
  return (
    <button type="button" className="sm-icon-btn sm-body-m-regular" data-type="text" onClick={onClick}>
      모임 후기 더보기
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" aria-hidden>
        <path d="M9 5l7 7-7 7" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    </button>
  );
}

/* ── Bottom Sheet + Item (State=Default|Pressed) ── */
export function BottomSheet({
  title,
  items,
  selected,
  onSelect,
  onClose,
}: {
  title: string;
  items: string[];
  selected: string;
  onSelect: (v: string) => void;
  onClose: () => void;
}) {
  const [pressed, setPressed] = useState<string | null>(null);
  return (
    <div className="sm-overlay" onClick={onClose}>
      <div className="sm-sheet" onClick={(e) => e.stopPropagation()}>
        <div className="sm-sheet-head">
          <span className="sm-body-l-medium">{title}</span>
          <IconContainer onClick={onClose} label="닫기">
            <Cross size={20} />
          </IconContainer>
        </div>
        {items.map((it) => (
          <button
            key={it}
            type="button"
            className="sm-sheet-item sm-body-l-regular"
            data-state={pressed === it ? "pressed" : "default"}
            data-selected={selected === it}
            onPointerDown={() => setPressed(it)}
            onPointerUp={() => setPressed(null)}
            onClick={() => onSelect(it)}
          >
            {selected === it && <Check size={18} />}
            {it}
          </button>
        ))}
      </div>
    </div>
  );
}

function Check({ size = 24 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none" aria-hidden>
      <path d="M5 12.5l4.5 4.5L19 7.5" stroke="currentColor" strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  );
}

/* ── Detail Menu ──────────────────────────── */
export function DetailMenu({ onReport, onClose }: { onReport: () => void; onClose: () => void }) {
  return (
    <>
      <div className="sm-overlay" style={{ background: "transparent" }} onClick={onClose} />
      <div className="sm-menu sm-body-m-regular">
        <button type="button" onClick={onReport}>
          <Report size={20} />
          신고하기
        </button>
      </div>
    </>
  );
}

/* ── Toast ────────────────────────────────── */
export function Toast({ message }: { message: string }) {
  return <div className="sm-toast sm-body-m-regular">{message}</div>;
}

/* ── Radio Button (Selected=True|False) ───── */
export function RadioButtonListItem({
  label,
  selected,
  onSelect,
}: {
  label: string;
  selected: boolean;
  onSelect: () => void;
}) {
  return (
    <button type="button" className="sm-radio sm-body-m-regular" data-selected={selected} onClick={onSelect}>
      <i />
      {label}
    </button>
  );
}

/* ── Textbox (State=Default|Focused|Filled|Disabled) ── */
export function Textbox({
  value,
  onChange,
  placeholder,
  maxLength = 500,
}: {
  value: string;
  onChange: (v: string) => void;
  placeholder: string;
  maxLength?: number;
}) {
  return (
    <textarea
      className="sm-textbox sm-body-m-regular"
      value={value}
      placeholder={placeholder}
      maxLength={maxLength}
      onChange={(e) => onChange(e.target.value)}
    />
  );
}
