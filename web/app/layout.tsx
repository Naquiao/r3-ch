import "./globals.css";

import type { Metadata } from "next";
import { Figtree, Geist_Mono } from "next/font/google";
import type { ReactElement, ReactNode } from "react";
import { SidebarNav } from "@/components/sidebar-nav";

const geistMono = Geist_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
});

const figtree = Figtree({
  subsets: ["latin"],
  variable: "--font-sans",
});

export const metadata: Metadata = {
  title: "BUGSTER // Opportunity Review",
  description: "No config, no test files, no babysitting. Autonomous QA agent pipeline.",
};

export default function RootLayout({ children }: { children: ReactNode }): ReactElement {
  return (
    <html lang="en" className={`${geistMono.variable} ${figtree.variable}`}>
      <body>
        <div className="window-shell">
          <div className="window-chrome">
            <div className="window-dots" aria-hidden="true">
              <span className="dot close"></span>
              <span className="dot min"></span>
              <span className="dot max"></span>
            </div>
            <span className="window-title">BUGSTER // Career Pipeline</span>
          </div>
          <div className="app-layout">
            <SidebarNav />
            <main className="app-main">{children}</main>
          </div>
        </div>
      </body>
    </html>
  );
}
