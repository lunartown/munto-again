import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: { default: "Somoim Design System", template: "%s · Somoim Design System" },
  description: "소모임의 탐색, 후기 작성과 조회 경험을 위한 디자인 원칙과 컴포넌트 가이드입니다.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="ko"><body>{children}</body></html>;
}
