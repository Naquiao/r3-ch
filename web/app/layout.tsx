import "./globals.css";

import type { Metadata } from "next";
import { Figtree, Geist_Mono } from "next/font/google";
import type { ReactElement, ReactNode } from "react";

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
        <main>{children}</main>
      </body>
    </html>
  );
}
