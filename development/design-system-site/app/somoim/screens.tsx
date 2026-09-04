"use client";

import { useState } from "react";
import type { Gathering } from "./data";
import { REPORT_REASONS, SORT_OPTIONS } from "./data";
import {
  Badge,
  BottomSheet,
  Button,
  Chip,
  DetailMenu,
  GatheringCard,
  IconContainer,
  MeetingCard,
  ReviewItem,
  ReviewListHeader,
  SortButton,
  StatusBar,
  Tabs,
  Textbox,
  TitleBar,
  Toast,
  RadioButtonListItem,
  ViewAllButton,
} from "./components";
import { Heart, MenuHorizontal, Share } from "./icons";

/* ── 목록 ─────────────────────────────────── */
export function ListScreen({
  gatherings,
  onSelect,
}: {
  gatherings: Gathering[];
  onSelect: (id: string) => void;
}) {
  return (
    <>
      <StatusBar />
      <TitleBar title="서울 독서 모임" align="center" onBack={() => {}} />
      <div className="sm-scroll">
        <div className="sm-list">
          {gatherings.map((g) => (
            <GatheringCard key={g.id} gathering={g} onClick={() => onSelect(g.id)} />
          ))}
        </div>
      </div>
    </>
  );
}

/* ── 소모임 상세 ───────────────────────────── */
export function DetailScreen({
  gathering,
  onBack,
  onOpenReviews,
}: {
  gathering: Gathering;
  onBack: () => void;
  onOpenReviews: () => void;
}) {
  const [liked, setLiked] = useState(false);
  return (
    <>
      <StatusBar time="3:01" />
      <TitleBar
        title={gathering.navName}
        align="center"
        onBack={onBack}
        actions={
          <>
            <IconContainer onClick={() => setLiked((v) => !v)} label="찜하기">
              <Heart selected={liked} />
            </IconContainer>
            <IconContainer label="공유하기">
              <Share />
            </IconContainer>
            <IconContainer label="더보기">
              <MenuHorizontal />
            </IconContainer>
          </>
        }
      />
      <Tabs items={["홈", "게시판", "사진첩", "채팅"]} active={0} />
      <div className="sm-scroll">
        <img className="sm-banner" src={gathering.banner} alt="" />
        <div className="sm-info">
          <div className="sm-chips">
            <Chip>{gathering.region}</Chip>
            <Chip>{gathering.category}</Chip>
            <Chip>멤버 {gathering.members}</Chip>
          </div>
          <h1 className="sm-title-m-bold" style={{ margin: 0 }}>
            {gathering.name}
          </h1>
          <p className="sm-intro sm-body-m-regular" style={{ margin: 0 }}>
            {gathering.intro}
          </p>
        </div>

        <div className="sm-band" />
        <section className="sm-section">
          <h2 className="sm-section-title sm-title-s-medium" style={{ margin: 0 }}>
            정기모임
          </h2>
          {gathering.meetings.length > 0 ? gathering.meetings.map((m) => (
            <MeetingCard key={m.name + m.when} meeting={m} thumb={gathering.thumb} />
          )) : <p className="sm-empty sm-body-m-regular">예정된 정기모임이 없습니다.</p>}
        </section>

        <div className="sm-band" />
        <section>
          <ReviewListHeader count={gathering.reviewCount} trailing={gathering.reviewCount > 0 ? <ViewAllButton onClick={onOpenReviews} /> : undefined} />
          {gathering.reviews.slice(0, 2).map((r, i) => (
            <ReviewItem key={r.author} review={r} thumb={gathering.thumb} index={i} />
          ))}
          {gathering.reviews.length === 0 && <p className="sm-empty sm-body-m-regular">아직 등록된 후기가 없습니다.</p>}
        </section>

        <div className="sm-band" />
        <section className="sm-section">
          <h2 className="sm-section-title sm-title-s-medium" style={{ margin: 0 }}>모임 멤버</h2>
          <p className="sm-body-m-regular" style={{ margin: 0, color: "var(--text-neutral)" }}>
            현재 {gathering.members.toLocaleString("ko-KR")}명이 함께하고 있습니다.
          </p>
        </section>
      </div>
      <div className="sm-joinbar">
        <IconContainer onClick={() => setLiked((v) => !v)} label="찜하기" tone="filled">
          <Heart selected={liked} />
        </IconContainer>
        <Button full>모임 가입하기</Button>
      </div>
    </>
  );
}

