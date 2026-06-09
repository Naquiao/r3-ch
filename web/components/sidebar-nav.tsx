"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ReactElement } from "react";

type NavItem = {
  href: string;
  label: string;
  hint: string;
};

const NAV_ITEMS: NavItem[] = [
  { href: "/review", label: "Review", hint: "Top funnel" },
  { href: "/pipeline", label: "Pipeline", hint: "Bottom funnel" },
];

function isActivePath(pathname: string, href: string): boolean {
  return pathname === href || pathname.startsWith(`${href}/`);
}

export function SidebarNav(): ReactElement {
  const pathname = usePathname();

  return (
    <aside className="sidebar-nav" aria-label="Sections">
      <div className="sidebar-nav-header">
        <span className="eyebrow">Navigation</span>
        <h2 className="sidebar-nav-title">Funnel Sections</h2>
      </div>
      <nav className="sidebar-nav-links">
        {NAV_ITEMS.map((item) => {
          const active = isActivePath(pathname, item.href);
          return (
            <Link
              key={item.href}
              href={item.href}
              className={`sidebar-nav-link ${active ? "active" : ""}`}
            >
              <span className="sidebar-nav-link-label">{item.label}</span>
              <span className="sidebar-nav-link-hint">{item.hint}</span>
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
