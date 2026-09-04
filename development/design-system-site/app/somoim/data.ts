// 소모임 프로토타입 데이터
// Figma 파일 jMx6ZzITwZJAeaiVee9xsG 의 화면 내용을 그대로 옮긴 데이터.

export type Review = {
  author: string;
  date: string;
  body: string;
  helpful: number;
  /** 참여한 정기모임 공개 여부 — Figma `Participated Gathering Card` 의 Visibility 배리언트 */
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
  where: string;
  cost: string;
  attend: string;
  cta: string;
  /** 정원이 찼을 때는 참석 대신 빈자리 알림 */
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
  quote: string;
  intro: string;
  reviewCount: number;
  meetings: Meeting[];
  reviews: Review[];
  banner: string;
  thumb: string;
};

const MEMBER_NAMES = ["모임장 · 나무늘보", "책읽는곰", "조용한밤", "민트초코", "오래된책방"];

export const MEMBERS = MEMBER_NAMES;

export const GATHERINGS: Gathering[] = [
  {
    id: "jayu",
    name: "🌸 자유독서단 🌸",
    navName: "🌸 자유독서단 🌸",
    desc: "책을 함께 읽되, 각자 읽어요",
    region: "강남구",
    category: "인문학/책/글",
    members: 175,
    recent: "방금 대화",
    quote: "‘책을 함께 읽되, 각자 읽어요.’",
    intro: `📚 책을 좋아하지만 혼자선 잘 안 읽게 되는 당신을 위해!
우리는 각자 읽고 싶은 책을 가져와
조용히 읽고, 짧게 소감을 나누는
💜 내향인 맞춤형 독서모임이에요 :)
💚 활동 없음으로 강퇴된 분들은 활동가능하실 때 얼마든지 ‘재가입’ 가능합니다!

✨ 신규가입비 ✨
최초 1회 가입비 3,000원이 있습니다.
가입비는 노쇼 방지 및 모임 운영비로 사용되며,
미입금시 참석이 불가합니다.

📜 운영 방식
- 1시간 동안 각자 책 읽기
- 이후 1시간 동안 소감, 인상 깊었던 구절 나누기
*총 2시간 진행
- 발표, 토론 ❌ 강요 ❌ 부담 ❌

🌿 이런 분께 추천해요
- 읽고 싶은 책은 많은데, 시간 내서 읽기 어려운 분
- 독서 습관을 만들고 싶은 분
- 조용한 분위기에서 편하게 집중하고 싶은 2030대

✔️ 반드시 공지사항 확인 해주세요.
✔️ 개인 사익을 위한 영업은 절대 불가합니다.`,
    reviewCount: 68,
    banner: "/somoim/banner_c1.png",
    thumb: "/somoim/thumb_c1.png",
    meetings: [
      { badge: "오늘", name: "🔥 자유독서", when: "8.20(목) 19:00", where: "투썸플레이스 강남IBC점", cost: "각자 음료(10%할인)", attend: "5명 참석중 (5/6)", cta: "참석" },
      { badge: "D-6", name: "🌸 자유독서", when: "8.26(수) 19:00", where: "투썸 강남 IBC점", cost: "각자 음료", attend: "6명 참석중 (6/6)", cta: "빈자리 알림 받기", full: true },
    ],
    reviews: [
      {
        author: "강렬한 토끼", date: "8월 9일 오후 6:48", helpful: 12, visibility: "public",
        meetingName: "🔥 8월 지정독서 [여름의 끝에서]", meetingWhen: "8월 7일 오후 7:00", meetingWhere: "강남구", meetingCount: "8명 참석",
        body: "첫 참석이었는데 분위기는 편했습니다. 다만 책 얘기는 처음 20분 정도였고 나머지는 다 같이 술자리로 이어졌어요. 저는 다음 일정이 있어 먼저 나왔는데 안 가면 눈치 보이는 분위기였습니다.",
      },
      {
        author: "게으른 고양이", date: "8월 5일 오후 3:32", helpful: 9, visibility: "private",
        body: "시작 시간이 30분 넘게 밀렸고, 진행을 맡은 분이 따로 없어서 아는 사람들끼리 얘기하다 끝났습니다. 처음 온 사람이 낄 자리가 없었어요.",
      },
      {
        author: "철없는 사자", date: "8월 3일 오후 1:32", helpful: 7, visibility: "private",
        body: "책 좋아하는 분들이라 얘기는 재미있었습니다. 다만 매번 뒤풀이가 길어져서 평일에는 부담됐어요.",
      },
    ],
  },
  {
    id: "jeonyeok",
    name: "📗 책읽는 저녁",
    navName: "📗 책읽는 저녁",
    desc: "퇴근하고 한 시간, 조용히 읽고 짧게 나눠요",
    region: "강남구",
    category: "인문학/책/글",
    members: 162,
    recent: "30분 전 대화",
    quote: "‘퇴근하고 한 시간, 조용히 읽고 짧게 나눠요.’",
    intro: `📗 퇴근하고 바로 오셔서 한 시간만 읽고 가세요.
각자 가져온 책을 읽고, 짧게 한 마디씩 나눕니다.
💬 말을 많이 하지 않아도 괜찮습니다.

✨ 참가비 ✨
매회 대관료 3,000원 (현장 납부)
그 외 비용은 없습니다.

📜 운영 방식
- 19:30~20:20 각자 책 읽기
- 20:20~20:40 한 사람씩 짧게 이야기
*총 70분, 시간 지켜서 끝냅니다
- 발표 ❌ 토론 ❌

🌿 이런 분께 추천해요
- 퇴근 후 짧게 집중하고 싶은 분
- 말수가 적어도 부담 없는 모임을 찾는 분

✔️ 처음 오시는 분께는 진행 순서를 미리 안내드립니다.`,
    reviewCount: 41,
    banner: "/somoim/banner_c2.png",
    thumb: "/somoim/thumb_c2.png",
    meetings: [
      { badge: "오늘", name: "📗 화요독서", when: "8.20(화) 19:30", where: "강남역 스터디룸 A", cost: "대관료 3,000원", attend: "4명 참석중 (4/8)", cta: "참석" },
      { badge: "D-7", name: "📗 화요독서", when: "8.27(화) 19:30", where: "강남역 스터디룸 A", cost: "대관료 3,000원", attend: "3명 참석중 (3/8)", cta: "참석" },
    ],
    reviews: [
      {
        author: "조용한 두루미", date: "8월 12일 오후 9:20", helpful: 15, visibility: "public",
        meetingName: "📖 8월 화요독서 [단단한 하루]", meetingWhen: "8월 12일 오후 7:30", meetingWhere: "강남구", meetingCount: "6명 참석",
        body: "진행 순서가 정해져 있어서 처음 가도 헤매지 않았습니다. 50분 읽고 20분 이야기하는데 시간이 밀린 적이 없어요.",
      },
      {
        author: "성실한 여우", date: "8월 6일 오후 10:05", helpful: 11, visibility: "private",
        body: "말을 많이 안 해도 되는 구조라 좋았습니다. 한 사람씩 돌아가며 짧게 이야기해서 조용한 사람도 낄 수 있어요.",
      },
      {
        author: "반가운 수달", date: "7월 30일 오후 9:41", helpful: 8, visibility: "private",
        body: "대관료 3,000원 외에 다른 비용은 없었고 끝나면 바로 해산합니다. 퇴근 후에 부담 없이 갈 수 있어요.",
      },
    ],
  },
  {
    id: "handal",
    name: "📚 한 달 한 권",
    navName: "📚 한 달 한 권",
    desc: "한 달에 한 권, 천천히 읽는 모임",
    region: "강남구",
    category: "인문학/책/글",
    members: 188,
    recent: "방금 대화",
    quote: "‘한 달에 한 권, 천천히 읽어요.’",
    intro: `📚 한 달에 한 권씩 같이 읽습니다.
그 달의 책은 단톡방에서 투표로 정해요.

✨ 참가비 ✨
따로 없습니다. 음료값만 각자 부담합니다.

📜 운영 방식
- 매월 마지막 주 토요일 오후
- 읽은 만큼 자유롭게 이야기
*시간은 그날 분위기에 따라 유동적입니다

🌿 이런 분께 추천해요
- 천천히 읽는 걸 좋아하는 분
- 부담 없이 한 달에 한 번만 나오고 싶은 분

✔️ 장소와 시간은 단톡방 공지로 안내드립니다.`,
    reviewCount: 33,
    banner: "/somoim/banner_c3.png",
    thumb: "/somoim/thumb_c3.png",
    meetings: [
      { badge: "D-11", name: "📚 8월 모임", when: "8.31(토) 15:00", where: "장소 미정 (당일 공지)", cost: "각자 음료", attend: "2명 참석중 (2/10)", cta: "참석" },
      { badge: "미정", name: "📚 9월 모임", when: "일정 조율 중", where: "장소 미정", cost: "각자 음료", attend: "0명 참석중 (0/10)", cta: "참석" },
    ],
    reviews: [
      {
        author: "무던한 곰", date: "8월 10일 오후 4:12", helpful: 14, visibility: "public",
        meetingName: "📚 8월 이달의 책 [느린 계절]", meetingWhen: "8월 9일 오후 3:00", meetingWhere: "강남구", meetingCount: "4명 참석",
        body: "책 선정은 좋았는데 장소가 매번 바뀌고 공지가 당일 오전에 옵니다. 두 번은 도착하니 장소가 또 바뀌어 있었어요.",
      },
      {
        author: "느긋한 사슴", date: "7월 28일 오후 6:03", helpful: 10, visibility: "private",
        body: "모임장이 안내한 시작 시간과 실제가 계속 달랐습니다. 한 번은 한 시간을 기다렸는데 그날 모임이 취소됐다는 연락을 나중에 받았어요.",
      },
      {
        author: "조심스러운 다람쥐", date: "7월 15일 오후 2:47", helpful: 6, visibility: "private",
        body: "사람들은 좋았습니다. 다만 다음 모임이 언제 열릴지 매번 알 수 없어서 일정을 잡기 어려웠어요.",
      },
    ],
  },
  {
    id: "toegeun",
    name: "🌙 퇴근길 독서모임",
    navName: "🌙 퇴근길 독서모임",
    desc: "평일 저녁 강남역에서 읽고 이야기합니다",
    region: "강남구",
    category: "인문학/책/글",
    members: 154,
    recent: "1시간 전 대화",
    quote: "‘평일 저녁, 읽고 이야기합니다.’",
    intro: `🌙 매주 수요일 저녁, 같은 자리에서 만납니다.
30분 각자 읽고, 그날 읽은 내용을 한 시간 이야기합니다.

✨ 참가비 ✨
없습니다. 음료값만 각자 부담합니다.

📜 운영 방식
- 19:00~19:30 각자 책 읽기
- 19:30~20:30 읽은 부분 이야기
*총 90분
- 읽은 만큼만 이야기하시면 됩니다

🌿 이런 분께 추천해요
- 독서모임이 처음인 분
- 매주 같은 요일에 고정으로 나오고 싶은 분

✔️ 끝나고 따로 자리를 갖지 않습니다.`,
    reviewCount: 52,
    banner: "/somoim/banner_c4.png",
    thumb: "/somoim/thumb_c4.png",
    meetings: [
      { badge: "오늘", name: "🌙 수요독서", when: "8.20(수) 19:00", where: "강남역 4번 출구 카페", cost: "각자 음료", attend: "6명 참석중 (6/10)", cta: "참석" },
      { badge: "D-7", name: "🌙 수요독서", when: "8.27(수) 19:00", where: "강남역 4번 출구 카페", cost: "각자 음료", attend: "5명 참석중 (5/10)", cta: "참석" },
    ],
    reviews: [
      {
        author: "담백한 고래", date: "8월 14일 오후 10:11", helpful: 13, visibility: "public",
        meetingName: "🌙 8월 수요독서 [퇴근 이후]", meetingWhen: "8월 13일 오후 7:00", meetingWhere: "강남구", meetingCount: "7명 참석",
        body: "매주 같은 요일 같은 장소라 일정 잡기 편했습니다. 세 번 갔는데 시간이 밀린 적이 없어요.",
      },
      {
        author: "다정한 너구리", date: "8월 7일 오후 9:52", helpful: 9, visibility: "private",
        body: "독서모임이 처음이라 걱정했는데 읽은 만큼만 이야기하면 된다고 해서 부담이 없었습니다.",
      },
      {
        author: "꾸준한 오리", date: "7월 31일 오후 9:35", helpful: 7, visibility: "private",
        body: "인원이 많지 않아 한 사람씩 충분히 이야기할 수 있었습니다. 끝나고 따로 자리를 갖지 않아서 좋았어요.",
      },
    ],
  },
];

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
