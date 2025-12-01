import "../styles/globals.css";
import type { Metadata } from "next";
import { Space_Grotesk } from "next/font/google";

const spaceGrotesk = Space_Grotesk({ subsets: ["latin"], variable: "--font-space" });

export const metadata: Metadata = {
  title: "Investia | AI-Powered Trading Copilot",
  description: "Simulated trading insights with chat explanations and broker connectivity.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={spaceGrotesk.variable}>
      <body className="bg-[var(--background)] text-slate-100">{children}</body>
    </html>
  );
}
