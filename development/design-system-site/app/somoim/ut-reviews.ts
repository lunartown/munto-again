export type UtReviewFixture = {
  author: string;
  date: string;
  body: string;
  helpful: number;
  meetingName: string;
  meetingWhen: string;
  meetingWhere: string;
  meetingCount: string;
};

export type UtReviewSet = {
  variant: "control" | "mine";
  mineCondition?: "social_over_activity" | "no_newcomer_structure" | "skill_mismatch" | "broken_promises";
  reviews: UtReviewFixture[];
};

// 사용성 테스트용 합성 후기입니다. 실제 모임에 대한 사실 주장으로 사용하지 않습니다.
export const UT_REVIEW_SETS: Record<string, UtReviewSet> = {
  "0c8407e6-52ac-40cd-b751-af86c463ba811": {
    variant: "control",
    reviews: [
      { author: "익명 41", date: "2026.08.29", body: "처음 참여했는데 진행자가 질문 순서를 잡아줘서 자연스럽게 이야기할 수 있었어요. 책을 다 읽지 못한 사람도 읽은 부분 안에서 의견을 나눌 수 있었습니다.", helpful: 7, meetingName: "8월 함께 읽기", meetingWhen: "2026.08.27 19:30", meetingWhere: "중구 카페", meetingCount: "8명 참여" },
      { author: "익명 18", date: "2026.08.17", body: "공지된 시간에 시작해 두 시간 동안 책 이야기를 나눴어요. 서로 다른 관점이 나와도 한 사람씩 충분히 말할 수 있게 진행해준 점이 좋았습니다.", helpful: 4, meetingName: "8월 정기 독서모임", meetingWhen: "2026.08.15 14:00", meetingWhere: "중구 모임공간", meetingCount: "9명 참여" },
    ],
  },
  "a7623880-14a0-11f0-895f-0a25e09d32091": {
    variant: "mine",
    mineCondition: "social_over_activity",
    reviews: [
      { author: "익명 07", date: "2026.08.30", body: "사람들이 친절해서 처음 가도 금방 어울릴 수 있었어요. 작품 이야기는 30분 정도 하고 이후에는 근황 이야기와 뒤풀이로 이어져서 친해지기 좋았습니다.", helpful: 12, meetingName: "8월 문화 이야기", meetingWhen: "2026.08.28 19:30", meetingWhere: "영등포구청역 모임공간", meetingCount: "11명 참여" },
      { author: "익명 32", date: "2026.08.16", body: "선정된 영화의 장면을 각자 다르게 해석한 부분이 재미있었어요. 진행 전에 참고 질문을 공유해줘서 생각을 정리하고 참여하기 편했습니다.", helpful: 5, meetingName: "영화 감상 모임", meetingWhen: "2026.08.14 19:30", meetingWhere: "영등포구청역 모임공간", meetingCount: "10명 참여" },
    ],
  },
  "e2bd3b80-47ba-43c0-b870-1c6065a6c8011": {
    variant: "control",
    reviews: [
      { author: "익명 24", date: "2026.08.31", body: "한 달에 한 권이라 직장 생활과 병행하기 부담스럽지 않았어요. 처음 온 사람에게도 질문을 먼저 건네줘서 책에 대한 생각을 편하게 말할 수 있었습니다.", helpful: 9, meetingName: "토요 오전 독서모임", meetingWhen: "2026.08.29 10:30", meetingWhere: "성북구 카페", meetingCount: "7명 참여" },
      { author: "익명 53", date: "2026.08.12", body: "발제문이 미리 올라와 준비할 범위를 알 수 있었고 실제 모임도 안내된 순서대로 진행됐어요. 독서량보다 서로의 생각을 듣는 데 집중하는 분위기였습니다.", helpful: 6, meetingName: "8월 책읽는 틈", meetingWhen: "2026.08.09 10:30", meetingWhere: "성북구 모임공간", meetingCount: "8명 참여" },
    ],
  },
  "9a09f1ce-bc7a-4af2-9e29-51a70e79add01": {
    variant: "control",
    reviews: [
      { author: "익명 16", date: "2026.08.28", body: "책에서 인상 깊었던 문장을 중심으로 이야기해서 어렵지 않게 참여했어요. 진행자가 발언 시간을 고르게 나눠줘서 처음 참석한 저도 충분히 말했습니다.", helpful: 8, meetingName: "8월 지정도서 모임", meetingWhen: "2026.08.26 19:30", meetingWhere: "종각역 카페", meetingCount: "12명 참여" },
      { author: "익명 45", date: "2026.08.10", body: "공지에 적힌 도서와 시간대로 진행됐고 토론 주제도 미리 공유됐어요. 감상을 정답처럼 몰아가지 않고 각자의 해석을 존중하는 분위기였습니다.", helpful: 3, meetingName: "수요 독서모임", meetingWhen: "2026.08.05 19:30", meetingWhere: "종각역 카페", meetingCount: "10명 참여" },
    ],
  },
  "42d32030-7b8f-11ec-bd4f-0a4ecec0f57f1": {
    variant: "control",
    reviews: [
      { author: "익명 29", date: "2026.08.30", body: "각자 가져온 책을 읽은 뒤 인상 깊은 부분을 나눴어요. 읽는 시간과 대화 시간이 분명히 나뉘어 있어서 제가 기대한 자유독서 방식과 잘 맞았습니다.", helpful: 11, meetingName: "8월 자유독서모임", meetingWhen: "2026.08.29 10:00", meetingWhere: "익선동 카페", meetingCount: "13명 참여" },
      { author: "익명 04", date: "2026.08.09", body: "회원 수가 많아 걱정했는데 정모는 적당한 인원으로 진행됐어요. 처음 온 사람을 소개하고 대화 순서를 안내해줘서 어색하지 않았습니다.", helpful: 7, meetingName: "토요일 자유독서", meetingWhen: "2026.08.08 10:00", meetingWhere: "익선동 카페", meetingCount: "12명 참여" },
    ],
  },
  "5f684fd2-39b9-11ef-ab2f-0ace312f98011": {
    variant: "control",
    reviews: [
      { author: "익명 38", date: "2026.08.27", body: "평일 저녁 일정이 매달 미리 공지돼 시간을 잡기 쉬웠어요. 책을 읽고 난 뒤 질문을 따라 대화하는 방식이라 흐름이 끊기지 않았습니다.", helpful: 5, meetingName: "소란스러운 목요일", meetingWhen: "2026.08.25 19:30", meetingWhere: "종로구 카페", meetingCount: "9명 참여" },
      { author: "익명 61", date: "2026.08.08", body: "독서 습관을 만들고 싶어 참여했는데 정해진 시간 동안 함께 읽는 방식이 도움이 됐어요. 끝난 뒤에도 참석을 강요하는 일정 없이 깔끔하게 마무리됐습니다.", helpful: 8, meetingName: "퇴근 후 함께 읽기", meetingWhen: "2026.08.06 19:30", meetingWhere: "종로구 모임공간", meetingCount: "8명 참여" },
    ],
  },
  "1eacdcc5-0cc2-4999-b6bf-a7c25e0661ea1": {
    variant: "mine",
    mineCondition: "no_newcomer_structure",
    reviews: [
      { author: "익명 12", date: "2026.08.29", body: "오래 참여한 분들이 서로 잘 챙겨줘서 분위기는 편안했어요. 다만 별도 진행 순서 없이 아는 사람끼리 대화가 이어져 처음 간 저는 끼어들 타이밍을 찾기 어려웠습니다.", helpful: 10, meetingName: "금요 지정독서", meetingWhen: "2026.08.28 19:30", meetingWhere: "광진구 카페", meetingCount: "10명 참여" },
      { author: "익명 47", date: "2026.08.15", body: "읽을 분량과 질문이 사전에 안내돼 준비하기 편했어요. 각자 기억에 남은 문장을 소개하는 시간이 있어 다른 분들의 관점을 들을 수 있었습니다.", helpful: 4, meetingName: "포근북스 함께 읽기", meetingWhen: "2026.08.14 19:30", meetingWhere: "광진구 카페", meetingCount: "9명 참여" },
    ],
  },
  "642d3ea2-2c8d-413b-ad62-003012a2c9bb1": {
    variant: "control",
    reviews: [
      { author: "익명 35", date: "2026.08.30", body: "책에서 읽은 역사적 배경을 현장에서 확인하니 기억에 오래 남았어요. 이동 경로와 준비물이 미리 안내돼 답사 모임이 처음이어도 따라가기 편했습니다.", helpful: 13, meetingName: "역사문학 답사", meetingWhen: "2026.08.29 10:00", meetingWhere: "용산구 일대", meetingCount: "14명 참여" },
      { author: "익명 09", date: "2026.08.11", body: "분기별 읽기 순서가 정리돼 있어 다음 모임을 준비하기 쉬웠습니다. 배경지식이 부족한 부분은 진행자가 짧게 설명해줘서 토론을 따라갈 수 있었어요.", helpful: 6, meetingName: "세계사 함께 읽기", meetingWhen: "2026.08.08 14:00", meetingWhere: "용산구 모임공간", meetingCount: "11명 참여" },
    ],
  },
  "f58d6afd-7628-4eb3-b455-392951e12ae61": {
    variant: "control",
    reviews: [
      { author: "익명 56", date: "2026.08.31", body: "신문 기사를 미리 고르지 못했는데 현장에서 함께 읽을 자료를 나눠줘서 바로 참여할 수 있었어요. 소수 인원이라 각자 의견을 충분히 이야기했습니다.", helpful: 4, meetingName: "책과 신문으로 대화", meetingWhen: "2026.08.30 20:00", meetingWhere: "강동구 카페", meetingCount: "4명 참여" },
      { author: "익명 21", date: "2026.08.17", body: "자유도서 시간에는 각자 읽고 싶은 책에 집중하고 마지막에 짧게 소개했어요. 진행 방식이 단순하고 공지와 실제 내용이 같아서 편했습니다.", helpful: 3, meetingName: "일요 자유독서", meetingWhen: "2026.08.16 20:00", meetingWhere: "강동구 카페", meetingCount: "5명 참여" },
    ],
  },
  "673a3b38-e813-465e-ab5e-54381028e2071": {
    variant: "control",
    reviews: [
      { author: "익명 43", date: "2026.08.28", body: "고전 문학이라 어렵지 않을까 걱정했는데 질문이 구체적이어서 이야기의 흐름을 따라가기 쉬웠어요. 처음 참여한 사람도 차례대로 의견을 나눴습니다.", helpful: 9, meetingName: "8월 고전문학 모임", meetingWhen: "2026.08.27 19:00", meetingWhere: "사당역 카페", meetingCount: "8명 참여" },
      { author: "익명 14", date: "2026.08.08", body: "월별 일정과 도서가 미리 올라와 꾸준히 참여할 계획을 세우기 좋았어요. 토론이 끝난 뒤 다음 책을 함께 정하는 과정도 투명했습니다.", helpful: 5, meetingName: "목요 지정도서", meetingWhen: "2026.08.06 19:00", meetingWhere: "사당역 카페", meetingCount: "9명 참여" },
    ],
  },
  "86916fce-b463-11ef-8b63-0a7bc75226211": {
    variant: "mine",
    mineCondition: "skill_mismatch",
    reviews: [
      { author: "익명 26", date: "2026.08.30", body: "깊이 있는 토론을 좋아하는 분들에게 잘 맞는 모임이에요. 초보도 괜찮다고 안내됐지만 실제로는 완독과 발제 경험을 전제로 대화가 진행돼 처음 참여한 저는 따라가기 벅찼습니다.", helpful: 14, meetingName: "8월 지정도서 토론", meetingWhen: "2026.08.29 14:00", meetingWhere: "동작구 카페", meetingCount: "12명 참여" },
      { author: "익명 50", date: "2026.08.13", body: "참여자들이 책의 세부 장면까지 기억하고 있어 다양한 해석을 들을 수 있었어요. 예정된 두 시간 동안 쉬지 않고 토론해서 밀도 있게 느껴졌습니다.", helpful: 8, meetingName: "토요 독서토론", meetingWhen: "2026.08.08 14:00", meetingWhere: "동작구 카페", meetingCount: "11명 참여" },
    ],
  },
  "8c05e320-b603-11e6-a9a5-22000aac01431": {
    variant: "control",
    reviews: [
      { author: "익명 05", date: "2026.08.29", body: "참여 인원이 많지만 소그룹으로 나눠서 모든 사람이 발언할 수 있었어요. 진행자가 시간표를 공유하고 순서대로 운영해 집중하기 좋았습니다.", helpful: 10, meetingName: "8월 꾸준한 독서", meetingWhen: "2026.08.28 10:30", meetingWhere: "강남역 모임공간", meetingCount: "16명 참여" },
      { author: "익명 34", date: "2026.08.14", body: "책을 읽으며 적어둔 질문을 자유롭게 꺼낼 수 있었고 다른 의견도 편하게 받아주는 분위기였어요. 다음 일정도 모임이 끝나기 전에 안내됐습니다.", helpful: 6, meetingName: "금요 지정책 모임", meetingWhen: "2026.08.13 19:30", meetingWhere: "강남역 모임공간", meetingCount: "15명 참여" },
    ],
  },
  "fdf75162-4d06-11e3-a21b-1231500688731": {
    variant: "control",
    reviews: [
      { author: "익명 58", date: "2026.08.27", body: "첫째·셋째 수요일 일정이 꾸준히 지켜져 퇴근 후 계획을 세우기 편해요. 책 이야기 중심으로 진행되고 정해진 시간에 마무리됐습니다.", helpful: 7, meetingName: "수요일 책 여행", meetingWhen: "2026.08.26 19:30", meetingWhere: "서울대입구역 북카페", meetingCount: "10명 참여" },
      { author: "익명 23", date: "2026.08.07", body: "오래된 모임이라 낯설까 봐 걱정했는데 시작할 때 새 참여자를 소개해주고 질문 순서도 안내해줬어요. 차분하게 책에 집중할 수 있었습니다.", helpful: 9, meetingName: "8월 첫째 주 모임", meetingWhen: "2026.08.05 19:30", meetingWhere: "서울대입구역 북카페", meetingCount: "9명 참여" },
    ],
  },
  "be4e600c-bad0-11ef-90bc-0a0dab7805851": {
    variant: "mine",
    mineCondition: "broken_promises",
    reviews: [
      { author: "익명 11", date: "2026.08.31", body: "참여자들의 책 이야기는 흥미로웠어요. 다만 공지에는 자유 감상이라고 적혀 있었는데 현장에서는 준비하지 않은 발표를 요청받았고, 장소도 전날 바뀌어 일정 맞추기가 어려웠습니다.", helpful: 13, meetingName: "8월 목요 독서", meetingWhen: "2026.08.27 19:00", meetingWhere: "합정역 카페", meetingCount: "13명 참여" },
      { author: "익명 49", date: "2026.08.15", body: "지정도서를 읽고 서로의 질문을 이어가는 과정이 재미있었어요. 여러 분야의 책을 접할 수 있고 한 사람에게 발언이 몰리지 않아 좋았습니다.", helpful: 5, meetingName: "목요일 지정도서", meetingWhen: "2026.08.13 19:00", meetingWhere: "합정역 카페", meetingCount: "12명 참여" },
    ],
  },
  "8153bff4-7e17-11ee-a7a9-0a10caceebb91": {
    variant: "control",
    reviews: [
      { author: "익명 31", date: "2026.08.30", body: "그림책의 문장을 읽고 각자 경험을 연결해 이야기했어요. 말하고 싶지 않은 부분은 건너뛸 수 있어 부담 없었고 진행자가 대화 범위를 잘 잡아줬습니다.", helpful: 8, meetingName: "마음 치유 그림책", meetingWhen: "2026.08.29 14:00", meetingWhere: "서대문구 모임공간", meetingCount: "8명 참여" },
      { author: "익명 63", date: "2026.08.12", body: "주제가 미리 공지돼 제 상황에 맞는 회차를 골라 참여할 수 있었어요. 정해진 활동과 나눔 시간 안에서 차분하게 진행됐습니다.", helpful: 4, meetingName: "8월 성장 독서", meetingWhen: "2026.08.09 14:00", meetingWhere: "서대문구 모임공간", meetingCount: "7명 참여" },
    ],
  },
  "4cd18c1a-e2e9-11ef-843c-0a7994fa3be51": {
    variant: "control",
    reviews: [
      { author: "익명 19", date: "2026.08.28", body: "질문 카드에 따라 책과 자신의 경험을 연결해 이야기했어요. 진행 순서가 분명하고 새로 온 사람도 같은 횟수로 발언해 편하게 참여했습니다.", helpful: 6, meetingName: "8월 골디락스 북클럽", meetingWhen: "2026.08.27 19:30", meetingWhere: "강남구 카페", meetingCount: "10명 참여" },
      { author: "익명 46", date: "2026.08.10", body: "책뿐 아니라 짧은 영상도 함께 보고 주제를 넓혀가는 방식이 신선했어요. 준비물과 종료 시간이 공지대로여서 다음에도 참여하기 좋을 것 같습니다.", helpful: 7, meetingName: "일요일 콘텐츠 모임", meetingWhen: "2026.08.09 15:00", meetingWhere: "강남구 카페", meetingCount: "9명 참여" },
    ],
  },
};