/* ── 익명 후기 목록 ────────────────────────── */
export function ReviewListScreen({
  gathering,
  onBack,
  onOpenPost,
  onReport,
}: {
  gathering: Gathering;
  onBack: () => void;
  onOpenPost: () => void;
  onReport: () => void;
}) {
  const [sort, setSort] = useState(SORT_OPTIONS[0]);
  const [sheet, setSheet] = useState(false);
  const [menu, setMenu] = useState(false);

  const reviews = [...gathering.reviews];
  if (sort === "오래된 순") reviews.reverse();
  if (sort === "추천순") reviews.sort((a, b) => b.helpful - a.helpful);

  return (
    <>
      <StatusBar />
      <TitleBar
        title={gathering.name}
        align="left"
        onBack={onBack}
        actions={
          <>
            <IconContainer label="찜하기">
              <Heart />
            </IconContainer>
            <IconContainer label="공유하기">
              <Share />
            </IconContainer>
            <IconContainer label="더보기">
              <MenuHorizontal />
            </IconContainer>
          </>
        }
      />
      <div className="sm-scroll">
        <ReviewListHeader count={gathering.reviewCount} trailing={<SortButton value={sort} onClick={() => setSheet(true)} />} />
        {reviews.map((r, i) => (
          <div key={r.author} onClick={r.visibility === "public" ? onOpenPost : undefined}>
            <ReviewItem review={r} thumb={gathering.thumb} index={i} onMenu={() => setMenu(true)} />
          </div>
        ))}
        {reviews.length === 0 && <p className="sm-empty sm-body-m-regular">아직 등록된 후기가 없습니다.</p>}
      </div>
      {sheet && (
        <BottomSheet
          title="후기 정렬"
          items={SORT_OPTIONS}
          selected={sort}
          onSelect={(v) => {
            setSort(v);
            setSheet(false);
          }}
          onClose={() => setSheet(false)}
        />
      )}
      {menu && (
        <DetailMenu
          onClose={() => setMenu(false)}
          onReport={() => {
            setMenu(false);
            onReport();
          }}
        />
      )}
    </>
  );
}

/* ── 게시글 - 모임후기 ─────────────────────── */
export function PostScreen({ gathering, onBack }: { gathering: Gathering; onBack: () => void }) {
  const review = gathering.reviews.find((r) => r.visibility === "public") ?? gathering.reviews[0];
  return (
    <>
      <StatusBar time="10:30" />
      <TitleBar title="게시글" align="center" onBack={onBack} />
      <div className="sm-scroll">
        <div className="sm-post">
          <div className="sm-post-head">
            <img src="/somoim/avatar_1.png" alt="" />
            <div style={{ flex: 1 }}>
              <div className="sm-body-m-medium">모임장 · 나무늘보</div>
              <div className="sm-label-s-regular" style={{ color: "var(--text-alternative)" }}>
                {review.meetingWhen}
              </div>
            </div>
            <Badge>모임후기</Badge>
          </div>
          <h1 className="sm-title-s-medium" style={{ margin: 0 }}>
            {review.meetingName}
          </h1>
          <img className="sm-post-photo" src={gathering.banner} alt="" />
          <dl className="sm-meeting-detail sm-label-s-regular">
            <div className="sm-meeting-row">
              <dt>일시</dt>
              <dd>{review.meetingWhen}</dd>
            </div>
            <div className="sm-meeting-row">
              <dt>위치</dt>
              <dd>{review.meetingWhere}</dd>
            </div>
            <div className="sm-meeting-row">
              <dt>참석</dt>
              <dd>{review.meetingCount}</dd>
            </div>
          </dl>
          <p className="sm-body-m-regular" style={{ margin: 0, color: "var(--text-neutral)" }}>
            이 게시글에서 정모에 대한 이야기를 나눠보세요.
          </p>
          <div style={{ display: "flex", gap: 8 }}>
            <Button styleVariant="assistive" full>
              좋아요
            </Button>
            <Button styleVariant="assistive" full>
              댓글 달기
            </Button>
          </div>
        </div>
      </div>
    </>
  );
}

/* ── 후기 신고하기 ─────────────────────────── */
export function ReportScreen({
  gathering,
  onBack,
  onDone,
}: {
  gathering: Gathering;
  onBack: () => void;
  onDone: () => void;
}) {
  const [reason, setReason] = useState<string | null>(null);
  const [detail, setDetail] = useState("");
  const [toast, setToast] = useState<string | null>(null);

  const submit = () => {
    if (!reason) {
      setToast("신고 사유를 선택해주세요.");
      setTimeout(() => setToast(null), 1800);
      return;
    }
    setToast("신고가 완료되었습니다.");
    setTimeout(() => {
      setToast(null);
      onDone();
    }, 1400);
  };

  return (
    <>
      <StatusBar />
      <TitleBar
        title={gathering.name}
        align="left"
        onBack={onBack}
        actions={
          <IconContainer onClick={submit} type="text" state={reason ? "default" : "disabled"} label="신고 제출">
            <span className="sm-body-m-medium">제출</span>
          </IconContainer>
        }
      />
      <div className="sm-scroll">
        <div className="sm-report">
          <span className="sm-body-l-medium">신고 사유를 선택해주세요.</span>
          <div className="sm-radio-list">
            {REPORT_REASONS.map((r) => (
              <RadioButtonListItem key={r} label={r} selected={reason === r} onSelect={() => setReason(r)} />
            ))}
          </div>
          <span className="sm-body-l-medium">
            신고 내용 <span style={{ color: "var(--text-alternative)" }}>(선택)</span>
          </span>
          <Textbox value={detail} onChange={setDetail} placeholder="신고 사유를 간략하게 입력해주세요." />
          <span className="sm-label-s-regular" style={{ color: "var(--text-alternative)", textAlign: "right" }}>
            {detail.length}/500
          </span>
        </div>
      </div>
      {toast && <Toast message={toast} />}
    </>
  );
}
