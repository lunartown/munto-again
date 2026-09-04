// 2026-09-02에 수집한 서울 공개 모임 목록 중 `독서` 키워드 모임을 무작위로 뽑은 스냅샷입니다.
// 목록 API에 없는 상세 위치·비용·참석자·후기는 만들지 않습니다.

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
  full?: boolean;
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
  reviews: Review[];
  banner: string;
  thumb: string;
  sourceUrl: string;
};

type SourceGroup = {
  id: string;
  name: string;
  description: string;
  region: string;
  members: number;
  eventCount: number;
  nextEventDate: number | null;
  nextEventTime: string | null;
};

const SOURCE_GROUPS: SourceGroup[] = [
  { id: "0c8407e6-52ac-40cd-b751-af86c463ba811", name: "잡학다食, - 독서모임", description: "📚 잡학다食  책은 같이 읽으면 더 재밌고, 대화는 같이 하면 더 재밌잖아요.  한 권의", region: "중구", members: 11, eventCount: 3, nextEventDate: 20260905, nextEventTime: "1100" },
  { id: "a7623880-14a0-11f0-895f-0a25e09d32091", name: "사유식탁", description: "🍽️ 함께 사유하는 테이블 '사유식탁'  책 한 권, 영화 한 편, 그림 한 폭 그 안의", region: "영등포구", members: 50, eventCount: 2, nextEventDate: 20260911, nextEventTime: "1930" },
  { id: "e2bd3b80-47ba-43c0-b870-1c6065a6c8011", name: "[📚 책읽는 틈]독서모임(신규모집)", description: "📚 책읽는 틈  바쁜 하루 속에서 잠시 멈춰, 책 한 권과 함께 쉬어갈 수 있는 시간을 만", region: "성북구", members: 19, eventCount: 1, nextEventDate: 20260905, nextEventTime: "1030" },
  { id: "9a09f1ce-bc7a-4af2-9e29-51a70e79add01", name: "[독서 모임] 사유(思惟)", description: "📚 독서 소모임 모집 | 사유(思惟)  혼자 읽고 넘기기에는 아까운 문장들이 있습니다. 생", region: "종로구", members: 59, eventCount: 4, nextEventDate: 20260902, nextEventTime: "1930" },
  { id: "42d32030-7b8f-11ec-bd4f-0a4ecec0f57f1", name: "자유독서모임 ‘윤슬’", description: "윤슬 이란  '햇빛이나 달빛에 비치어 반짝이는 잔 물결'  을 뜻 하는 순 우리말 입니다.", region: "성동구", members: 291, eventCount: 3, nextEventDate: 20260902, nextEventTime: "1930" },
  { id: "5f684fd2-39b9-11ef-ab2f-0ace312f98011", name: "🌃 북클럽 소란 | SORAN", description: "'소란스러운 저녁🌜, 책 읽고 떠드는 사람들'  책 좋은건 알지만 손에 잘 안잡히죠? 같이", region: "종로구", members: 70, eventCount: 0, nextEventDate: null, nextEventTime: null },
  { id: "1eacdcc5-0cc2-4999-b6bf-a7c25e0661ea1", name: "✨NEW☁️포근북스☁️신입환영", description: "독서 · 스터디 · 개인업무 · 어드민 나이트 포근북스에서 함께 성장해요. 📚☕✨ ‘책을", region: "광진구", members: 18, eventCount: 3, nextEventDate: 20260902, nextEventTime: "1930" },
  { id: "642d3ea2-2c8d-413b-ad62-003012a2c9bb1", name: "독서 행성", description: "당신은 지금 세상의 모든 역사+ 책을 읽고 토론& 현장을 답사하는, 독서행성에 도착하셨습니", region: "용산구", members: 30, eventCount: 4, nextEventDate: 20260903, nextEventTime: "1900" },
  { id: "f58d6afd-7628-4eb3-b455-392951e12ae61", name: "책 & 신문을 통한 세상과의 대화", description: "함께 책과 신문으로 세상과 소통하는 모임입니다. 독서를 좋아하시거나 관심은 있지만 혼자서", region: "강동구", members: 3, eventCount: 1, nextEventDate: 20260906, nextEventTime: "2000" },
  { id: "673a3b38-e813-465e-ab5e-54381028e2071", name: "독서모임 뮤트(Mute)", description: "안녕하세요. 저희는 30대 운영진 4명을 주축으로 운영되고 있는 4년 차 독서 동아리입니", region: "동작구", members: 24, eventCount: 3, nextEventDate: 20260904, nextEventTime: "1900" },
  { id: "86916fce-b463-11ef-8b63-0a7bc75226211", name: "[독서모임] 📚북적북적📚", description: "📖 [북적북적: 책을 읽고 함께 피리를 불다] 안녕하세요! 북적북적은 책(Book)과 피리", region: "동작구", members: 72, eventCount: 4, nextEventDate: 20260908, nextEventTime: "1930" },
  { id: "8c05e320-b603-11e6-a9a5-22000aac01431", name: "📙[강남] 최대 독서모임 꾸독💖", description: "■ ■가입인사\"  24시간내 미작성시 \"강퇴 ■■  😎Ai시대,독서\"와 환경설정\"이 답 입", region: "강남구", members: 263, eventCount: 2, nextEventDate: 20260905, nextEventTime: "1030" },
  { id: "fdf75162-4d06-11e3-a21b-1231500688731", name: "수요일엔 책이랑~♥", description: "좋은 사람들과 책 이야기 나누며 기나긴 여행을 하는 중입니다. 매달 첫째, 셋째 주 수요일에", region: "관악구", members: 106, eventCount: 4, nextEventDate: 20260902, nextEventTime: "1930" },
  { id: "be4e600c-bad0-11ef-90bc-0a0dab7805851", name: "[독서] 북포레(BookFore)", description: "\"독서를 이기는 건 없다\" - Warren Buffett  책으로 연결되고, 사람으로 따뜻", region: "마포구", members: 200, eventCount: 4, nextEventDate: 20260903, nextEventTime: "1900" },
  { id: "8153bff4-7e17-11ee-a7a9-0a10caceebb91", name: "📕치유.성장.행복_북스런💚", description: "📕📗📓📙📘📒📔  📚책의 힘을 믿어요!  🧤지식 쌓기가 아닌  👒치유와 자신의 성장을 목표로", region: "서대문구", members: 50, eventCount: 1, nextEventDate: 20260903, nextEventTime: "1900" },
  { id: "4cd18c1a-e2e9-11ef-843c-0a7994fa3be51", name: "북클럽 골디락스(Goldilocks)", description: "🔶북클럽 골디락스(Goldilocks)🔶  ▪️책을 비롯한 다양한 매개체를 도구삼아 “자신", region: "강남구", members: 46, eventCount: 2, nextEventDate: 20260903, nextEventTime: "1800" },
];

function formatDate(value: number, time: string | null): string {
  const raw = String(value);
  const month = Number(raw.slice(4, 6));
  const day = Number(raw.slice(6, 8));
  if (!time) return `${month}월 ${day}일`;
  return `${month}월 ${day}일 ${time.slice(0, 2)}:${time.slice(2)}`;
}

export const GATHERINGS: Gathering[] = SOURCE_GROUPS.map((group, index) => ({
  id: group.id,
  name: group.name,
  navName: group.name,
  desc: group.description,
  region: group.region,
  category: "독서",
  members: group.members,
  recent: group.eventCount > 0 ? `정모 ${group.eventCount}개` : "예정 정모 없음",
  intro: group.description,
  reviewCount: 0,
  reviews: [],
  meetings: group.nextEventDate
    ? [{ badge: "예정", name: "다음 정기모임", when: formatDate(group.nextEventDate, group.nextEventTime), where: group.region, cta: "상세 보기" }]
    : [],
  banner: `/somoim/banner_c${(index % 4) + 1}.png`,
  thumb: `/somoim/thumb_c${(index % 4) + 1}.png`,
  sourceUrl: `https://www.somoim.co.kr/${group.id}`,
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
