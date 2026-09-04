"use client";

import { useEffect, useRef, useState } from "react";
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
      <StatusBar time="8:58" />
      <TitleBar title="맞춤 모임" align="center" onBack={() => {}} titleClassName="sm-title-s-medium" />
      <div className="sm-category-tabs" role="tablist" aria-label="모임 카테고리">
        {["맞춤추천", "인문학/책/글", "문화/공연/축제", "음악/악기"].map((label, index) => (
          <button key={label} type="button" className="sm-category-tab" data-active={index === 0}>{label}</button>
        ))}
      </div>
      <div className="sm-scroll">
        <div className="sm-list">
          {gatherings.map((g) => (
            <GatheringCard key={g.id} gathering={g} onClick={() => onSelect(g.id)} />
          ))}
        </div>
      </div>
      <button type="button" className="sm-fab sm-fab-list" aria-label="모임 만들기">+</button>
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
  const [activeTab, setActiveTab] = useState(0);
  const [toast, setToast] = useState<string | null>(null);
  const toastTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => () => {
    if (toastTimer.current) clearTimeout(toastTimer.current);
  }, []);

  const showMemberOnly = () => {
    if (toastTimer.current) clearTimeout(toastTimer.current);
    setToast("모임 멤버에게만 공개됩니다");
    toastTimer.current = setTimeout(() => setToast(null), 1800);
  };

  const selectTab = (index: number) => {
    if (index === 3) {
      showMemberOnly();
      return;
    }
    setActiveTab(index);
  };

  return (
    <>
      <StatusBar time="3:01" island />
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
      <Tabs items={["홈", "게시판", "사진첩", "채팅"]} active={activeTab} onSelect={selectTab} />
      <div className="sm-scroll">
        {activeTab === 0 && (
          <>
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
                <MeetingCard key={m.name + m.when} meeting={m} />
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
          </>
        )}
        {activeTab === 1 && <CommunityBoard gathering={gathering} onRestricted={showMemberOnly} />}
        {activeTab === 2 && <PhotoGallery gathering={gathering} onRestricted={showMemberOnly} />}
      </div>
      <div className="sm-joinbar">
        <IconContainer onClick={() => setLiked((v) => !v)} label="찜하기" tone="filled">
          <Heart selected={liked} />
        </IconContainer>
        <Button full>모임 가입하기</Button>
      </div>
      {toast && <Toast message={toast} />}
    </>
  );
}

const BOARD_FILTERS = ["전체", "공지", "모임후기", "가입인사", "자유", "관심사"];

