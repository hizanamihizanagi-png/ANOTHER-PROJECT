import type { Metadata } from "next";
import "./globals.css";
import Link from "next/link";
import { SessionProvider } from "@/lib/session";

export const metadata: Metadata = {
  title: "ScorAI — Épargne Sportive & Crédit Intelligent",
  description: "Transforme ta passion sportive en épargne intelligente.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr">
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
        <meta name="theme-color" content="#f8fafc" />
      </head>
      <body>
        <div className="bg-grid" />
        <SessionProvider>
          {children}
        </SessionProvider>

        {/* Bottom Navigation */}
        <nav className="bottom-nav">
          <Link href="/dashboard">
            <span className="icon">🏠</span>
            Accueil
          </Link>
          <Link href="/triggers">
            <span className="icon">⚡️</span>
            Triggers
          </Link>
          <Link href="/credit">
            <span className="icon">💳</span>
            Crédit
          </Link>
          <Link href="/leaderboard">
            <span className="icon">🏆</span>
            Classement
          </Link>
        </nav>
      </body>
    </html>
  );
}
