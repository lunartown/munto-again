import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: { default: "Somoim Design System", template: "%s · Somoim Design System" },
  description: "소모임 후기 경험에 실제로 사용된 토큰과 컴포넌트를 정리하는 디자인 시스템 문서입니다.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="ko"><body>{children}</body></html>;
}