function CommunityBoard({
  gathering,
  onRestricted,
}: {
  gathering: Gathering;
  onRestricted: () => void;
}) {
  const [filter, setFilter] = useState("전체");
  const meeting = gathering.meetings[0];
  const posts = [
    { category: "공지", author: "모임장", when: "", title: "모임 활동 및 게시판 이용 안내", body: "새로 오신 분들은 공지와 가입인사를 확인해주세요.", likes: 8, comments: 3, pinned: true },
    { category: "가입인사", author: "새 멤버", when: "방금 전", title: "안녕하세요! 잘 부탁드립니다", body: `${gathering.category}를 좋아해서 가입했습니다. 반갑습니다.`, likes: 1, comments: 1 },
    { category: "모임후기", author: "모임 멤버", when: "어제", title: "즐거웠던 정기모임 후기", body: "함께 이야기 나눌 수 있어 즐거웠어요. 다음 모임도 기대됩니다.", likes: 3, comments: 2 },
    { category: "가입인사", author: "새 멤버", when: "2일 전", title: "가입인사 드립니다", body: "처음 참여합니다. 모임에서 뵙겠습니다!", likes: 2, comments: 1 },
  ];
  const visiblePosts = filter === "전체" ? posts : posts.filter((post) => post.category === filter);

  return (
    <section className="sm-board" aria-label="게시판">
      <div className="sm-board-filters" aria-label="게시글 분류">
        {BOARD_FILTERS.map((item) => (
          <button
            key={item}
            type="button"
            className="sm-board-filter sm-label-s-medium"
            data-active={filter === item}
            onClick={() => setFilter(item)}
          >
            {item}
          </button>
        ))}
      </div>
      {meeting && (filter === "전체" || filter === "모임후기") && (
        <button type="button" className="sm-board-meeting" onClick={onRestricted}>
          <span className="sm-board-meeting-icon" aria-hidden>⌂</span>
          <span>
            <b className="sm-body-m-medium">{meeting.name}</b>
            <small className="sm-label-s-regular">{meeting.when}{meeting.where ? ` · ${meeting.where}` : ""}</small>
          </span>
          <span aria-hidden>→</span>
        </button>
      )}
      <div className="sm-board-posts">
        {visiblePosts.map((post) => (
          <button key={post.title} type="button" className="sm-board-post" onClick={onRestricted}>
            <span className="sm-board-post-head">
              <span className="sm-board-avatar" aria-hidden>{post.author.slice(0, 1)}</span>
              <span className="sm-body-m-medium">{post.author}</span>
              <time className="sm-label-s-regular">{post.when}</time>
            </span>
            <span className="sm-board-post-title sm-body-m-medium">
              {post.pinned && <em>필독</em>}{post.title}
            </span>
            <span className="sm-board-post-body sm-body-m-regular">{post.body}</span>
            <span className="sm-board-post-meta sm-label-s-regular">♡ 좋아요 {post.likes}　▢ 댓글 {post.comments}<i>{post.category}</i></span>
          </button>
        ))}
        {visiblePosts.length === 0 && <p className="sm-empty sm-body-m-regular">등록된 게시글이 없습니다.</p>}
      </div>
    </section>
  );
}

const GALLERY_IMAGES = [
  "/somoim/banner_c1.png",
  "/somoim/thumb_c2.png",
  "/somoim/banner_c3.png",
  "/somoim/thumb_c4.png",
  "/somoim/banner_c2.png",
  "/somoim/thumb_c1.png",
  "/somoim/banner_c4.png",
  "/somoim/thumb_c3.png",
  "/somoim/thumb_c1.png",
  "/somoim/banner_c3.png",
  "/somoim/thumb_c2.png",
  "/somoim/banner_c4.png",
];

function PhotoGallery({
  gathering,
  onRestricted,
}: {
  gathering: Gathering;
  onRestricted: () => void;
}) {
  return (
    <section className="sm-gallery" aria-label="사진첩">
      {GALLERY_IMAGES.map((image, index) => (
        <button
          key={`${image}-${index}`}
          type="button"
          className="sm-gallery-item"
          onClick={onRestricted}
          aria-label={`${gathering.name} 활동 사진 ${index + 1}`}
        >
          <img src={index === 0 ? gathering.banner : image} alt="" />
          <span className="sm-label-s-medium">♡ {index % 3 + 1}　▢ {index % 2 + 1}</span>
        </button>
      ))}
    </section>
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
        align="center"
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
          <div className="sm-review-wrap" key={r.author} onClick={r.visibility === "public" ? onOpenPost : undefined}>
            <ReviewItem review={r} thumb={gathering.thumb} index={i} onMenu={() => setMenu(true)} />
          </div>
        ))}
        {reviews.length === 0 && <p className="sm-empty sm-body-m-regular">아직 등록된 후기가 없습니다.</p>}
      </div>
      <button type="button" className="sm-fab" aria-label="후기 작성"><span>＋</span><small>작성</small></button>
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
            <span className="sm-body-m-medium">완료</span>
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
          <button type="button" className="sm-photo-button" disabled>▧&nbsp; 사진 첨부 (0/5)</button>
        </div>
      </div>
      {toast && <Toast message={toast} />}
    </>
  );
}
