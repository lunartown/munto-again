import Link from "next/link";
import { ThemeToggle } from "./system-components";

export function SiteShell({ children }: { children: React.ReactNode }) {
  return (
    <div className="site-shell">
      <header className="site-header">
        <Link className="brand" href="/" aria-label="Somoim Design System 홈">
          <span className="brand-mark" aria-hidden="true"><i /><i /><i /></span>
          <span>Somoim <b>DS</b></span>
        </Link>
        <nav aria-label="주요 메뉴">
          <Link href="/foundations">Foundations</Link>
          <Link href="/components">Components</Link>
          <Link href="/roadmap">Roadmap</Link>
        </nav>
        <ThemeToggle />
      </header>
      {children}
      <footer className="site-footer"><span>Somoim Design System</span><span>Mobile community patterns · 2026</span></footer>
    </div>
  );
}
