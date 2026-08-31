import Link from "next/link";
import { SiteShell } from "./site-shell";

const sections = [
  { href: "/foundations", label: "Foundations", children: ["Color", "Typography", "Spacing & radius", "Icons"] },
  { href: "/components", label: "Components", children: ["Core", "Supporting", "Usage map"] },
  { href: "/roadmap", label: "Roadmap", children: ["Principles", "Phases", "Triggers"] },
];

export function DocsLayout({ children, toc }: { children: React.ReactNode; toc?: { href: string; label: string }[] }) {
  return (
    <SiteShell>
      <div className="docs-frame">
        <aside className="docs-sidebar" aria-label="문서 메뉴">
          <Link className="sidebar-overview" href="/">Overview</Link>
          {sections.map((section) => <div className="sidebar-group" key={section.label}><Link href={section.href}>{section.label}</Link>{section.children.map((item) => <span key={item}>{item}</span>)}</div>)}
        </aside>
        <main className="docs-main">{children}</main>
        {toc && <aside className="docs-toc" aria-label="페이지 목차"><strong>On this page</strong>{toc.map((item) => <a href={item.href} key={item.href}>{item.label}</a>)}</aside>}
      </div>
    </SiteShell>
  );
}

export function PageIntro({ eyebrow, title, description }: { eyebrow: string; title: string; description: string }) {
  return <header className="page-intro"><p className="eyebrow">{eyebrow}</p><h1>{title}</h1><p>{description}</p></header>;
}

export function StatusBadge({ kind, children }: { kind: "verified" | "chosen" | "pending"; children: React.ReactNode }) {
  return <span className={`status-badge status-${kind}`}><i />{children}</span>;
}
