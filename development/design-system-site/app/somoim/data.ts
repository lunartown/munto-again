import sourceGroups from "./groups.json";

export type Review = {
  author: string;
  date: string;
  body: string;
  helpful: number;
  visibility: "public" | "private";
  meetingName?: string;
  meetingWhen?: string;
  meetingWhere?: string;
  meetingCount?: string;
};

export type Meeting = {
  badge: string;
  name: string;
  when: string;
  where?: string;
  cost?: string;
  attend?: string;
  cta: string;
  image: string;
  full?: boolean;
};

export type Member = {
  id: string;
  name: string;
  image: string;
  isManager: boolean;
};

export type Article = {
  id: string;
  author: string;
  authorImage?: string;
  category: string;
  title: string;
  body: string;
  likes: number;
  comments: number;
};

export type Photo = {
  id: string;
  image: string;
  likes: number;
  comments: number;
};

export type Gathering = {
  id: string;
  name: string;
  navName: string;
  desc: string;
  region: string;
  category: string;
  members: number;
  recent: string;
  intro: string;
  reviewCount: number;
  meetings: Meeting[];
  memberList: Member[];
  articles: Article[];
  photos: Photo[];
  reviews: Review[];
  banner: string;
  thumb: string;
  sourceUrl: string;
};

function formatDate(value: number, time: string): string {
  const raw = String(value);
  const month = Number(raw.slice(4, 6));
  const day = Number(raw.slice(6, 8));
  return `${month}월 ${day}일 ${time.slice(0, 2)}:${time.slice(2)}`;
}

function summarize(description: string): string {
  const compact = description.replace(/\s+/g, " ").trim();
  return compact.length > 74 ? `${compact.slice(0, 74)}…` : compact;
}

export const GATHERINGS: Gathering[] = sourceGroups.map((group, index) => ({
  id: group.id,
  name: group.name,
  navName: group.name,
  desc: summarize(group.description),
  region: group.region,
  category: group.keyword,
  members: group.members,
  recent: group.events.length > 0 ? `정모 ${group.events.length}개` : "예정 정모 없음",
  intro: group.description,
  reviewCount: 0,
  reviews: [],
  meetings: group.events.map((event) => ({
    badge: "예정",
    name: event.name,
    when: formatDate(event.date, event.time),
    where: event.location,
    cost: event.cost,
    attend: `${event.currentMembers}명 참석중 (${event.currentMembers}/${event.maxMembers})`,
    cta: event.currentMembers >= event.maxMembers ? "빈자리 알림 받기" : "참석",
    full: event.currentMembers >= event.maxMembers,
    image: `/somoim/events/${event.id}.png`,
  })),
  memberList: group.memberList.map((member) => ({
    id: member.id,
    name: member.name,
    image: member.imageUrl,
    isManager: member.isManager,
  })),
  articles: group.articles.map((article) => ({
    id: article.id,
    author: article.author,
    authorImage: article.authorImageUrl ?? undefined,
    category: article.category,
    title: article.title,
    body: article.body,
    likes: article.likes,
    comments: article.comments,
  })),
  photos: group.photos.map((photo) => ({
    id: photo.id,
    image: photo.imageUrl,
    likes: photo.likes,
    comments: photo.comments,
  })),
  banner: `/somoim/group_${String(index + 1).padStart(2, "0")}.png`,
  thumb: `/somoim/group_${String(index + 1).padStart(2, "0")}.png`,
  sourceUrl: group.source_url,
}));

export function byId(id: string): Gathering | undefined {
  return GATHERINGS.find((g) => g.id === id);
}

export const REPORT_REASONS = [
  "욕설, 비방, 혐오 표현",
  "개인정보 노출 또는 신상 침해",
  "허위 사실 또는 악의적 명예훼손",
  "상업적 홍보 또는 스팸",
  "음란물, 불건전, 위험 내용",
  "기타",
];

export const SORT_OPTIONS = ["최신순", "오래된 순", "추천순"];
